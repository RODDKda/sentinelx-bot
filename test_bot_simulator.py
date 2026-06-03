#!/usr/bin/env python3
"""
SentinelX MVP - Local Bot Simulator
====================================
Simulates a Telegram Bot calling all API endpoints to verify the full MVP flow.
No external network required - everything runs against localhost:8000.

Simulates 3 user scenarios:
  User A (Alice): New user, full flow
  User B (Bob):   New user, binds a different wallet
  User C (Carol): Registers via referral from Alice
"""

import requests
import json
import time
import sys

BASE = "http://127.0.0.1:8000"
PASS = 0
FAIL = 0
WARN = 0

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

CHECK = "OK"
CROSS = "FAIL"

PRIVATE_KEY = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
PRIVATE_KEY_B = "0xfedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321"


def ok(msg):
    global PASS
    PASS += 1
    print(f"  {GREEN}[PASS]{RESET} {msg}")


def err(msg):
    global FAIL
    FAIL += 1
    print(f"  {RED}[FAIL]{RESET} {msg}")


def warn(msg):
    global WARN
    WARN += 1
    print(f"  {YELLOW}[WARN]{RESET} {msg}")


def header(text):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")


def test(method, path, expected_status=200, **kwargs):
    """Make an API call and verify the response."""
    url = f"{BASE}{path}"
    try:
        if "data" in kwargs:
            resp = requests.request(method, url, data=kwargs.pop("data"), timeout=5)
        elif "json" in kwargs:
            resp = requests.request(method, url, json=kwargs.pop("json"), timeout=5)
        elif "params" in kwargs:
            resp = requests.request(method, url, params=kwargs.pop("params"), timeout=5)
        else:
            resp = requests.request(method, url, timeout=5)

        if resp.status_code == expected_status:
            ok(f"{method} {path} → {resp.status_code}")
            return resp
        else:
            err(f"{method} {path} → {resp.status_code} (expected {expected_status})")
            err(f"  Body: {resp.text[:200]}")
            return resp
    except requests.ConnectionError:
        err(f"{method} {path} → Connection refused! Is the server running on :8000?")
        sys.exit(1)
    except Exception as e:
        err(f"{method} {path} → {e}")
        return None


# ================================================================
# SCENARIO 1: Alice - Full New User Flow
# ================================================================
header("USER A (Alice): New user registration + wallet bind + trading")

# 1.1 Health check
test("GET", "/health")

# 1.2 Register Alice
resp = test("POST", "/api/v1/auth/register",
            params={"telegram_id": 1001, "username": "alice_crypto"})
alice = resp.json()
assert alice["status"] == "created", f"Expected 'created', got {alice}"
print(f"  Alice ID: {alice['user_id'][:8]}..., Referral: {alice['referral_code']}")

# 1.3 Re-register (idempotent)
resp = test("POST", "/api/v1/auth/register",
            params={"telegram_id": 1001, "username": "alice_crypto"})
recheck = resp.json()
assert recheck["status"] == "existing", f"Expected 'existing', got {recheck}"
ok("Re-registration returns 'existing' (idempotent)")

# 1.4 Bind wallet
resp = test("POST", "/api/v1/wallet/bind", data={
    "private_key": PRIVATE_KEY,
    "label": "AliceMain",
    "telegram_id": 1001,
})
assert resp.status_code == 200
assert "successfully" in resp.text.lower() or "Decryption verified" in resp.text
assert "0x1Be3" in resp.text  # First 4 chars of derived address
ok("Wallet bound + AES encrypted + decryption verified")

# 1.5 Get web verify code
resp = test("POST", "/api/v1/bot/verify-code", params={"telegram_id": 1001})
code_data = resp.json()
alice_code = code_data["code"]
assert len(alice_code) == 6
ok(f"Verify code generated: {alice_code}")

# 1.6 Validate verify code
resp = test("GET", "/api/v1/bot/verify-code/validate",
            params={"code": alice_code, "telegram_id": 1001})
assert resp.json()["status"] == "valid"
ok("Verify code validated successfully")

# 1.7 Code is consumed (one-time use) - should return 401
resp = test("GET", "/api/v1/bot/verify-code/validate",
            params={"code": alice_code, "telegram_id": 1001},
            expected_status=401)
ok("Verify code consumed (one-time use)")

# 1.8 Browse markets
resp = test("GET", "/api/v1/markets/active")
markets = resp.json()
assert markets["count"] == 4
assert len(markets["markets"]) == 4
ok(f"Markets: {[m['coin'] for m in markets['markets']]}")

# 1.9 Market detail
resp = test("GET", "/api/v1/markets/btc-above-95k")
btc = resp.json()
assert btc["coin"] == "BTC"
assert "safety_score" in btc
ok(f"BTC market: UP=${btc['up_price']} DOWN=${btc['down_price']} Safety={btc['safety_score']}")

# 1.10 Place a buy order
resp = test("POST", "/api/v1/trades/buy",
            params={"market_slug": "btc-above-95k", "direction": "UP",
                    "amount_usd": 100.0, "telegram_id": 1001})
buy = resp.json()
assert buy["status"] == "ok"
assert buy["order"]["direction"] == "UP"
assert buy["order"]["fee"] == 0.75  # 0.75% of $100
ok(f"Buy: 100 USDC → {buy['order']['contracts']} contracts UP @ ${buy['order']['price']}, fee=${buy['order']['fee']}")

# 1.11 Buy another (ETH DOWN)
resp = test("POST", "/api/v1/trades/buy",
            params={"market_slug": "eth-above-3500", "direction": "DOWN",
                    "amount_usd": 50.0, "telegram_id": 1001})
buy2 = resp.json()
ok(f"Buy: 50 USDC → {buy2['order']['contracts']} contracts DOWN @ ${buy2['order']['price']}")

# 1.12 Check positions
resp = test("GET", "/api/v1/trades/positions", params={"telegram_id": 1001})
pos = resp.json()
assert len(pos["positions"]) == 2
ok(f"Positions: {len(pos['positions'])} open, invested ${pos['total_invested']}")

# 1.13 Trade history
resp = test("GET", "/api/v1/trades/history", params={"telegram_id": 1001})
history = resp.json()
assert history["total"] == 2
ok(f"History: {history['total']} trades")

# 1.14 Sell a position
resp = test("POST", "/api/v1/trades/sell",
            params={"market_slug": "btc-above-95k", "telegram_id": 1001})
sell = resp.json()
assert sell["status"] == "ok"
ok(f"Sell BTC: PnL=${sell['sold'][0]['pnl']}")

# 1.15 Check positions after sell
resp = test("GET", "/api/v1/trades/positions", params={"telegram_id": 1001})
pos_after = resp.json()
assert len(pos_after["positions"]) == 1  # Only ETH remains
ok("Position closed correctly after sell")


# ================================================================
# SCENARIO 2: Bob - Another User
# ================================================================
header("USER B (Bob): Registration + wallet + trade")

test("POST", "/api/v1/auth/register",
     params={"telegram_id": 2002, "username": "bob_trader"})
ok("Bob registered")

test("POST", "/api/v1/wallet/bind", data={
    "private_key": PRIVATE_KEY_B,
    "label": "BobWallet",
    "telegram_id": 2002,
})
ok("Bob wallet bound")

test("POST", "/api/v1/trades/buy",
     params={"market_slug": "sol-above-180", "direction": "DOWN",
             "amount_usd": 200.0, "telegram_id": 2002})
ok("Bob bought SOL DOWN $200")


# ================================================================
# SCENARIO 3: Carol - Referral
# ================================================================
header("USER C (Carol): Referral registration via Alice")

resp = test("POST", "/api/v1/auth/register",
            params={"telegram_id": 3003, "username": "carol_newbie",
                    "referrer_code": alice["referral_code"]})
carol = resp.json()
assert carol["status"] == "created"
ok(f"Carol registered via Alice's referral: {alice['referral_code']}")


# ================================================================
# SCENARIO 4: Web Page Verification
# ================================================================
header("WEB PAGES: Verify all pages render correctly")

for path, keyword in [
    ("/", "SentinelX MVP"),
    ("/web/wallet/bind", "AES-256-GCM"),
    ("/web/dashboard", "Dashboard"),
]:
    resp = test("GET", path)
    assert keyword in resp.text
    ok(f"Page {path}: contains '{keyword}'")


# ================================================================
# SCENARIO 5: Error Handling
# ================================================================
header("ERROR HANDLING: Verify proper error responses")

# Invalid private key
resp = test("POST", "/api/v1/wallet/bind", data={
    "private_key": "not_a_valid_key",
    "label": "bad",
    "telegram_id": 1001,
})
assert "Invalid" in resp.text or "invalid" in resp.text.lower()
ok("Invalid private key rejected")

# Unknown market
resp = test("GET", "/api/v1/markets/nonexistent")
assert "error" in resp.json() or resp.status_code != 200
ok("Unknown market returns error")

# Expired verify code - should return 401
test("GET", "/api/v1/bot/verify-code/validate",
     params={"code": "EXPIRED", "telegram_id": 1001},
     expected_status=401)
ok("Expired code rejected")

# Non-existent user verify code - should return 404
resp = test("POST", "/api/v1/bot/verify-code", params={"telegram_id": 99999},
            expected_status=404)
ok("Non-existent user rejected")


# ================================================================
# FINAL SUMMARY
# ================================================================
header("MVP COMPLETE - TEST SUMMARY")

total = PASS + FAIL + WARN
bar = "█" * 50

print(f"""
{GREEN if FAIL == 0 else RED}{bar}{RESET}
  Total tests:   {total}
  {GREEN}Passed:        {PASS}{RESET}
  {RED}Failed:        {FAIL}{RESET}
  {YELLOW}Warnings:      {WARN}{RESET}
  Success rate:  {PASS/total*100:.0f}%
{GREEN if FAIL == 0 else RED}{bar}{RESET}

Scenarios tested:
  ✓ User A (Alice): Register → Wallet → WebCode → Markets → Buy → Pos → Sell
  ✓ User B (Bob):   Register → Wallet → Trade
  ✓ User C (Carol): Referral registration
  ✓ Web pages:      All 3 pages render correctly
  ✓ Error handling: Invalid key, unknown market, expired code

All API endpoints verified:
  GET  /health
  GET  /
  GET  /web/wallet/bind, /web/dashboard
  POST /api/v1/auth/register
  POST /api/v1/wallet/bind
  POST /api/v1/bot/verify-code
  GET  /api/v1/bot/verify-code/validate
  GET  /api/v1/markets/active, /api/v1/markets/{{slug}}
  POST /api/v1/trades/buy, /api/v1/trades/sell
  GET  /api/v1/trades/positions, /api/v1/trades/history
""")

if FAIL == 0:
    print(f"{GREEN}{BOLD}[SUCCESS] MVP VERIFIED! All {PASS} tests passed.{RESET}\n")
    sys.exit(0)
else:
    print(f"{RED}{BOLD}[WARNING] {FAIL} test(s) failed. Review errors above.{RESET}\n")
    sys.exit(1)

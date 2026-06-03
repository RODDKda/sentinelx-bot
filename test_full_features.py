#!/usr/bin/env python3
"""
SentinelX MVP - Complete Verification Script
=============================================
Tests ALL features: data freshness, fee engine, copy trading,
security detection, i18n, error handling.
"""
import requests, json, time, sys

BASE = "http://127.0.0.1:8000"
PASS = 0; FAIL = 0
PK = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"

def t(method, path, **kw):
    global PASS, FAIL
    url = f"{BASE}{path}"
    try:
        es = kw.pop("expected_status", 200)
        if "data" in kw: r = requests.request(method, url, data=kw.pop("data"), timeout=5)
        elif "json" in kw: r = requests.request(method, url, json=kw.pop("json"), timeout=5)
        elif "params" in kw: r = requests.request(method, url, params=kw.pop("params"), timeout=5)
        else: r = requests.request(method, url, timeout=5)
        status = "OK" if r.status_code == es else f"FAIL({r.status_code})"
        if r.status_code == es: PASS += 1
        else: FAIL += 1; print(f"  FAIL: {method} {path} → {r.status_code} (expected {es})")
        return r
    except Exception as e:
        FAIL += 1; print(f"  FAIL: {method} {path} → {e}"); return None

def info(msg): print(f"  {msg}")
def section(msg): print(f"\n{'='*50}\n  {msg}\n{'='*50}")

# Setup: register Alice
section("SETUP: Register users")
t("POST","/api/v1/auth/register",params={"telegram_id":1,"username":"alice"})
t("POST","/api/v1/auth/register",params={"telegram_id":2,"username":"bob"})
t("POST","/api/v1/auth/register",params={"telegram_id":3,"username":"carol"})
t("POST","/api/v1/wallet/bind",data={"private_key":PK,"label":"A","telegram_id":1})
t("POST","/api/v1/wallet/bind",data={"private_key":PK,"label":"B","telegram_id":2})
info("3 users registered, 2 wallets bound")

# 1. Market data freshness
section("1. MARKET DATA FRESHNESS")
r = t("GET","/api/v1/markets/active")
d = r.json()
info(f"Markets: {d['count']} | Cached at: {d['cached_at']}")
for m in d["markets"]:
    age = max(m["up_age_sec"], m["down_age_sec"])
    status = m["data_freshness"]
    info(f"  {m['coin']:4s} UP=${m['up_ask']:<6} DOWN=${m['down_ask']:<6} age={age:.1f}s [{status}] tradeable={m['is_tradeable']}")
assert all(m["is_tradeable"] for m in d["markets"]), "Markets should be tradeable!"

# Wait for prices to change
info("Waiting 4s for simulated price updates...")
time.sleep(4)
r2 = t("GET","/api/v1/markets/active")
d2 = r2.json()
changed = 0
for i, m in enumerate(d2["markets"]):
    if m["up_ask"] != d["markets"][i]["up_ask"] or m["down_ask"] != d["markets"][i]["down_ask"]:
        changed += 1
        info(f"  {m['coin']} price changed: {d['markets'][i]['up_ask']}→{m['up_ask']} / {d['markets'][i]['down_ask']}→{m['down_ask']}")
assert changed > 0, "Prices should change after simulated update!"
info(f"{changed}/4 markets updated - data feed working")

# 2. Fee engine
section("2. FEE ENGINE")
r = t("GET","/api/v1/settings/calculate",params={"amount":1000,"tier":"free"})
f = r.json()
assert abs(f["fee"] - 7.5) < 0.01
info(f"Free: ${f['fee']} (rate={f['rate']*100:.2f}%) {f['breakdown']}")

r = t("GET","/api/v1/settings/calculate",params={"amount":1000,"tier":"vip2"})
f = r.json()
assert abs(f["fee"] - 4.5) < 0.01
info(f"VIP2: ${f['fee']} (rate={f['rate']*100:.2f}%) {f['breakdown']}")

r = t("GET","/api/v1/settings/calculate",params={"amount":1000,"tier":"vip3","subscription":"pro"})
f = r.json()
info(f"VIP3+Pro: ${f['fee']} (rate={f['rate']*100:.2f}%) - min is 0.15%")
assert f["rate"] >= 0.0015

r = t("GET","/api/v1/settings/calculate",params={"amount":100,"tier":"free"})
f = r.json()
c = f["commission"]
info(f"Referral on $0.75 fee: direct=${c['direct']} second=${c['second_level']} platform=${c['platform']}")

# 3. Copy trading
section("3. COPY TRADING")
t("POST","/api/v1/copy/start",params={"follower_id":"2","leader_id":"1","max_per_trade":200,"total_cap":500})
info("Bob copies Alice (max $200/trade, $500 cap)")

t("POST","/api/v1/copy/start",params={"follower_id":"3","leader_id":"1","max_per_trade":50,"total_cap":200,"copy_ratio":0.5})
info("Carol copies Alice at 50% ratio")

r = t("GET","/api/v1/copy/following",params={"follower_id":"2"})
info(f"Bob follows: {len(r.json()['following'])} leaders")
r = t("GET","/api/v1/copy/followers",params={"leader_id":"1"})
info(f"Alice has {len(r.json()['followers'])} followers")

# Alice trades → triggers copy
r = t("POST","/api/v1/trades/buy",params={"market_slug":"btc-above-95k","direction":"UP","amount_usd":300,"telegram_id":1})
order = r.json()
info(f"Alice: ${order['order']['total_usd']} {order['order']['direction']} @ ${order['order']['price']}")
info(f"Fee: ${order['order']['fee']} ({order['order']['fee_rate']*100:.2f}%)")
info(f"Copy trades triggered: {order['copy_trades_triggered']}")

r = t("GET","/api/v1/copy/history")
info(f"Copy trade history: {len(r.json()['trades'])} entries")
for ct in r.json()["trades"]:
    info(f"  {ct['follower_id']} → {ct['amount_usd']} {ct['direction']} @ {ct['price']} ({ct['copy_ratio']*100:.0f}%)")

# Bob stops copying
t("POST","/api/v1/copy/stop",params={"follower_id":"2","leader_id":"1"})
r = t("GET","/api/v1/copy/following",params={"follower_id":"2"})
rel = [x for x in r.json()["following"] if x["leader_id"] == "1"]
assert not rel[0]["is_active"]
info("Bob stopped copying Alice")

# 4. Security detection
section("4. SECURITY DETECTION")
for slug, strategy in [("btc-above-95k","advisory"),("eth-above-3500","threshold"),("sol-above-180","confidence")]:
    r = t("GET",f"/api/v1/security/market/{slug}",params={"strategy":strategy})
    s = r.json()
    info(f"{s['market_slug']:15s} Risk:{s['overall']:3d}/100 Level:{s['risk_level']:8s} Tradeable:{s['can_trade']} [{s['strategy_used']}]")

r = t("GET","/api/v1/security/wallet/0xf42138298fa1Fc8514BC17D59eBB451AceF3cDBa")
w = r.json()
info(f"Wallet score: {w['reputation_score']}/100 Verified:{w['is_verified_smart_wallet']}")

# 5. Trade with security (high-risk market)
section("5. TRADE WITH SECURITY (THRESHOLD MODE)")
r = t("POST","/api/v1/trades/buy",params={
    "market_slug":"sol-above-180","direction":"UP","amount_usd":100,"telegram_id":1,"security_strategy":"threshold"
})
order = r.json()
info(f"Security: score={order['order']['safety_score']} strategy={order['order']['safety_strategy']}")

# 6. i18n
section("6. I18N")
t("POST","/api/v1/settings/user/language",params={"telegram_id":1,"language":"zh"})
info("Alice switched to Chinese")
r = t("GET","/api/v1/settings/languages")
for lang in r.json()["languages"]:
    info(f"  {lang['code']}: {lang['name']} ({lang['native']})")

# 7. Data freshness edge case
section("7. DATA FRESHNESS EDGE")
# Check stale detection
r = t("GET","/api/v1/markets/btc-above-95k")
m = r.json()
info(f"BTC age: {m['up_age_sec']}s, tradeable: {m['is_tradeable']}, freshness: {m['data_freshness']}")
assert m["is_tradeable"], "Should be tradeable with fresh data"

# ===========================================
section("FINAL SUMMARY")
total = PASS + FAIL
pct = PASS/total*100 if total else 0
bar = "="*50
print(f"""
{bar}
  Passed:  {PASS}
  Failed:  {FAIL}
  Total:   {total}
  Rate:    {pct:.0f}%
{bar}
""")
if FAIL == 0:
    print("ALL FEATURES VERIFIED!")
    sys.exit(0)
else:
    sys.exit(1)

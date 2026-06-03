/** API service for calling the SentinelX backend */

import type { UserData, MarketInfo, SecurityScore } from "../types";

const API_BASE = process.env.API_BASE_URL || "http://localhost:8000";

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text.slice(0, 200)}`);
  }
  return res.json();
}

/** Register a new user via Telegram ID */
export async function registerUser(
  telegramId: number,
  username?: string
): Promise<UserData> {
  const params = new URLSearchParams({ telegram_id: String(telegramId) });
  if (username) params.set("username", username);
  return fetchAPI<UserData>(`/api/v1/auth/register?${params}`, {
    method: "POST",
  });
}

/** Get active markets (mock for now, returns sample data) */
export async function getActiveMarkets(): Promise<MarketInfo[]> {
  try {
    return await fetchAPI<MarketInfo[]>("/api/v1/markets/active");
  } catch {
    // Return mock data if backend is not available
    return [
      {
        slug: "btc-above-95k",
        title: "BTC above $95k at close?",
        coin: "BTC",
        up_price: 0.62,
        down_price: 0.40,
        volume: 1250000,
        ends_in_seconds: 480,
      },
      {
        slug: "eth-above-3500",
        title: "ETH above $3,500?",
        coin: "ETH",
        up_price: 0.55,
        down_price: 0.47,
        volume: 890000,
        ends_in_seconds: 720,
      },
      {
        slug: "sol-above-180",
        title: "SOL above $180?",
        coin: "SOL",
        up_price: 0.48,
        down_price: 0.54,
        volume: 450000,
        ends_in_seconds: 360,
      },
    ];
  }
}

/** Generate a web login link with one-time code */
export async function generateWebCode(
  telegramId: number
): Promise<{ code: string; expires_in: number }> {
  try {
    return await fetchAPI<{ code: string; expires_in: number }>(
      `/api/v1/bot/verify-code?telegram_id=${telegramId}`,
      { method: "POST" }
    );
  } catch {
    // Mock: generate a random code locally
    const code = Math.random().toString(36).substring(2, 8).toUpperCase();
    return { code, expires_in: 300 };
  }
}

/** Get security score for a market */
export async function getSecurityScore(
  slug: string
): Promise<SecurityScore | null> {
  try {
    return await fetchAPI<SecurityScore>(`/api/v1/security/market/${slug}`);
  } catch {
    return null;
  }
}

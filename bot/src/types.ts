/** Shared types for the SentinelX Bot */

export interface UserData {
  user_id: string;
  telegram_id: number;
  username: string | null;
  referral_code: string;
  tier: string;
  language: string;
}

export interface WalletInfo {
  wallet_address: string;
  label: string;
  usdc_balance: number;
  matic_balance: number;
}

export interface MarketInfo {
  slug: string;
  title: string;
  coin: string;
  up_price: number;
  down_price: number;
  volume: number;
  ends_in_seconds: number;
}

export interface SecurityScore {
  overall: number;
  manipulation: number;
  reputation: number;
}

export interface BotSession {
  userId?: string;
  language?: string;
  step?: string;
  tempData?: Record<string, unknown>;
}

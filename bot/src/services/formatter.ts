/** Message formatting utilities */

import type { MarketInfo } from "../types";

/** Format market list for Telegram */
export function formatMarketList(markets: MarketInfo[]): string {
  if (markets.length === 0) return "No active markets found.";

  const lines = ["\u{1F4CA} *Active Markets*\n"];

  for (const m of markets) {
    const mins = Math.floor(m.ends_in_seconds / 60);
    const secs = m.ends_in_seconds % 60;
    const timeStr = `${mins}m ${secs}s`;
    const spread = (m.up_price + m.down_price).toFixed(2);

    lines.push(
      `*${m.title}*`,
      `  \u{1F4C8} UP: $${m.up_price.toFixed(2)} | \u{1F4C9} DOWN: $${m.down_price.toFixed(2)}`,
      `  Vol: $${(m.volume / 1000).toFixed(0)}K | Ends: ${timeStr}`,
      `  \`/buy ${m.slug} <UP/DOWN> <amount>\``,
      ""
    );
  }

  return lines.join("\n");
}

/** Format welcome message */
export function formatWelcome(
  username: string | undefined,
  language: string
): string {
  const name = username ? `@${username}` : "there";

  return [
    `\u{1F6E1}\u{FE0F} *Welcome to SentinelX, ${name}!*`,
    "",
    "Security-enhanced Polymarket trading bot.",
    "",
    "\u{1F4CB} *Commands:*",
    "/markets \u2014 Browse active markets",
    "/web \u2014 Get your dashboard link",
    "/help \u2014 Show all commands",
    "",
    "\u{1F510} *Your keys, your control.* All private keys are encrypted with AES-256-GCM. Never stored in plain text.",
  ].join("\n");
}

/** Format help message */
export function formatHelp(): string {
  return [
    "\u{1F6E1}\u{FE0F} *SentinelX Commands*",
    "",
    "*Market:*",
    "/markets \u2014 Browse active Polymarket markets",
    "/market \\<slug\\> \u2014 Market details + safety score",
    "",
    "*Trading:*",
    "/buy \\<slug\\> \\<UP/DOWN\\> \\<amount\\> \u2014 Place an order",
    "/sell \\<slug\\> \u2014 Sell your position",
    "/positions \u2014 View your open positions",
    "/pnl \u2014 Profit & Loss summary",
    "",
    "*Copy Trading:*",
    "/copy \\<user\\_id\\> \u2014 Start copying a trader",
    "/copylist \u2014 View your copy relationships",
    "/copystop \\<user\\_id\\> \u2014 Stop copying",
    "",
    "*Security:*",
    "/safety \\<slug\\> \u2014 Market safety score",
    "/verify \\<wallet\\> \u2014 Wallet reputation check",
    "",
    "*Account:*",
    "/web \u2014 Get your web dashboard link",
    "/settings \u2014 Language & notification settings",
    "/stop \u2014 Emergency stop (with confirmation)",
    "",
    "\u{1F4B0} Fee: 0.75% \u2022 Referral: 25% + 10%",
  ].join("\n");
}

/** Format web link message */
export function formatWebLink(
  code: string,
  telegramId: number,
  webUrl: string
): string {
  const link = `${webUrl}/web/dashboard?code=${code}&tg_id=${telegramId}`;
  return [
    "\u{1F517} *Your Dashboard*",
    "",
    `[Open Dashboard](${link})`,
    "",
    `Code: \`${code}\``,
    "_This link expires in 5 minutes._",
    "",
    "The dashboard lets you:",
    "\u2022 Bind your wallet private key",
    "\u2022 View your trading stats",
    "\u2022 Manage API keys",
  ].join("\n");
}

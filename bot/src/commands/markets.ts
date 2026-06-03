/** /markets command handler */

import type { Context } from "grammy";
import { getActiveMarkets } from "../services/api";
import { formatMarketList } from "../services/formatter";

export async function handleMarkets(ctx: Context) {
  try {
    const markets = await getActiveMarkets();
    const msg = formatMarketList(markets);
    await ctx.reply(msg, { parse_mode: "Markdown" });
  } catch (err) {
    await ctx.reply(
      "\u26A0\uFE0F Unable to fetch markets. The trading engine may be offline.",
    );
  }
}

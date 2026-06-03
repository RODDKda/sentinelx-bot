/** /web command handler - generates one-time dashboard link */

import type { Context } from "grammy";
import { generateWebCode } from "../services/api";
import { formatWebLink } from "../services/formatter";

const WEB_URL = process.env.WEB_APP_URL || "http://localhost:8000";

export async function handleWeb(ctx: Context) {
  const telegramId = ctx.from?.id;
  if (!telegramId) {
    await ctx.reply("Unable to identify your account.");
    return;
  }

  try {
    const { code } = await generateWebCode(telegramId);
    const msg = formatWebLink(code, telegramId, WEB_URL);
    await ctx.reply(msg, {
      parse_mode: "Markdown",
      disable_web_page_preview: false,
    });
  } catch (err) {
    await ctx.reply(
      "\u26A0\uFE0F Unable to generate dashboard link. Please try again later.",
    );
  }
}

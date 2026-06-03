/** /start command handler */

import type { Context } from "grammy";
import { registerUser } from "../services/api";
import { formatWelcome } from "../services/formatter";

export async function handleStart(ctx: Context) {
  const telegramId = ctx.from?.id;
  const username = ctx.from?.username;

  if (!telegramId) {
    await ctx.reply("Unable to identify your Telegram account.");
    return;
  }

  // Register user with backend
  try {
    const user = await registerUser(telegramId, username);
    await ctx.reply(formatWelcome(username, user.language), {
      parse_mode: "Markdown",
      reply_markup: {
        inline_keyboard: [
          [
            { text: "\u{1F4CA} Markets", callback_data: "cmd_markets" },
            { text: "\u{1F517} Dashboard", callback_data: "cmd_web" },
          ],
          [{ text: "\u{2753} Help", callback_data: "cmd_help" }],
        ],
      },
    });
  } catch (err) {
    // Fallback if backend is not available
    await ctx.reply(formatWelcome(username, "en"), {
      parse_mode: "Markdown",
    });
  }
}

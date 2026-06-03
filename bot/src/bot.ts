/** SentinelX Telegram Bot - Main Entry Point
 *
 * Security-Enhanced Polymarket Trading Bot
 * Uses grammY with long polling mode.
 */

import { Bot } from "grammy";
import { handleStart } from "./commands/start";
import { handleMarkets } from "./commands/markets";
import { handleWeb } from "./commands/web";
import { formatHelp } from "./services/formatter";

// --- Bot Initialization ---
const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;

if (!BOT_TOKEN) {
  console.error("ERROR: TELEGRAM_BOT_TOKEN environment variable is required.");
  console.error("Get one from @BotFather on Telegram.");
  process.exit(1);
}

const bot = new Bot(BOT_TOKEN);

// --- Error Handler ---
bot.catch((err) => {
  console.error("[Bot Error]", err.message);
});

// --- Command Handlers ---

// /start - Welcome + registration
bot.command("start", handleStart);

// /help - Show all commands
bot.command("help", async (ctx) => {
  await ctx.reply(formatHelp(), { parse_mode: "Markdown" });
});

// /markets - Active market list
bot.command("markets", handleMarkets);

// /web - Generate dashboard link
bot.command("web", handleWeb);

// /ping - Health check
bot.command("ping", async (ctx) => {
  await ctx.reply("pong \u{1F3D3}");
});

// --- Callback Handlers (inline keyboard buttons) ---
bot.callbackQuery("cmd_markets", handleMarkets);
bot.callbackQuery("cmd_web", handleWeb);
bot.callbackQuery("cmd_help", async (ctx) => {
  await ctx.reply(formatHelp(), { parse_mode: "Markdown" });
  await ctx.answerCallbackQuery();
});

// --- Fallback for unknown commands ---
bot.on("message:text", async (ctx) => {
  const text = ctx.message.text;
  if (text.startsWith("/")) {
    await ctx.reply(
      `Unknown command: \`${text}\`. Use /help to see available commands.`,
      { parse_mode: "Markdown" },
    );
  }
});

// --- Start Bot ---
console.log("[SentinelX Bot] Starting...");
console.log(`[SentinelX Bot] Token: ${BOT_TOKEN.slice(0, 6)}...${BOT_TOKEN.slice(-4)}`);

bot.start({
  onStart: (info) => {
    console.log(`[SentinelX Bot] Running as @${info.username}`);
    console.log("[SentinelX Bot] Commands: /start /help /markets /web /ping");
  },
});

// Graceful shutdown
process.once("SIGINT", () => bot.stop());
process.once("SIGTERM", () => bot.stop());

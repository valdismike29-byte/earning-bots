#!/usr/bin/env python3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import asyncio
import random

TELEGRAM_TOKEN = "8394842732:AAEmWUKgT-VzDLp8PWKY1TN3wwjlEkspmdY"

AIRDROP_PROJECTS = [
    {
        "name": "🚀 LayerZero",
        "reward": "$500-2000",
        "type": "DeFi Protocol",
        "tasks": "Bridge между сетями",
        "ref_link": "https://layerzero.network/",
        "status": "Активный"
    },
    {
        "name": "🌟 zkSync Era", 
        "reward": "$300-1500",
        "type": "Layer 2",
        "tasks": "Транзакции в сети",
        "ref_link": "https://zksync.io/",
        "status": "Активный"
    }
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎁 Активные Airdrop", callback_data="active_airdrops")],
        [InlineKeyboardButton("💰 Мой заработок", callback_data="my_earnings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎯 **AIRDROP HUNTER BOT**\n\n"
        f"💎 Добро пожаловать в мир бесплатных криптовалют!\n\n"
        f"👇 Выберите действие:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "active_airdrops":
    text = "🎁 **АКТИВНЫЕ AIRDROP:**\n\n"
    for i, project in enumerate(AIRDROP_PROJECTS, 1):
        if project['status'] == 'Активный':
            text += f"{i}. {project['name']}\n"
            text += f"💰 {project['reward']}\n"
            text += f"📋 {project['type']}\n"
            text += f"🔗 {project['ref_link']}\n\n"
    await query.edit_message_text(text, parse_mode='Markdown')
elif query.data == "my_earnings":
    text = "💰 **МОЙ ЗАРАБОТОК:**\n\n"
    text += "✅ Получено: $0\n"
    text += "⏳ Ожидает: $500-2000\n"
    text += "📊 Активных: 2 проекта\n"
    await query.edit_message_text(text, parse_mode='Markdown')

def main():
    print("🎯 Запуск Airdrop Hunter Bot...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Airdrop Hunter Bot запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()

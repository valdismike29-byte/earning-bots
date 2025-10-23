#!/usr/bin/env python3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio

# ВАЖНО! Ваш токен от BotFather
TELEGRAM_TOKEN = "7975407210:AAFRf2UeL2hxzRekrVE5jk6JmKsXPWJ33jk"
ADMIN_ID = 123456789

# База данных пользователей (в памяти)
users_db = {}

def get_user_data(user_id):
    if user_id not in users_db:
        users_db[user_id] = {
            'balance': 0.00,
            'referrals': 0,
            'tasks_completed': 0,
            'total_earned': 0.00
        }
    return users_db[user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    keyboard = [
        [InlineKeyboardButton("💰 Мой баланс", callback_data='balance')],
        [InlineKeyboardButton("📋 Задания", callback_data='tasks'), 
         InlineKeyboardButton("👥 Рефералы", callback_data='referrals')],
        [InlineKeyboardButton("💎 Вывод средств", callback_data='withdraw'),
         InlineKeyboardButton("❓ Помощь", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎉 Привет, {user_name}!\n\n"
        f"💰 Добро пожаловать в бот для заработка!\n"
        f"�� Ваш баланс: ${user_data['balance']:.2f}\n"
        f"📊 Выполнено заданий: {user_data['tasks_completed']}\n\n"
        f"🚀 Выберите действие:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = get_user_data(user_id)
    
    if query.data == 'balance':
        await show_balance(query, user_data)
    elif query.data == 'tasks':
        await show_tasks(query, user_data)
    elif query.data == 'referrals':
        await show_referrals(query, user_data)
    elif query.data == 'withdraw':
        await show_withdraw(query, user_data)
    elif query.data == 'help':
        await show_help(query)
    elif query.data.startswith('task_'):
        await complete_task(query, user_data, query.data)
    elif query.data == 'back':
        await show_main_menu(query, user_data)

async def show_balance(query, user_data):
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"💰 ВАШ БАЛАНС:\n\n"
        f"💵 Доступно: ${user_data['balance']:.2f}\n"
        f"📈 Всего заработано: ${user_data['total_earned']:.2f}\n"
        f"📋 Заданий выполнено: {user_data['tasks_completed']}\n"
        f"👥 Рефералов: {user_data['referrals']}\n\n"
        f"✅ Минимальная сумма вывода: $1.00",
        reply_markup=reply_markup
    )

async def show_tasks(query, user_data):
    keyboard = [
        [InlineKeyboardButton("📱 Подписаться на канал (+$0.10)", callback_data='task_subscribe')],
        [InlineKeyboardButton("⭐ Оценить бота (+$0.05)", callback_data='task_rate')],
        [InlineKeyboardButton("🔗 Поделиться ботом (+$0.15)", callback_data='task_share')],
        [InlineKeyboardButton("🎯 Ежедневный бонус (+$0.20)", callback_data='task_daily')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📋 ДОСТУПНЫЕ ЗАДАНИЯ:\n\n"
        f"💡 Выполняйте задания и получайте деньги!\n"
        f"💰 Ваш баланс: ${user_data['balance']:.2f}\n\n"
        f"🚀 Выберите задание:",
        reply_markup=reply_markup
    )

async def complete_task(query, user_data, task_id):
    rewards = {
        'task_subscribe': 0.10,
        'task_rate': 0.05,
        'task_share': 0.15,
        'task_daily': 0.20
    }
    
    task_names = {
        'task_subscribe': 'Подписка на канал',
        'task_rate': 'Оценка бота',
        'task_share': 'Поделиться ботом',
        'task_daily': 'Ежедневный бонус'
    }
    
    if task_id in rewards:
        reward = rewards[task_id]
        user_data['balance'] += reward
        user_data['total_earned'] += reward
        user_data['tasks_completed'] += 1
        
        keyboard = [
            [InlineKeyboardButton("📋 Еще задания", callback_data='tasks')],
            [InlineKeyboardButton("🔙 Главное меню", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ ЗАДАНИЕ ВЫПОЛНЕНО!\n\n"
            f"🎯 {task_names[task_id]}\n"
            f"💰 Получено: +${reward:.2f}\n"
            f"💵 Новый баланс: ${user_data['balance']:.2f}\n\n"
            f"🚀 Отлично! Продолжайте зарабатывать!",
            reply_markup=reply_markup
        )

async def show_referrals(query, user_data):
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"👥 РЕФЕРАЛЬНАЯ СИСТЕМА:\n\n"
        f"📊 Ваших рефералов: {user_data['referrals']}\n"
        f"💰 Заработано с рефералов: ${user_data['referrals'] * 0.50:.2f}\n\n"
        f"🔗 Ваша ссылка: https://t.me/your_bot\n\n"
        f"💡 За каждого реферала: +$0.50\n"
        f"🎯 Приглашайте друзей и зарабатывайте!",
        reply_markup=reply_markup
    )

async def show_withdraw(query, user_data):
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if user_data['balance'] >= 1.00:
        status = "✅ Доступен!"
        instruction = "💳 Свяжитесь с @admin для вывода"
    else:
        status = "❌ Недостаточно средств"
        instruction = f"�� Нужно еще: ${1.00 - user_data['balance']:.2f}"
    
    await query.edit_message_text(
        f"�� ВЫВОД СРЕДСТВ:\n\n"
        f"💵 Ваш баланс: ${user_data['balance']:.2f}\n"
        f"📊 Минимум для вывода: $1.00\n"
        f"🎯 Статус: {status}\n\n"
        f"{instruction}",
        reply_markup=reply_markup
    )

async def show_help(query):
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"❓ ПОМОЩЬ:\n\n"
        f"�� Как зарабатывать:\n"
        f"1️⃣ Выполняйте задания\n"
        f"2️⃣ Приглашайте рефералов\n"
        f"3️⃣ Получайте ежедневные бонусы\n\n"
        f"💰 Минимальный вывод: $1.00\n"
        f"📞 Поддержка: @admin",
        reply_markup=reply_markup
    )

async def show_main_menu(query, user_data):
    keyboard = [
        [InlineKeyboardButton("💰 Мой баланс", callback_data='balance')],
        [InlineKeyboardButton("📋 Задания", callback_data='tasks'), 
         InlineKeyboardButton("👥 Рефералы", callback_data='referrals')],
        [InlineKeyboardButton("💎 Вывод средств", callback_data='withdraw'),
         InlineKeyboardButton("❓ Помощь", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🏠 ГЛАВНОЕ МЕНЮ:\n\n"
        f"💵 Ваш баланс: ${user_data['balance']:.2f}\n"
        f"📊 Выполнено заданий: {user_data['tasks_completed']}\n\n"
        f"🚀 Выберите действие:",
        reply_markup=reply_markup
    )

def main():
    print("🚀 Запуск улучшенного бота...")
    print(f"🤖 Токен: {TELEGRAM_TOKEN[:10]}...")
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ Бот с кнопками запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()

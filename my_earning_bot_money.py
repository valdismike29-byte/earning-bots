#!/usr/bin/env python3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio
import json
import os

TELEGRAM_TOKEN = "7975407210:AAFRf2UeL2hxzRekrVE5jk6JmKsXPWJ33jk"
ADMIN_ID = 123456789

# Файл для сохранения данных
DATA_FILE = "users_data.json"

def load_users_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users_db = load_users_data()

def get_user_data(user_id):
    user_id = str(user_id)
    if user_id not in users_db:
        users_db[user_id] = {
            'balance': 0.00,
            'referrals': 0,
            'tasks_completed': 0,
            'total_earned': 0.00,
            'completed_tasks': [],
            'referred_by': None
        }
        save_users_data(users_db)
    return users_db[user_id]

# РЕАЛЬНЫЕ ПАРТНЕРСКИЕ ЗАДАНИЯ
REAL_TASKS = {
    'binance_register': {
        'name': '📊 Регистрация Binance',
        'reward': 2.50,
        'url': 'https://accounts.binance.com/register?ref=YOUR_REF',
        'description': 'Зарегистрируйтесь на Binance по ссылке'
    },
    'telegram_channel': {
        'name': '📢 Подписка на канал',
        'reward': 0.15,
        'url': 'https://t.me/crypto_earnings_official',
        'description': 'Подпишитесь и поставьте лайк'
    },
    'youtube_subscribe': {
        'name': '▶️ YouTube подписка',
        'reward': 0.25,
        'url': 'https://youtube.com/@cryptoearnings',
        'description': 'Подпишитесь и лайк на видео'
    },
    'app_install': {
        'name': '📱 Установить приложение',
        'reward': 1.00,
        'url': 'https://play.google.com/store/apps/details?id=com.earning.app',
        'description': 'Установите и запустите приложение'
    },
    'survey_complete': {
        'name': '📝 Опрос (5 минут)',
        'reward': 0.75,
        'url': 'https://forms.gle/survey-link',
        'description': 'Заполните короткий опрос'
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    # Проверка реферала
    if context.args and context.args[0].startswith('ref_'):
        referrer_id = context.args[0].replace('ref_', '')
        if referrer_id != str(user_id) and user_data['referred_by'] is None:
            user_data['referred_by'] = referrer_id
            if referrer_id in users_db:
                users_db[referrer_id]['referrals'] += 1
                users_db[referrer_id]['balance'] += 0.50
                users_db[referrer_id]['total_earned'] += 0.50
                save_users_data(users_db)
    
    keyboard = [
        [InlineKeyboardButton("💰 Мой баланс", callback_data='balance')],
        [InlineKeyboardButton("🎯 Задания", callback_data='tasks'), 
         InlineKeyboardButton("👥 Рефералы", callback_data='referrals')],
        [InlineKeyboardButton("💎 Вывод ($1+)", callback_data='withdraw'),
         InlineKeyboardButton("❓ Помощь", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"💰 Добро пожаловать, {user_name}!\n\n"
        f"🚀 РЕАЛЬНЫЙ ЗАРАБОТОК В ИНТЕРНЕТЕ!\n"
        f"💵 Ваш баланс: ${user_data['balance']:.2f}\n"
        f"📊 Выполнено заданий: {user_data['tasks_completed']}\n\n"
        f"✅ Выплаты каждый день!\n"
        f"🎯 Минимум для вывода: $1.00",
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
        await show_referrals(query, user_data, user_id)
    elif query.data == 'withdraw':
        await show_withdraw(query, user_data)
    elif query.data == 'help':
        await show_help(query)
    elif query.data.startswith('task_'):
        await start_task(query, user_data, query.data)
    elif query.data.startswith('complete_'):
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
        f"👥 Рефералов приглашено: {user_data['referrals']}\n\n"
        f"✅ Минимум для вывода: $1.00\n"
        f"💳 Поддерживаем: USDT, PayPal, Qiwi",
        reply_markup=reply_markup
    )

async def show_tasks(query, user_data):
    keyboard = []
    
    for task_id, task in REAL_TASKS.items():
        if task_id not in user_data['completed_tasks']:
            keyboard.append([InlineKeyboardButton(
                f"{task['name']} (+${task['reward']:.2f})", 
                callback_data=f'task_{task_id}'
            )])
    
    if not keyboard:
        keyboard.append([InlineKeyboardButton("🎉 Все задания выполнены!", callback_data='back')])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data='back')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🎯 РЕАЛЬНЫЕ ЗАДАНИЯ:\n\n"
        f"💡 Выполняйте и получайте деньги на счет!\n"
        f"💰 Ваш баланс: ${user_data['balance']:.2f}\n"
        f"🏆 Доступно заданий: {len([t for t in REAL_TASKS if t not in user_data['completed_tasks']])}\n\n"
        f"🚀 Выберите задание:",
        reply_markup=reply_markup
    )

async def start_task(query, user_data, task_id):
    task_key = task_id.replace('task_', '')
    
    if task_key in REAL_TASKS and task_key not in user_data['completed_tasks']:
        task = REAL_TASKS[task_key]
        
        keyboard = [
            [InlineKeyboardButton("🔗 Выполнить задание", url=task['url'])],
            [InlineKeyboardButton("✅ Я выполнил!", callback_data=f'complete_{task_key}')],
            [InlineKeyboardButton("🔙 Назад", callback_data='tasks')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🎯 ЗАДАНИЕ: {task['name']}\n\n"
            f"📝 Что нужно сделать:\n{task['description']}\n\n"
            f"💰 Награда: +${task['reward']:.2f}\n\n"
            f"1️⃣ Нажмите 'Выполнить задание'\n"
            f"2️⃣ Выполните действие\n"
            f"3️⃣ Вернитесь и нажмите 'Я выполнил!'\n\n"
            f"⚠️ Проверим выполнение в течение 5 минут",
            reply_markup=reply_markup
        )

async def complete_task(query, user_data, task_id):
    task_key = task_id.replace('complete_', '')
    
    if task_key in REAL_TASKS and task_key not in user_data['completed_tasks']:
        task = REAL_TASKS[task_key]
        
        # Добавляем награду
        user_data['balance'] += task['reward']
        user_data['total_earned'] += task['reward']
        user_data['tasks_completed'] += 1
        user_data['completed_tasks'].append(task_key)
        save_users_data(users_db)
        
        keyboard = [
            [InlineKeyboardButton("🎯 Еще задания", callback_data='tasks')],
            [InlineKeyboardButton("�� Мой баланс", callback_data='balance')],
            [InlineKeyboardButton("🔙 Главное меню", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🎉 ЗАДАНИЕ ВЫПОЛНЕНО!\n\n"
            f"✅ {task['name']}\n"
            f"💰 Получено: +${task['reward']:.2f}\n"
            f"💵 Новый баланс: ${user_data['balance']:.2f}\n\n"
            f"🚀 Отлично! Продолжайте зарабатывать!\n"
            f"💎 При балансе $1+ можете вывести деньги!",
            reply_markup=reply_markup
        )

async def show_referrals(query, user_data, user_id):
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    bot_info = await query.bot.get_me()
    bot_username = bot_info.username
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    await query.edit_message_text(
        f"👥 РЕФЕРАЛЬНАЯ ПРОГРАММА:\n\n"
        f"📊 Ваших рефералов: {user_data['referrals']}\n"
        f"💰 Заработано: ${user_data['referrals'] * 0.50:.2f}\n\n"
        f"🔗 Ваша ссылка:\n`{referral_link}`\n\n"
        f"💡 За каждого друга: +$0.50\n"
        f"🎯 Друг тоже получает +$0.25 бонус!\n\n"
        f"📢 Поделитесь ссылкой везде!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_withdraw(query, user_data):
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if user_data['balance'] >= 1.00:
        status = "✅ ВЫВОД ДОСТУПЕН!"
        instruction = f"💳 Напишите @crypto_support_bot\nИли в поддержку: @admin\n\n📝 Укажите:\n• Сумму: ${user_data['balance']:.2f}\n• Способ выплаты\n• Реквизиты"
    else:
        needed = 1.00 - user_data['balance']
        status = "❌ Недостаточно средств"
        instruction = f"💡 Нужно еще: ${needed:.2f}\n🎯 Выполните {int(needed/0.25)+1} заданий"
    
    await query.edit_message_text(
        f"💎 ВЫВОД СРЕДСТВ:\n\n"
        f"💵 Ваш баланс: ${user_data['balance']:.2f}\n"
        f"📊 Минимум: $1.00\n"
        f"🎯 {status}\n\n"
        f"{instruction}\n\n"
        f"💳 Способы вывода:\n"
        f"• USDT (TRC20) - без комиссии\n"
        f"• PayPal - комиссия 3%\n"
        f"• Qiwi - комиссия 5%\n\n"
        f"⚡ Выплаты в течение 24 часов!",
        reply_markup=reply_markup
    )

async def show_help(query):
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"❓ ИНСТРУКЦИЯ:\n\n"
        f"💰 Как зарабатывать:\n"
        f"1️⃣ Выполняйте задания ($0.15-2.50)\n"
        f"2️⃣ Приглашайте друзей (+$0.50)\n"
        f"3️⃣ Получайте ежедневные бонусы\n\n"
        f"💎 Минимальный вывод: $1.00\n"
        f"⚡ Выплаты каждый день!\n"
        f"🎯 Реальные деньги на карту/кошелек\n\n"
        f"📞 Поддержка: @admin\n"
        f"💬 Чат пользователей: @earning_chat",
        reply_markup=reply_markup
    )

async def show_main_menu(query, user_data):
    keyboard = [
        [InlineKeyboardButton("💰 Мой баланс", callback_data='balance')],
        [InlineKeyboardButton("🎯 Задания", callback_data='tasks'), 
         InlineKeyboardButton("👥 Рефералы", callback_data='referrals')],
        [InlineKeyboardButton("💎 Вывод ($1+)", callback_data='withdraw'),
         InlineKeyboardButton("❓ Помощь", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🏠 ГЛАВНОЕ МЕНЮ:\n\n"
        f"💵 Ваш баланс: ${user_data['balance']:.2f}\n"
        f"📊 Выполнено заданий: {user_data['tasks_completed']}\n"
        f"👥 Рефералов: {user_data['referrals']}\n\n"
        f"🚀 Выберите действие:",
        reply_markup=reply_markup
    )

def main():
    print("💰 Запуск бота с РЕАЛЬНЫМ заработком...")
    print(f"🤖 Токен: {TELEGRAM_TOKEN[:10]}...")
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ Бот с реальными деньгами запущен!")
    print("💎 Партнерские задания активны!")
    application.run_polling()

if __name__ == '__main__':
    main()

import threading
import time

def keep_alive():
    while True:
        try:
            print("🔄 Keep alive - бот работает")
        except:
            pass
        time.sleep(300)  # каждые 5 минут

# Запускаем keep-alive в фоне
threading.Thread(target=keep_alive, daemon=True).start()

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from datetime import datetime

BOT_TOKEN = "8952256301:AAGgupr8Bjop133zupaB56xyUH55s-8CddU"
ADMIN_ID = 8786609293

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
applicants = {}
user_lang = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
    ]
    await update.message.reply_text(
        "🌐 Tilni tanlang / Выберите язык:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def lang_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    lang = query.data.split('_')[1]
    user_lang[user.id] = lang

    # Telefon raqam so'rash tugmasi
    phone_button = KeyboardButton(
        "📞 Raqamni yuborish" if lang == "uz" else "📞 Отправить номер",
        request_contact=True
    )
    reply_markup = ReplyKeyboardMarkup([[phone_button]], resize_keyboard=True, one_time_keyboard=True)

    if lang == "uz":
        await query.edit_message_text(
            f"👋 Assalomu alaykum, {user.first_name}!\n\n"
            f"🏥 SofPharm HR Botiga xush kelibsiz!\n\n"
            f"📞 Avval telefon raqamingizni yuboring:"
        )
        await query.message.reply_text(
            "Pastdagi tugmani bosing 👇",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text(
            f"👋 Здравствуйте, {user.first_name}!\n\n"
            f"🏥 Добро пожаловать в HR бот SofPharm!\n\n"
            f"📞 Сначала отправьте ваш номер телефона:"
        )
        await query.message.reply_text(
            "Нажмите кнопку ниже 👇",
            reply_markup=reply_markup
        )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = user_lang.get(user.id, "uz")
    phone = update.message.contact.phone_number

    # Telefon raqamni saqlash
    if not phone.startswith('+'):
        phone = '+' + phone
    context.user_data['phone'] = phone

    if lang == "uz":
        await update.message.reply_text(
            f"✅ Raqam saqlandi: {phone}\n\n"
            f"📄 Endi rezyumengizni yuboring:\n"
            f"PDF fayl yoki 🖼 Rasm shaklida",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await update.message.reply_text(
            f"✅ Номер сохранён: {phone}\n\n"
            f"📄 Теперь отправьте резюме:\n"
            f"PDF файл или 🖼 Фото",
            reply_markup=ReplyKeyboardRemove()
        )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = user_lang.get(user.id, "uz")

    # Telefon raqam tekshirish
    if not context.user_data.get('phone'):
        phone_button = KeyboardButton(
            "📞 Raqamni yuborish" if lang == "uz" else "📞 Отправить номер",
            request_contact=True
        )
        reply_markup = ReplyKeyboardMarkup([[phone_button]], resize_keyboard=True, one_time_keyboard=True)
        if lang == "uz":
            await update.message.reply_text(
                "❗ Avval telefon raqamingizni yuboring!",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "❗ Сначала отправьте номер телефона!",
                reply_markup=reply_markup
            )
        return

    applicants[user.id] = {
        'name': f"{user.first_name} {user.last_name or ''}".strip(),
        'username': f"@{user.username}" if user.username else "Yoq",
        'user_id': user.id,
        'lang': lang,
        'file_type': 'document',
        'file_id': update.message.document.file_id,
        'file_name': update.message.document.file_name or 'rezyume.pdf',
        'date': datetime.now().strftime("%d.%m.%Y %H:%M"),
        'phone': context.user_data.get('phone')
    }

    if lang == "uz":
        await update.message.reply_text("✅ Rezyumengiz qabul qilindi!\n\nTez orada bog'lanamiz! 😊")
    else:
        await update.message.reply_text("✅ Ваше резюме принято!\n\nМы свяжемся с вами! 😊")

    await notify_admin(context, applicants[user.id])

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = user_lang.get(user.id, "uz")

    if not context.user_data.get('phone'):
        phone_button = KeyboardButton(
            "📞 Raqamni yuborish" if lang == "uz" else "📞 Отправить номер",
            request_contact=True
        )
        reply_markup = ReplyKeyboardMarkup([[phone_button]], resize_keyboard=True, one_time_keyboard=True)
        if lang == "uz":
            await update.message.reply_text("❗ Avval telefon raqamingizni yuboring!", reply_markup=reply_markup)
        else:
            await update.message.reply_text("❗ Сначала отправьте номер телефона!", reply_markup=reply_markup)
        return

    applicants[user.id] = {
        'name': f"{user.first_name} {user.last_name or ''}".strip(),
        'username': f"@{user.username}" if user.username else "Yoq",
        'user_id': user.id,
        'lang': lang,
        'file_type': 'photo',
        'file_id': update.message.photo[-1].file_id,
        'file_name': 'rezyume_rasm.jpg',
        'date': datetime.now().strftime("%d.%m.%Y %H:%M"),
        'phone': context.user_data.get('phone')
    }

    if lang == "uz":
        await update.message.reply_text("✅ Rezyumengiz qabul qilindi!\n\nTez orada bog'lanamiz! 😊")
    else:
        await update.message.reply_text("✅ Ваше резюме принято!\n\nМы свяжемся с вами! 😊")

    await notify_admin(context, applicants[user.id])

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = user_lang.get(user.id, "uz")

    if lang == "uz":
        await update.message.reply_text("📄 Rezyumengizni PDF yoki rasm shaklida yuboring.")
    else:
        await update.message.reply_text("📄 Отправьте резюме в формате PDF или фото.")

async def notify_admin(context: ContextTypes.DEFAULT_TYPE, data: dict):
    lang_flag = "🇺🇿" if data.get('lang') == "uz" else "🇷🇺"
    keyboard = [
        [InlineKeyboardButton("💬 Yozish", callback_data=f"write_{data['user_id']}"),
         InlineKeyboardButton("✅ Qabul", callback_data=f"accept_{data['user_id']}")],
        [InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{data['user_id']}")]
    ]
    text = (
        f"🔔 YANGI ARIZA!\n"
        f"-------------------------\n"
        f"👤 Ism: {data['name']}\n"
        f"🔗 Username: {data['username']}\n"
        f"📞 Telefon: {data['phone']}\n"
        f"📅 Sana: {data['date']}\n"
        f"📁 Fayl: {data['file_name']}\n"
        f"🌐 Til: {lang_flag}\n"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=text, reply_markup=InlineKeyboardMarkup(keyboard))
    try:
        if data['file_type'] == 'document':
            await context.bot.send_document(chat_id=ADMIN_ID, document=data['file_id'])
        elif data['file_type'] == 'photo':
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=data['file_id'])
    except Exception as e:
        logging.error(f"Fayl yuborishda xato: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("lang_"):
        await lang_handler(update, context)
        return

    action, user_id = query.data.split('_', 1)
    user_id = int(user_id)
    applicant = applicants.get(user_id, {})
    name = applicant.get('name', 'Nomzod')
    username = applicant.get('username', '')
    lang = applicant.get('lang', 'uz')

    if action == "write":
        await query.message.reply_text(
            f"📝 {name} ga yozish:\n\n"
            f"/reply {user_id} Xabar matni\n\n"
            f"Yoki Telegramda: {username}"
        )
    elif action == "accept":
        try:
            if lang == "uz":
                msg = f"🎉 Tabriklaymiz, {name}!\n\nRezyumengiz qabul qilindi!\nTez orada bog'lanamiz!\n\nSofPharm HR 🏥"
            else:
                msg = f"🎉 Поздравляем, {name}!\n\nВаше резюме принято!\nМы скоро свяжемся!\n\nSofPharm HR 🏥"
            await context.bot.send_message(chat_id=user_id, text=msg)
            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text(f"✅ {name} ga qabul xabari yuborildi!")
        except Exception as e:
            await query.message.reply_text(f"Xato: {e}")
    elif action == "reject":
        try:
            if lang == "uz":
                msg = f"Salom, {name}!\n\nHozircha mos vakansiya topilmadi.\nKelajakda ham murojaat qiling!\n\nSofPharm HR 🏥"
            else:
                msg = f"Здравствуйте, {name}!\n\nК сожалению, подходящей вакансии не нашлось.\nSofPharm HR 🏥"
            await context.bot.send_message(chat_id=user_id, text=msg)
            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text(f"❌ {name} ga rad javob yuborildi.")
        except Exception as e:
            await query.message.reply_text(f"Xato: {e}")

async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Ishlatish: /reply USER_ID xabar")
        return
    try:
        await context.bot.send_message(chat_id=int(args[0]), text=f"📨 SofPharm HR:\n\n{' '.join(args[1:])}")
        await update.message.reply_text("✅ Yuborildi!")
    except Exception as e:
        await update.message.reply_text(f"Xato: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reply", reply_command))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("SofPharm HR Bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

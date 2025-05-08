from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database import Data
import os
from dotenv import load_dotenv

# تحميل المتغيرات من .env
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')


# 🟢 رسالة الترحيب
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = update.effective_user
    message = f'''مرحبًا بك "{user_data.first_name}" في بوت إدارة ملفاتك الشخصية! 📁

📌 يمكنك استخدام هذا البوت لحفظ الصور والملفات بسهولة، واسترجاعها لاحقًا.

✅ الأوامر المتوفرة:
/start - عرض هذه الرسالة الترحيبية
/myfiles - عرض الملفات التي أرسلتها
/delete <id> - حذف ملف معين من ملفاتك
/help - عرض التعليمات

🔁 فقط أرسل أي ملف وسنقوم بحفظه لك فورًا!
'''
    await update.message.reply_text(message)


# 💾 حفظ الملفات المرسلة
async def save_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    download_path = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_path, exist_ok=True)

    if update.message.photo:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        file_id = photo.file_id
        file_name = f'user_{file_id}.jpg'
        Data().save_data(user_id, file_id, photo.file_size, file_name, 'jpg')
        await file.download_to_drive(os.path.join(download_path, file_name))
        await update.message.reply_text('✅ تم حفظ الصورة بنجاح!')

    elif update.message.document:
        document = update.message.document
        file = await document.get_file()
        file_id = document.file_id
        file_type = document.mime_type.split('/')[-1] if document.mime_type else 'file'
        file_name = f'user_{file_id}.{file_type}'
        Data().save_data(user_id, file_id, document.file_size, file_name, file_type)
        await file.download_to_drive(os.path.join(download_path, file_name))
        await update.message.reply_text('✅ تم حفظ الملف بنجاح!')


# 📂 عرض الملفات
async def myfiles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    get_data = Data().get_user_files(user_id)

    if not get_data:
        await update.message.reply_text("📭 لا يوجد لديك ملفات محفوظة بعد")
        return

    for id, file_name, file_id in get_data:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f'⬇️ تنزيل {id}', callback_data=f'download_{id}'),
             InlineKeyboardButton(f'🗑️ حذف {id}', callback_data=f'delete_{id}')]
        ])
        await update.message.reply_text(file_name[:50], reply_markup=keyboard)


# ⌨️ أزرار التنزيل والحذف
async def handler_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    download_path = os.path.join(os.getcwd(), "downloads")
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()

    get_data = Data().get_user_files(user_id)
    for id, file_name, file_id in get_data:
        if int(query.data.split('_')[1]) == id:
            action = query.data.split('_')[0]
            file_path = os.path.join(download_path, file_name)

            if action == "download":
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=f)
                        else:
                            await context.bot.send_document(chat_id=update.effective_chat.id, document=f)
                else:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ الملف غير موجود.")
            elif action == "delete":
                Data().delete_file_by_id(id)
                if os.path.exists(file_path):
                    os.remove(file_path)
                await context.bot.send_message(chat_id=update.effective_chat.id, text="🗑️ تم حذف الملف بنجاح.")


# 🆘 رسالة المساعدة
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = '''🆘 *مساعدة - قائمة الأوامر المتاحة*:

/start - عرض رسالة الترحيب والتعليمات.
/myfiles - عرض جميع ملفاتك المحفوظة.
/delete <id> - حذف ملف برقم معين.
/help - عرض هذه الرسالة.

🔁 فقط أرسل أي *صورة* أو *ملف* وسنقوم بحفظه تلقائيًا!

💾 الملفات تحفظ باسمك ويمكنك تنزيلها أو حذفها من خلال الأزرار.
'''
    await update.message.reply_text(message, parse_mode='Markdown')


# 🚀 تشغيل البوت
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(CommandHandler('myfiles', myfiles))
    app.add_handler(MessageHandler((filters.PHOTO | filters.Document.ALL) & ~filters.COMMAND, save_data))
    app.add_handler(CallbackQueryHandler(handler_button))
    print('Bot Starting...')
    app.run_polling()
    print('Bot Stopping...')

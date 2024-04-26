from config import BOT_TOKEN
import logging
import asyncio

from telegram import ForceReply, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


reply_keyboard = [['/my_chat_id', '/chat_id']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        f"👋 Привет, {user.mention_html()}! Я твой бот-помощник! Чем я могу помочь? \n"
        f"/my_chat_id - твой chat id\n"
        f"/chat_id - chat id по username", reply_markup=markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я пока не умею помогать", reply_markup=markup)


async def my_chat_id(update, context):
    # chat_id = update.effective_message.chat_id
    # await update.message.reply_text(
    #     f"Ваш chat id: {chat_id}", reply_markup=markup)
    chat_id = update['message']['chat']['id']
    await update.message.reply_text(
        f"Ваш chat id: {chat_id}", reply_markup=markup)


async def chat_id(update, context):
    await update.message.reply_text(
        f"Скопируйте username контакта и пришлите мне", reply_markup=markup)
    return 1


async def first_response(update, context):
    user = update.message.from_user
    logger.info("Пользователь %s рассказал: %s", user.first_name, update.message.text)
    username = update.message.text
    context.user_data['username'] = username
    try:
        await update.message.reply_text(
            f"Username {username}", reply_markup=markup)
        await update.message.reply_text(
            f"Username id {username.chat_id}", reply_markup=markup)
    except AttributeError:
        return update.message.reply_text(
            f"Error: AttributeError", reply_markup=markup)
    return ConversationHandler.END


async def stop(update, context):
    user = update.message.from_user
    logger.info("Пользователь %s отменил разговор.", user.first_name)
    return ConversationHandler.END


async def close_keyboard(update, context):
    await update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


if __name__ == '__main__':
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("my_chat_id", my_chat_id))
    application.add_handler(CommandHandler("close", close_keyboard))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('chat_id', chat_id)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response)]
        },

        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)

    application.run_polling()

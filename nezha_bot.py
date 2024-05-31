import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler
from telegram.ext import Filters as filters 
import requests

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary to store user tokens and dashboard URLs
user_data = {}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to Nezha Monitor Bot! Please provide your API Token and Dashboard URL in the format:\n/token <API_TOKEN> <DASHBOARD_URL>')

def set_token(update: Update, context: CallbackContext) -> None:
    try:
        token, dashboard_url = context.args
        user_id = update.message.chat_id
        user_data[user_id] = {'token': token, 'dashboard_url': dashboard_url}
        update.message.reply_text('Your API Token and Dashboard URL have been set!')
    except ValueError:
        update.message.reply_text('Invalid format. Please use: /token <API_TOKEN> <DASHBOARD_URL>')

def get_all_servers(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    if user_id not in user_data:
        update.message.reply_text('Please set your API Token and Dashboard URL first using /token command.')
        return

    token = user_data[user_id]['token']
    dashboard_url = user_data[user_id]['dashboard_url']
    headers = {"Authorization": f"Token {token}"}
    url = f"{dashboard_url}/api/v1/server/list"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        servers = data.get('result', [])
        message = ''
        for server in servers:
            message += f"Server Name: {server['name']}, Last Active: {server['last_active']}, IP: {server['valid_ip']}\n"
        update.message.reply_text(message or "No servers found.")
    else:
        update.message.reply_text('Failed to retrieve server list.')

def get_server_details(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    if user_id not in user_data:
        update.message.reply_text('Please set your API Token and Dashboard URL first using /token command.')
        return

    try:
        server_id = context.args[0]
    except IndexError:
        update.message.reply_text('Please provide a server ID.')
        return

    token = user_data[user_id]['token']
    dashboard_url = user_data[user_id]['dashboard_url']
    headers = {"Authorization": f"Token {token}"}
    url = f"{dashboard_url}/api/v1/server/details?id={server_id}"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        server = data.get('result', [])[0]
        message = (f"Server Name: {server['name']}\n"
                   f"CPU Usage: {server['status']['CPU']}%\n"
                   f"Memory Used: {server['status']['MemUsed']} bytes\n"
                   f"Disk Used: {server['status']['DiskUsed']} bytes\n"
                   f"Network In Speed: {server['status']['NetInSpeed']} bytes/s\n"
                   f"Network Out Speed: {server['status']['NetOutSpeed']} bytes/s")
        update.message.reply_text(message)
    else:
        update.message.reply_text('Failed to retrieve server details.')

def error(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
    updater = Updater("7276957363:AAGtfCeqYCLcz7RzvFF4gdDamGTwLadJzzs", use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("token", set_token))
    dp.add_handler(CommandHandler("all", get_all_servers))
    dp.add_handler(CommandHandler("id", get_server_details, pass_args=True))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

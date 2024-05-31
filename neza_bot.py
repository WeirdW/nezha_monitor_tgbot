import logging
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

API_TOKEN, DASHBOARD_URL = range(2)
user_data = {}

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('欢迎使用哪吒监控查询机器人！\n请发送你的 API Token。')
    return API_TOKEN

def get_api_token(update: Update, context: CallbackContext) -> int:
    user_data['api_token'] = update.message.text
    update.message.reply_text('API Token 已保存。\n请发送你的 Dashboard URL。')
    return DASHBOARD_URL

def get_dashboard_url(update: Update, context: CallbackContext) -> int:
    user_data['dashboard_url'] = update.message.text
    update.message.reply_text('Dashboard URL 已保存。\n你可以使用 /all 获取所有服务器信息，或使用 /id <服务器ID> 获取特定服务器详情。')
    return ConversationHandler.END

def all_servers(update: Update, context: CallbackContext):
    api_token = user_data.get('api_token')
    dashboard_url = user_data.get('dashboard_url')
    
    if not api_token or not dashboard_url:
        update.message.reply_text('请先使用 /start 命令设置 API Token 和 Dashboard URL。')
        return
    
    headers = {"Authorization": f"Token {api_token}"}
    response = requests.get(f"{dashboard_url}/api/v1/server/list", headers=headers)
    data = response.json()
    
    if data['code'] == 0:
        result = data['result']
        message = "服务器列表：\n"
        for server in result:
            message += f"ID: {server['id']}, 名称: {server['name']}, 最后活跃时间: {server['last_active']}, IP: {server['valid_ip']}\n"
        update.message.reply_text(message)
    else:
        update.message.reply_text('获取服务器列表失败。')

def server_details(update: Update, context: CallbackContext):
    api_token = user_data.get('api_token')
    dashboard_url = user_data.get('dashboard_url')
    
    if not api_token or not dashboard_url:
        update.message.reply_text('请先使用 /start 命令设置 API Token 和 Dashboard URL。')
        return
    
    try:
        server_id = context.args[0]
    except IndexError:
        update.message.reply_text('请提供服务器 ID。用法: /id <服务器ID>')
        return
    
    headers = {"Authorization": f"Token {api_token}"}
    response = requests.get(f"{dashboard_url}/api/v1/server/details?id={server_id}", headers=headers)
    data = response.json()
    
    if data['code'] == 0:
        server = data['result'][0]
        message = (
            f"服务器名称: {server['name']}\n"
            f"CPU 使用率: {server['status']['CPU']}%\n"
            f"内存使用: {server['status']['MemUsed']} bytes\n"
            f"磁盘使用: {server['status']['DiskUsed']} bytes\n"
            f"网络入速率: {server['status']['NetInSpeed']} bytes/s\n"
            f"网络出速率: {server['status']['NetOutSpeed']} bytes/s\n"
        )
        update.message.reply_text(message)
    else:
        update.message.reply_text('获取服务器详情失败。')

def main():
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            API_TOKEN: [MessageHandler(Filters.text & ~Filters.command, get_api_token)],
            DASHBOARD_URL: [MessageHandler(Filters.text & ~Filters.command, get_dashboard_url)],
        },
        fallbacks=[]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('all', all_servers))
    dp.add_handler(CommandHandler('id', server_details))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

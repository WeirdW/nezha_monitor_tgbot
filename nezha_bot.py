import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

# 配置日志记录
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

API_TOKEN = "7276957363:AAGtfCeqYCLcz7RzvFF4gdDamGTwLadJzzs"

# 在这里定义全局变量来存储用户的哪吒监控信息
user_nezha_info = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        '欢迎使用哪吒监控查询机器人！请发送你的哪吒监控 API Token 和 Dashboard 链接，格式如下：\n'
        '/config <API Token> <Dashboard URL>'
    )

async def config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 2:
        await update.message.reply_text('格式错误！请发送 /config <API Token> <Dashboard URL>')
        return
    
    api_token, dashboard_url = context.args
    user_id = update.message.from_user.id
    user_nezha_info[user_id] = {'api_token': api_token, 'dashboard_url': dashboard_url}
    
    await update.message.reply_text('配置成功！你可以使用 /all 查看所有服务器信息，使用 /id <Server ID> 查看特定服务器详情。')

async def get_all_servers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_nezha_info:
        await update.message.reply_text('请先使用 /config 命令配置你的 API Token 和 Dashboard URL。')
        return

    api_token = user_nezha_info[user_id]['api_token']
    dashboard_url = user_nezha_info[user_id]['dashboard_url']
    
    headers = {"Authorization": api_token}
    response = requests.get(f"{dashboard_url}/api/v1/server/list", headers=headers)
    
    # 打印调试信息
    logging.info(f'API响应状态码: {response.status_code}')
    logging.info(f'API响应内容: {response.text}')

    if response.status_code == 200:
        try:
            data = response.json()
            logging.info(f'解析后的响应数据: {data}')
            servers = data.get('result', [])
            if not servers:
                await update.message.reply_text('未找到服务器信息。')
                return

            message = '服务器列表：\n'
            for server in servers:
                message += f"ID: {server['id']}, Name: {server['name']}\n"
            await update.message.reply_text(message)
        except ValueError:
            await update.message.reply_text('解析响应失败，返回的不是有效的JSON格式。')
    else:
        await update.message.reply_text(f'获取服务器信息失败，状态码：{response.status_code}，响应内容：{response.text}')

async def get_server_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1:
        await update.message.reply_text('格式错误！请发送 /id <Server ID>')
        return

    user_id = update.message.from_user.id
    if user_id not in user_nezha_info:
        await update.message.reply_text('请先使用 /config 命令配置你的 API Token 和 Dashboard URL。')
        return

    server_id = context.args[0]
    api_token = user_nezha_info[user_id]['api_token']
    dashboard_url = user_nezha_info[user_id]['dashboard_url']
    
    headers = {"Authorization": api_token}
    response = requests.get(f"{dashboard_url}/api/v1/server/details?id={server_id}", headers=headers)
    
    # 打印调试信息
    logging.info(f'API响应状态码: {response.status_code}')
    logging.info(f'API响应内容: {response.text}')

    if response.status_code == 200:
        try:
            data = response.json()
            logging.info(f'解析后的响应数据: {data}')
            servers = data.get('result', None)
            if not servers:
                await update.message.reply_text('未找到服务器信息。')
                return

            server = servers[0]  # 取列表中的第一个元素
            message = (
                f"ID: {server['id']}\n"
                f"Name: {server['name']}\n"
                f"Status: {server['status']['CPU']}%\n"
                f"Uptime: {server['status']['Uptime']}\n"
                f"CPU Usage: {server['status']['CPU']}%\n"
                f"Memory Usage: {server['status']['MemUsed']} bytes\n"
                f"Disk Usage: {server['status']['DiskUsed']} bytes\n"
            )
            await update.message.reply_text(message)
        except ValueError:
            await update.message.reply_text('解析响应失败，返回的不是有效的JSON格式。')
    else:
        await update.message.reply_text(f'获取服务器信息失败，状态码：{response.status_code}，响应内容：{response.text}')


def main():
    app = ApplicationBuilder().token(API_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("config", config))
    app.add_handler(CommandHandler("all", get_all_servers))
    app.add_handler(CommandHandler("id", get_server_by_id))

    app.run_polling()

if __name__ == '__main__':
    main()

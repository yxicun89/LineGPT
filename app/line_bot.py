import os
from linebot import LineBotApi

channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

if channel_access_token is None:
    raise ValueError("LINE_CHANNEL_ACCESS_TOKEN environment variable is not set")

line_bot_api = LineBotApi(channel_access_token)
from flask import Blueprint, request, jsonify, current_app
from linebot import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage, FollowEvent
from .line_bot import line_bot_api
from openai import OpenAI
import os
import base64

main_bp = Blueprint('main', __name__)

handler = WebhookHandler('Put your LINE_CHANNEL_SECRET here')

# OpenAI クライアントの初期化
client = OpenAI()

SYSTEM_CONTENT = """あなたは画像認識と栄養分析の専門家です。送られてきた画像に基づいて以下のように応答してください：

1. 料理の画像の場合：
   - 料理名を特定してください。
   - おおよそのカロリー、タンパク質、脂質、炭水化物の量を推定してください。
   - その料理の主な栄養価や健康への影響について簡単に説明してください。
   - 応答形式：
     料理名：[料理名]
     推定栄養価：
     - カロリー：約[数値]kcal
     - タンパク質：約[数値]g
     - 脂質：約[数値]g
     - 炭水化物：約[数値]g
     
     栄養解説：[簡単な解説]

2. それ以外の画像の場合：
   - 画像に写っているものを詳細に説明してください。
   - 主な被写体、色彩、構図などの特徴を述べてください。
   - 画像から感じ取れる雰囲気や印象についても言及してください。
   - 応答形式：
     画像の内容：[詳しい説明]
     
     詳細解説：
     [詳細な説明、特徴、印象など]

注意事項：
- 常に客観的かつ正確な情報を提供するよう心がけてください。
- 推測に基づく情報は、それが推測であることを明確にしてください。
- 不適切または有害な内容を含む画像の場合は、その旨を丁寧に伝え、詳細な説明は控えてください。

以上の指示に従って、送られてきた画像に対して適切な応答を生成してください。"""

@main_bp.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return jsonify({'error': 'Invalid signature'}), 400
    return 'OK'

@handler.add(MessageEvent, message=(TextMessage, ImageMessage))
def handle_message(event):
    if isinstance(event.message, ImageMessage):
        # 画像メッセージの場合
        message_content = line_bot_api.get_message_content(event.message.id)
        static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        if not os.path.exists(static_folder):
            os.makedirs(static_folder)
        image_path = os.path.join(static_folder, f"{event.message.id}.jpg")
        with open(image_path, 'wb') as f:
            for chunk in message_content.iter_content():
                f.write(chunk)
        
        # 画像をbase64エンコード
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

        # GPT-4 Visionを使用して画像認識
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_CONTENT
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "この画像を分析し、指示に従って応答してください。"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_string}"}}
                    ],
                }
            ],
            max_tokens=500,
        )

        assistant_response = response.choices[0].message.content.strip()
        reply_message = f"画像分析結果：\n\n{assistant_response}"

        # 画像ファイルを削除
        os.remove(image_path)

    else:
        # テキストメッセージの場合
        user_message = event.message.text
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたは優秀なエンジニアです。。ユーザーの質問に対してわかりやすく教えてください。"},
                {"role": "user", "content": user_message}
            ],
            max_tokens=300,
        )
        reply_message = response.choices[0].message.content.strip()

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )

@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id  # ユーザーのIDを取得
    nickname = line_bot_api.get_profile(user_id).display_name 
    welcome_message = "ご登録ありがとうございます。"+"ようこそブタチームの就活支援サービスへ！\n"+ "#自己紹介を入れて次の情報を教えてくれると、より適切なサポートができます!!\n"+"年齢、ニックネーム、居住地、文理選択、希望職種、簡単な経歴"
    service_description = "こちらは、音声認識を用いた面接練習や、画像認識でのES添削などができる就活生向けのLINEbotです。ESを添削してもらいたい場合は画像をアップロードし、面接練習をしたい場合は下のタブメニューから選んでください！"
    messages = [
        TextSendMessage(text=welcome_message),
        TextSendMessage(text=service_description)
    ]

    line_bot_api.push_message(user_id, messages)
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai

app = Flask(__name__)

# LINE 聊天機器人的 Channel Access Token 和 Channel Secret
line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

@app.route("/callback", methods=['POST'])
def callback():
    # 獲取 LINE 平台傳來的 X-Line-Signature，用於驗證 LINE 聊天機器人的請求
    signature = request.headers['X-Line-Signature']

    # 獲取 LINE 平台傳來的 HTTP 請求主體
    body = request.get_data(as_text=True)

    # 處理 LINE 聊天機器人的訊息
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# OpenAI GPT 的設定
openai.api_key = ""

# GPT 模型的回答
def generate_answer(prompt):
    model_engine = "text-davinci-002"
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )
    message = response.choices[0].text.strip()
    return message

# 回覆使用者傳送的文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 當收到使用者傳送的文字訊息時，回覆 OpenAI GPT 的回答
    response = generate_answer(event.message.text)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )



if __name__ == "__main__":
    app.run()

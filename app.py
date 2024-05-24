from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import os
import datetime

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 使用字典儲存每天的待辦事項，key是日期，value是待辦事項列表
todo_list = {}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text
    if "我今天要做的事情：" in msg:
        # 切割訊息，取得日期和待辦事項
        _, date, tasks = msg.split("：", 2)
        date = date.strip()
        tasks = tasks.strip().split("、")
        todo_list[date] = tasks
        line_bot_api.reply_message(event.reply_token, TextSendMessage(f"已記錄{date}的待辦事項：{tasks}"))
    elif "查看今天完成了什麼事情" in msg:
        today = datetime.date.today().strftime("%Y-%m-%d")
        tasks_done = todo_list.get(today, [])
        if tasks_done:
            reply_msg = f"今天已完成的待辦事項：{tasks_done}"
        else:
            reply_msg = "今天還沒有完成任何待辦事項哦！"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(reply_msg))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

from flask import Flask, request, jsonify
import requests
import schedule
import time
import threading

app = Flask(__name__)
channel_access_token = 'sCIp24H+cQ/Swy9T92tPrziaIvWLYqaTMrtJ+rnPEZI2osz/o4xtSM2aymVf6tWiFWWuBAAGbcuwAG/yB4Nv5cL36thJQTokFM5bVOpQAHQQWawXybZVE/otQxGx1s7WFUR70xu0dXaCEfGApn8jMwdB04t89/1O/w1cDnyilFU='

todos = {}
remind_time = {}

def send_message(to, message):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {channel_access_token}'
    }
    data = {
        'to': to,
        'messages': [{
            'type': 'text',
            'text': message
        }]
    }
    requests.post('https://api.line.me/v2/bot/message/push', headers=headers, json=data)

def check_todos():
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/webhook', methods=['POST'])
def webhook():
    body = request.json
    events = body['events']
    for event in events:
        user_id = event['source']['userId']
        text = event['message']['text']
        if text.startswith('今天的待辦事項'):
            todos[user_id] = text[7:]
            send_message(user_id, '已保存今天的待辦事項！')
        elif text.startswith('設定檢查時間'):
            time_str = text[6:]
            schedule.every().day.at(time_str).do(send_message, user_id, f'今日待辦事項：{todos.get(user_id, "未設置")}')
            send_message(user_id, f'已設定檢查時間為 {time_str}!')
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    threading.Thread(target=check_todos).start()
    app.run(port=5000)

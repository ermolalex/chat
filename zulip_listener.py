import sys
import zulip
import requests

from app.zulip_client import ZulipClient
from app.config import settings

zulip_client = ZulipClient().client


def send_msg_to_bot(text):
   token = settings.BOT_TOKEN
   chat_id = str(settings.ADMIN_ID)
   url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + text
   results = requests.get(url_req)
   print(results.json())


def on_message(msg: dict):
    if msg["subject"] == "от бота":
        channel_name = msg["display_recipient"]
        if channel_name[0] == "+":
            print(f"Сообщение в адрес {channel_name}: {msg['content']}")
            send_msg_to_bot(msg['content'])

zulip_client.call_on_each_message(on_message)

#zulip_client.call_on_each_event(lambda event: sys.stdout.write(str(event) + "\n"))

#{'type': 'message',
# 'message':
# {'id': 59, 'sender_id': 8, 'content': 'тест 13:09', 'recipient_id': 13,
# 'timestamp': 1744193389, 'client': 'website', 'subject': 'tg_bot', 'topic_links': [], 'is_me_message': False,
# 'reactions': [], 'submessages': [], 'sender_full_name': 'Александр Ермолаев', 'sender_email': 'alex@kik-soft.ru',
# 'sender_realm_str': '', 'display_recipient': 'test', 'type': 'stream', 'stream_id': 5, 'avatar_url': None,
# 'content_type': 'text/x-markdown'},
# 'flags': ['read'], 'id': 37}

# {'id': 64, 'sender_id': 8, 'content': 'Тест 13:25', 'recipient_id': 18, 'timestamp': 1744194320,
# 'client': 'website', 'subject': 'от бота', 'topic_links': [], 'is_me_message': False, 'reactions': [],
# 'submessages': [], 'sender_full_name': 'Александр Ермолаев', 'sender_email': 'alex@kik-soft.ru',
# 'sender_realm_str': '', 'display_recipient': '+79219376763', 'type': 'stream', 'stream_id': 10,
# 'avatar_url': None, 'content_type': 'text/x-markdown'}


# Откройте браузер и перейдите по ссылке, заменив <Bot_token> и <chat_id> на свои данные
# https://api.telegram.org/bot<Bot_token>/sendMessage?chat_id=<chat_id>&text=Привет%20мир

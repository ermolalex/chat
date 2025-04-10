import sys
import zulip
import requests

from app.zulip_client import ZulipClient
from app.config import settings

zulip_client = ZulipClient().client


def send_msg_to_bot(user_tg_id, text):
    # # https://api.telegram.org/bot<Bot_token>/sendMessage?chat_id=<chat_id>&text=Привет%20мир
    token = settings.BOT_TOKEN
    chat_id = str(user_tg_id)
    url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + text
    results = requests.get(url_req)
    print(results.json())


def on_message(msg: dict):
    # print(msg)
    if msg["subject"] == "от бота" and msg["client"] == "website":
        channel_name = msg["display_recipient"]
        phone, user_tg_id = tuple(channel_name.split("_"))
        if user_tg_id and user_tg_id.isnumeric():
            print(f"Сообщение в адрес {channel_name}: {msg['content']}")
            send_msg_to_bot(user_tg_id, msg['content'])

zulip_client.call_on_each_message(on_message)

# от ТгБота
# {'id': 86, 'sender_id': 8, 'content': 'проблема 7', 'recipient_id': 20, 'timestamp': 1744282058, 'client': 'ZulipPython',
# 'subject': 'от бота', 'topic_links': [], 'is_me_message': False, 'reactions': [], 'submessages': [], 'sender_full_name': 'Александр Ермолаев',
# 'sender_email': 'alex@kik-soft.ru', 'sender_realm_str': '', 'display_recipient': '79219376763_542393918', 'type': 'stream', 'stream_id': 12,
# 'avatar_url': None, 'content_type': 'text/x-markdown'}
# {'ok': True, 'result': {'message_id': 480, 'from': {'id': 7586848030, 'is_bot': True, 'first_name': 'kik-test-bot', 'username': 'kik_soft_supp_bot'},
# 'chat': {'id': 542393918, 'first_name': 'Александр', 'type': 'private'}, 'date': 1744282059, 'text': 'проблема 7'}}

# от Zulip
# {'id': 87, 'sender_id': 8, 'content': 'решение 6', 'recipient_id': 20, 'timestamp': 1744282105, 'client': 'website',
# 'subject': 'от бота', 'topic_links': [], 'is_me_message': False, 'reactions': [], 'submessages': [], 'sender_full_name': 'Александр Ермолаев',
# 'sender_email': 'alex@kik-soft.ru', 'sender_realm_str': '', 'display_recipient': '79219376763_542393918', 'type': 'stream', 'stream_id': 12,
# 'avatar_url': None, 'content_type': 'text/x-markdown'}
# {'ok': True, 'result': {'message_id': 481, 'from': {'id': 7586848030, 'is_bot': True, 'first_name': 'kik-test-bot', 'username': 'kik_soft_supp_bot'},
# 'chat': {'id': 542393918, 'first_name': 'Александр', 'type': 'private'}, 'date': 1744282106, 'text': 'решение 6'}}

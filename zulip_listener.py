import sys
import re
import zulip
import requests
from sqlmodel import  Session
from app.db import DB
from app.logger import create_logger
from app.zulip_client import ZulipClient
from app.config import settings
from app import helpers

logger = create_logger(logger_name=__name__)

db = DB()
session = Session(db.engine)

zulip_client = ZulipClient().client
"""   !!!! Важно
Пользователь, от лица которого создается клиент, 
(прописан в переменных окружения ZULIP_API_KEY, ZULIP_EMAIL)
д.б. подписан на каналы, сообщения в которых нужно перехватывать.
=> Пользователь ТГБот д.б. подписан на все каналы.  
"""
# todo Пользователь ТГБот д.б. подписан на все каналы.
# todo все сотрудники ТехОтдела д.б. подписаны на все каналы.


def send_msg_to_bot(user_tg_id, text):
    # # https://api.telegram.org/bot<Bot_token>/sendMessage?chat_id=<chat_id>&text=Привет%20мир
    token = settings.BOT_TOKEN
    chat_id = str(user_tg_id)
    url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + text
    results = requests.get(url_req)
    print(results.json())


def extract_tg_id_from_subject(subject: str):
    try:
        _, tg_id = tuple(subject.split("_"))
        return tg_id
    except ValueError:
        msg_text = f"При попытке отправить сообщение из zulip, не удалось извлеч TG_ID из строки {subject}"
        logger.error(msg_text)
        send_msg_to_bot(settings.ADMIN_ID, msg_text)
        return None

def clean_msg_text(raw_text: str) -> str:
    # чистим тект сообщения

    # редактируем цитирование
    clean_text = helpers.clean_quote(raw_text)

    return clean_text

def on_message(msg: dict):
    logger.info(msg)
    if msg["client"] in  ("website", "ZulipMobile"):
        subject = msg["subject"]
        user_tg_id = extract_tg_id_from_subject(subject)

        if user_tg_id and user_tg_id.isnumeric():
            msg_content = clean_msg_text(msg['content'])
            msg_text = f"{msg['sender_full_name']}: {msg_content}"

            send_msg_to_bot(user_tg_id, msg_text)


zulip_client.call_on_each_message(on_message)


# от ТгБота
# {'id': 86, 'sender_id': 8, 'content': 'проблема 7', 'recipient_id': 20, 'timestamp': 1744282058, 'client': 'ZulipPython',
# 'subject': 'от бота', 'topic_links': [], 'is_me_message': False, 'reactions': [], 'submessages': [], 'sender_full_name': 'Александр Ермолаев',
# 'sender_email': 'alex@kik-soft.ru', 'sender_realm_str': '', 'display_recipient': '79219376763_542393918', 'type': 'stream', 'stream_id': 12,
# 'avatar_url': None, 'content_type': 'text/x-markdown'}
# {'ok': True, 'result': {'message_id': 480, 'from': {'id': 7586848030, 'is_bot': True, 'first_name': 'kik-test-bot', 'username': 'kik_soft_supp_bot'},
# 'chat': {'id': 542393918, 'first_name': 'Александр', 'type': 'private'}, 'date': 1744282059, 'text': 'проблема 7'}}

# от Zulip
#{'id': 371, 'sender_id': 8, 'content': 'ping', 'recipient_id': 32, 'timestamp': 1750539450, 'client': 'website',
# 'subject': 'Александр_542393918', 'topic_links': [], 'is_me_message': False, 'reactions': [], 'submessages': [],
# 'sender_full_name': 'Александр Ермолаев', 'sender_email': 'alex@kik-soft.ru', 'sender_realm_str': '',
# 'display_recipient': 'КиК-софт (тестовый)', 'type': 'stream', 'stream_id': 20, 'avatar_url': None, 'content_type': 'text/x-markdown'}
#
# {'ok': True, 'result': {'message_id': 481, 'from': {'id': 7586848030, 'is_bot': True, 'first_name': 'kik-test-bot', 'username': 'kik_soft_supp_bot'},
# 'chat': {'id': 542393918, 'first_name': 'Александр', 'type': 'private'}, 'date': 1744282106, 'text': 'решение 6'}}

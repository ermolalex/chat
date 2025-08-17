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

"""
'[Снимок экрана от 2025-07-10 17-48-37.png](/user_uploads/2/4c/vQfELySoD1xFWvxK7lPBz6Yv/2025-07-10-17-48-37.png)  \nи еще и еще'
из этой строки выделяем 1)имя файла - все что в скобках 2)остальной текст 
"""
def uploaded_file_name(msg_text: str) -> str:
    pattern = r'[^(]+(\(\/.+\))'

    logger.info(f"***msg_text='{msg_text}'")
    matches = re.match(pattern, msg_text)
    if matches:
        file_name = matches.group(1)[1:-1]
        logger.info(f"***file_name='{file_name}'")
        return file_name
    else:
        return ''

def description_text(msg_text: str) -> str:
    pattern = r'(\(\/.+\))'
    substr = re.sub(pattern, '', msg_text)
    return substr


def send_photo_to_bot(user_tg_id: int, file_name: str):
    token = settings.BOT_TOKEN
    chat_id = str(user_tg_id)

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    files = {'photo': open(file_name, 'rb')}
    data = {'chat_id' : chat_id}
    result = requests.post(url, files=files, data=data)
    print(results.json())


def send_msg_to_bot(user_tg_id, zulip_text):
    # # https://api.telegram.org/bot<Bot_token>/sendMessage?chat_id=<chat_id>&text=Привет%20мир
    token = settings.BOT_TOKEN
    chat_id = str(user_tg_id)
    tgbot_text = zulip_text

    if '/user_uploads/' in zulip_text:  # отправляется файл
        file_name = uploaded_file_name(zulip_text)
        tgbot_text = description_text(zulip_text)
        logger.info(f"Sending photo from file {file_name}, descr: {tgbot_text}")
        try:
            send_photo_to_bot(user_tg_id, file_name)
        except FileNotFoundError:
            logger.error(f"Не найден файл по пути '{file_name}'")
            tgbot_text += "\nНе удалось отправить картинку..."

    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={tgbot_text}"
    results = requests.get(url)
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

        if user_tg_id and helpers.is_int_string(user_tg_id):
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

# от Zulip с картинкой
# {'id': 835, 'sender_id': 8,
# 'content': '[Снимок экрана от 2025-04-04 23-08-25.png](/user_uploads/2/c6/IF2RKikfklKeiJ9kSDMcBlWs/2025-04-04-23-08-25.png)',
# 'recipient_id': 13, 'timestamp': 1755448700, 'client': 'website', 'subject': 'Александр_542393918', 'topic_links': [],
# 'is_me_message': False, 'reactions': [], 'submessages': [], 'sender_full_name': 'Александр', 'sender_email': 'alex@kik-soft.ru',
# 'sender_realm_str': '', 'display_recipient': 'КиК-софт', 'type': 'stream', 'stream_id': 4, 'avatar_url': None,
# 'content_type': 'text/x-markdown'}

# картинка  'content': '[Снимок экрана от 2025-07-10 17-48-37.png](/user_uploads/2/4c/vQfELySoD1xFWvxK7lPBz6Yv/2025-07-10-17-48-37.png)  и еще текст\nи еще текст'

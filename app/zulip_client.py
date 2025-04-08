import sys
import logging
import zulip

from app.config import settings

class ZulipException(Exception):
    pass

class ZulipClient():
    def __init__(self):
        self.is_active = False
        self._create_client()

    def _create_client(self):
        try:
            self.client = zulip.Client(
                api_key=settings.ZULIP_API_KEY,
                email=settings.ZULIP_EMAIL,
                site=settings.ZULIP_SITE,
                insecure=settings.ZULIP_ALLOW_INSECURE
            )
            self.is_active = True
            logging.info("ZulipClient настроен.")

        except Exception as e:
            self.is_active = False
            logging.fatal(e)
            raise ZulipException(e)

    def send_msg_to_channel(self, channel: str, topic: str, msg: str) -> str:
        if not self.is_active:
            logging.warning("ZulipClient не настроен!")
            return

        request = {
            "type": "channel",
            "to": channel,
            "topic": topic,
            "content": msg,
        }
        result = self.client.send_message(request)
        logging.info(result)

    def get_channel_id(self, channel_name: str) -> int:
        # по названию канала возвращает его ID, или 0, если канала нет
        #
        # {'result': 'error', 'msg': "Invalid channel name 'tg_bot'", 'code': 'BAD_REQUEST'}
        # {'result': 'success', 'msg': '', 'stream_id': 6}

        if not channel_name:
            raise ValueError("Не указано название канала.")

        result = self.client.get_stream_id(channel_name)

        if result["result"] == 'success':
            return result["stream_id"]
        elif (result["result"] == 'error' and "Invalid channel name" in result["msg"]):  # todo
            return 0
        else:
            err_msg = f"Ошибка при обращении к каналу (get_channel_id) '{channel_name}' - {result.get('msg', '')}"
            logging.warning(err_msg)
            raise ZulipException(err_msg)

    def is_channel_exists(self, channel_name: str) -> bool:
        channel_id = self.get_channel_id(channel_name)
        return channel_id > 0

    def subscribe_to_channel(self, channel_name: str) -> int:
        # Create and subscribe to channel.
        # {'result': 'success', 'msg': '', 'subscribed': {'8': ['канал про все']}, 'already_subscribed': {}} - если канал создали
        # {'result': 'success', 'msg': '', 'subscribed': {}, 'already_subscribed': {'8': ['Zulip']}} - если канал уже был
        if not channel_name:
            raise ValueError("Не указано название канала.")

        result = self.client.add_subscriptions(
            streams=[
                {
                    "name": channel_name,
                    "description": "Описание канала",
                },
            ],
        )

        if result["result"] == "success":
            logging.info(f"Пользователь подписан на канал '{channel_name}'")
            return channel_name
        else:
            err_msg = f"Ошибка при подписании на канал '{channel_name}' - {result.get('msg', '')}"
            logging.warning(err_msg)
            raise ZulipException(err_msg)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        client = ZulipClient()
    except ZulipException:
        sys.exit("Фатальная ошибка! Выполнение программы прекращено!")
        
        

    # send_msg_to_channel
    #
    # client.send_msg_to_channel(
    #     "test",
    #     "tg_bot",
    #     "Тестовое сообщение 5"
    # )

    # get_channel_id
    #
    try:
        ch_name = "Zulip"
        print(f"ID of channel '{ch_name}' is: {client.get_channel_id(ch_name)}")
        ch_name = "not_exist"
        print(f"ID of channel '{ch_name}' is: {client.get_channel_id(ch_name)}")
    except ZulipException as e:
        print(e)


    # subscribe_to_channel
    #
    #print(client.subscribe_to_channel("новый"))

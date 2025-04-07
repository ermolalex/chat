import logging
import zulip

from app.config import settings

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
            logging.error(e)

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


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    client = ZulipClient()
    client.send_msg_to_channel(
        "test",
        "tg_bot",
        "Тестовое сообщение 3"
    )


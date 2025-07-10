from app.zulip_client import ZulipClient


def test_create_zulip_client():
    client = ZulipClient()
    assert client.is_active

def test_send_message():
    client = ZulipClient()
    client.send_msg_to_channel(
        "test",
        "tg_bot",
        "Тетовое сообщение"
    )
    assert client.is_active

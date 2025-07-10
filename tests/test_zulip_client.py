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

def test_clean_quote():
    raw_text = """
@_**Александр|8** [писал/а](https://zulip.kik-soft.ru/#narrow/channel/4-.D0.9A.D0.B8.D0.9A-.D1.81.D0.BE.D1.84.D1.82/topic/.D0.90.D0.BB.D0.B5.D0.BA.D1.81.D0.B0.D0.BD.D0.B4.D1.80_542393918/near/50):
```quote
pong
```

ТестТест
"""

    clean_text = f"Вы писали: pong\n\nТестТест"

    assert ZulipClient.clean_quote(raw_text) == clean_text



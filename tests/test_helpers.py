from app.helpers import clean_quote

def test_clean_quote():
    raw_text = """
@_**Александр|8** [писал/а](https://zulip.kik-soft.ru/#narrow/channel/4-.D0.9A.D0.B8.D0.9A-.D1.81.D0.BE.D1.84.D1.82/topic/.D0.90.D0.BB.D0.B5.D0.BA.D1.81.D0.B0.D0.BD.D0.B4.D1.80_542393918/near/50):
```quote
pong
```

ТестТест
"""

    cleaned_text = clean_quote(raw_text)
    exp_text = f"\n>pong\n\nТестТест"

    assert cleaned_text == exp_text



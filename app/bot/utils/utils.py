from aiogram.types import Message
from app.bot.keyboards.kbs import main_keyboard


def get_about_us_text() -> str:
    return """
🌟 ЭЛЕГАНТНАЯ ПАРИКМАХЕРСКАЯ "СТИЛЬ И ШАРМ" 🌟

Добро пожаловать в мир изысканной красоты и непревзойденного стиля!

✨ Наша миссия:
Мы стремимся раскрыть вашу уникальную красоту, подчеркнуть индивидуальность и подарить уверенность в себе.

🎨 Наши услуги:
• Стрижки и укладки для любого типа волос
• Окрашивание и колорирование
• Уходовые процедуры для волос
• Макияж и визаж
• Маникюр и педикюр

👩‍🎨 Наши мастера:
Талантливая команда профессионалов с многолетним опытом и постоянным стремлением к совершенству. Мы следим за последними трендами и используем инновационные техники.

🌿 Наша атмосфера:
Погрузитесь в атмосферу уюта и релаксации. Каждый визит к нам - это не просто процедура, а настоящий ритуал красоты и заботы о себе.

💎 Почему выбирают нас:
• Индивидуальный подход к каждому клиенту
• Использование премиальной косметики
• Гарантия качества и результата
• Уютная и стильная обстановка
• Удобное расположение в центре города

Откройте для себя мир стиля вместе с "СТИЛЬ И ШАРМ"!
Запишитесь на консультацию прямо сейчас и сделайте первый шаг к вашему новому образу.

✨ Ваша красота - наше призвание! ✨
"""


#async def greet_user(message: Message, is_new_user: bool) -> None:
async def greet_user(message: Message, is_new_user: bool = True) -> None:

    """
    Приветствует пользователя и отправляет соответствующее сообщение.
    """
    greeting = "Добро пожаловать" if is_new_user else "С возвращением"
    status = "Вы успешно зарегистрированы!" if is_new_user else "Рады видеть вас снова!"
    await message.answer(
        f"{greeting}, <b>Sasa</b>! {status}\n"
        "Чем я могу помочь вам сегодня?",
        # reply_markup=main_keyboard(user_id=message.from_user.id, first_name=message.from_user.first_name)
    )
    # await message.answer(
    #     f"{greeting}, <b>{message.from_user.full_name}</b>! {status}\n"
    #     "Чем я могу помочь вам сегодня?",
    #     reply_markup=main_keyboard(user_id=message.from_user.id, first_name=message.from_user.first_name)
    # )
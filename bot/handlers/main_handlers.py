from typing import Any
import logging

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.base import StorageKey

from keyboards.main_menu_keyboard import build_main_menu
from main import backend_client

logger = logging.getLogger(__name__)

router = Router()


# Состояния для формы "Написать директору"
class DirectorMessage(StatesGroup):
    waiting_for_message = State()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    user_id: int = message.from_user.id
    logger.info(f"User {user_id} started bot")
    
    try:
        # Получаем профиль из backend
        profile_data: dict[str, Any] = await backend_client.get_profile(user_id)
        
        if profile_data and "full_name" in profile_data:
            welcome_text: str = (
                f"👋 Добро пожаловать, <b>{profile_data['full_name']}</b>!\n\n"
                f"✅ Вы успешно авторизованы в системе KIBERone.\n"
            )
            
            if "group_name" in profile_data:
                welcome_text += f"🏫 Ваша группа: <b>{profile_data['group_name']}</b>\n\n"

            welcome_text += "Выберите нужный раздел:"

            await message.answer(
                welcome_text,
                reply_markup=build_main_menu()
            )
        else:
            await message.answer(
                text="❌ <b>Вы не зарегистрированы в системе</b>\n\n"
                    "Для подключения бота обратитесь к администрации школы.\n"
                    "Сообщите ваш телефон или ID ученика администратору.",
                reply_markup=ReplyKeyboardRemove()
            )
    except PermissionError:
        await message.answer(
            text="❌ <b>Ошибка авторизации</b>\n\n"
                "Пожалуйста, обратитесь к администратору для подключения бота.",
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.answer(
            text="⚠️ <b>Произошла ошибка при подключении к системе</b>\n\n"
                "Попробуйте позже или обратитесь к администратору.",
            reply_markup=ReplyKeyboardRemove()
        )


@router.message(F.text == "Баланс")
async def show_balance(message: Message) -> None:
    user_id: int = message.from_user.id
    logger.info(f"User {user_id} requested balance")
    
    try:
        balance_data: dict[str, Any] = await backend_client.get_balance(user_id)
        
        # Формируем ответ на основе данных из backend
        focus_group= balance_data.get("focus_group", "Основная группа")
        money_balance = balance_data.get("money_balance", 0)
        paid_lessons = balance_data.get("paid_lessons", 0)
        cyberon_balance = balance_data.get("cyberon_balance", 0)

        response_text: str = (
            f"💰 <b>Баланс</b>\n\n"
            f"<b>1. {focus_group}</b>\n"
            f"📊 Баланс: <b>{money_balance} руб.</b>\n"
            f"🎓 Оплаченных занятий: <b>{paid_lessons}</b>\n"
            f"🪙 Баланс киберонов: <b>{cyberon_balance}</b>\n\n"
            f"<i>Данные обновляются автоматически</i>"
        )
        
        await message.answer(response_text)
    except Exception as e:
        logger.error(f"Error showing balance for user {user_id}: {e}")
        await message.answer(
            text="⚠️ <b>Не удалось загрузить данные о балансе</b>\n\n"
                "Попробуйте позже или обратитесь к администратору.",
        )


@router.message(F.text == "Оплата по QR")
async def qr_payment(message: Message) -> None:
    qr_text: str = (
        "💳 <b>Оплата по QR</b>\n\n"
        "🔧 Раздел в разработке. QR-код будет доступен позже.\n\n"
        "Для оплаты вы можете:\n"
        "1. Обратиться к администратору в школе\n"
        "2. Использовать банковский перевод\n"
        "3. Оплатить наличными в офисе\n\n"
        "<i>Онлайн-оплата появится в ближайшее время!</i>"
    )
    await message.answer(qr_text)


@router.message(F.text == "Правила бота")
async def show_bot_rules(message: Message) -> None:
    try:
        rules_data: dict[str, str] = await backend_client.get_bot_rules()
        rules_text: str = rules_data.get("text", "")

        if rules_text:
            response = f"📋 <b>Правила использования бота</b>\n\n{rules_text}"
        else:
            response: str = (
                "ℹ️ <b>Правила использования бота</b>\n\n"
                "1. Бот предназначен только для клиентов KIBERone\n"
                "2. Запрещено спамить и использовать нецензурную лексику\n"
                "3. Конфиденциальные данные не передаются третьим лицам\n"
                "4. Администрация оставляет за собой право блокировки\n\n"
                "<i>Полная версия правил скоро будет доступна</i>"
            )
            
        await message.answer(response)
    except Exception as e:
        logger.error(f"Error showing bot rules: {e}")
        await message.answer(
            text="⚠️ <b>Не удалось загрузить правила бота</b>\n\n"
                "Попробуйте позже.",
        )


@router.message(F.text == "Правила школы")
async def show_school_rules(message: Message) -> None:
    try:
        rules_data: dict[str, str] = await backend_client.get_school_rules()
        rules_text: str = rules_data.get("text", "")
        
        if rules_text:
            response = f"🏫 <b>Правила школы KIBERone</b>\n\n{rules_text}"
        else:
            response: str = (
                "🏫 <b>Правила школы KIBERone</b>\n\n"
                "Основные правила:\n\n"
                "✅ <b>Посещение занятий:</b>\n"
                "• Опоздание не более 15 минут\n"
                "• Предупреждать об отсутствии за 24 часа\n"
                "• Иметь сменную обувь\n\n"
                "✅ <b>Поведение:</b>\n"
                "• Уважительное отношение к преподавателям\n"
                "• Бережное обращение с оборудованием\n"
                "• Соблюдение чистоты в классах\n\n"
                "✅ <b>Оплата:</b>\n"
                "• Оплата до 10 числа каждого месяца\n"
                "• Возврат средств за пропущенные занятия не предусмотрен\n"
                "• Возможна заморозка абонемента по уважительной причине\n\n"
                "<i>Полная версия правил доступна у администратора</i>"
            )
            
        await message.answer(response)
    except Exception as e:
        logger.error(f"Error showing school rules: {e}")
        await message.answer(
            text="⚠️ <b>Не удалось загрузить правила школы</b>\n\n"
                "Попробуйте позже или обратитесь к администратору.",
        )


@router.message(F.text == "Кибероны")
async def show_cyberons(message: Message) -> None:
    cyberons_text: str = """
🪙 <b>Кибероны - внутренняя валюта KIBERone</b>

🎯 <b>Как начисляются кибероны:</b>
• 1 киберон = 1 посещенное занятие
• +5 киберонов за приведенного друга
• +10 киберонов за отличную учебу (оценка 5)
• +15 киберонов за участие в конкурсах
• +20 киберонов за победу в олимпиаде

💰 <b>Как можно потратить кибероны:</b>
• 10 киберонов = 1 дополнительное занятие
• 25 киберонов = мерч KIBERone (футболка)
• 50 киберонов = участие в мастер-классе
• 100 киберонов = скидка 20% на следующий месяц
• 150 киберонов = бесплатный месяц обучения

📜 <b>Основные правила:</b>
1. Кибероны действуют в течение учебного года
2. Не подлежат обмену на денежные средства
3. Накопленные кибероны отображаются в разделе "Баланс"
4. Списываются автоматически при использовании

👨‍💻 <b>Текущий курс:</b>
1 киберон = 50 рублей (номинальная стоимость)

<i>Точные условия начисления и списания уточняйте у администратора школы.</i>
"""
    await message.answer(cyberons_text)


@router.message(F.text == "Финансы")
async def show_finances(message: Message) -> None:
    user_id: int = message.from_user.id
    logger.info(f"User {user_id} requested finance history")

    try:
        finance_data: dict[str, Any] = await backend_client.get_finance_history(user_id)

        focus_group = finance_data.get("focus_group", "Ваша группа")
        transactions = finance_data.get("transactions", [])

        if not transactions:
            response_text: str = (
                f"💰 <b>Финансы: {focus_group}</b>\n\n"
                "📭 История финансов пуста.\n"
                "Данные обновляются раз в 15 минут.\n\n"
                "<i>Здесь будут отображаться все ваши платежи и операции</i>"
            )
        else:
            # Формируем список транзакций
            transactions_text: list[str] = []
            for i, transaction in enumerate(transactions[:10], 1):
                emoji = "📥" if transaction.get("type") == "income" else "📤"
                sign = "+" if transaction.get("type") == "income" else "-"
                amount = transaction.get("amount", 0)
                currency = transaction.get("currency", "руб.")
                date = transaction.get("date", "Неизвестно")
                description = transaction.get("description", "Без описания")

                transactions_text.append(
                    f"{emoji} <b>{date}</b>\n"
                    f"   {sign}{amount} {currency}\n"
                    f"   <i>{description}</i>\n"
                )

            response_text: str = (
                f"💰 <b>Финансы: {focus_group}</b>\n\n" +
                "\n".join(transactions_text) +
                f"\n\n<i>Показано {len(transactions[:10])} из {len(transactions)} операций</i>"
            )
            
        await message.answer(response_text)
    except Exception as e:
        logger.error(f"Error showing finances for user {user_id}: {e}")
        await message.answer(
            text="⚠️ <b>Не удалось загрузить историю финансов</b>\n\n"
                "Попробуйте позже или обратитесь к администратору.",
        )


@router.message(F.text == "Написать директору")
async def start_director_dialog(message: Message, state: FSMContext) -> None:
    await message.answer(
        text="✍️ <b>Написать директору</b>\n\n"
            "Пожалуйста, напишите ваше сообщение для директора школы.\n\n"
            "<b>Что можно написать:</b>\n"
            "• Предложения по улучшению работы школы\n"
            "• Жалобы или замечания\n"
            "• Благодарности преподавателям\n"
            "• Идеи для новых курсов\n\n"
            "<i>Сообщение будет прочитано лично директором.\n"
            "Ответ поступит в течение 24 часов.\n\n"
            "Для отмены отправьте /cancel</i>",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(DirectorMessage.waiting_for_message)


@router.message(DirectorMessage.waiting_for_message)
async def process_director_message(
    message: Message,
    state: FSMContext
) -> None:
    if not message.text or len(message.text.strip()) < 5:
        await message.answer(
            "❌ Сообщение слишком короткое. \
            Пожалуйста, напишите подробнее (минимум 5 символов)."
        )
        return

    user_id: int = message.from_user.id
    user_message: str = message.text.strip()
    
    try:
        # Отправляем сообщение через backend
        success = await backend_client.send_to_director(
            telegram_id=user_id,
            message=user_message
        )

        if success:
            await message.answer(
                text="✅ <b>Сообщение успешно отправлено!</b>\n\n"
                    "Ваше обращение зарегистрировано и будет рассмотрено "
                    "в течение 24 часов.\n\n"
                    "Спасибо за ваше мнение и участие в жизни школы!",
                reply_markup=build_main_menu()
            )
        else:
            await message.answer(
                text="⚠️ <b>Не удалось отправить сообщение</b>\n\n"
                    "Попробуйте позже или обратитесь к администратору лично.",
                reply_markup=build_main_menu()
            )
    except Exception as e:
        logger.error(f"Error sending director message from user {user_id}: {e}")
        await message.answer(
            text="⚠️ <b>Произошла ошибка при отправке сообщения</b>\n\n"
                "Попробуйте позже.",
            reply_markup=build_main_menu()
        )

    await state.clear()


@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    
    if current_state == DirectorMessage.waiting_for_message:
        await message.answer(
            text="❌ Отправка сообщения директору отменена.",
            reply_markup=build_main_menu()
        )
        await state.clear()
    else:
        await message.answer(
            text="Нет активных действий для отмены.",
            reply_markup=build_main_menu()
        )

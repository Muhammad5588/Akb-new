"""
Yordamchi funksiyalar
"""
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database.db_manager import DatabaseManager

db = DatabaseManager()


async def check_user_approved(message: Message, state: FSMContext) -> tuple:
    """
    Foydalanuvchi tasdiqlangan yoki yo'qligini tekshirish

    Args:
        message: Telegram xabari
        state: FSM holati

    Returns:
        tuple: (user, lang, is_approved)
    """
    user = await db.get_user_by_telegram_id(message.from_user.id)

    if not user:
        data = await state.get_data()
        lang = data.get('language', 'uz')
        return None, lang, False

    lang = user['language']
    is_approved = user['verification_status'] == 'approved'

    if not is_approved:
        await message.answer(
            "⚠️ Ushbu funksiyadan foydalanish uchun avval ma'lumotlaringiz tasdiqlanishi kerak!"
            if lang == 'uz' else
            "⚠️ Для использования этой функции сначала подтвердите свои данные!"
        )

    return user, lang, is_approved

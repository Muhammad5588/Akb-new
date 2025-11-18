"""
User Handlers - Foydalanuvchi funksiyalari
"""
import logging
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, FSInputFile

from config import (
    is_admin,
    CHINA_ADDRESS_TEMPLATE,
    CHINA_ADDRESS_TEMPLATE_TEXT,
    FEEDBACK_GROUP_ID
)
from database.db_manager import DatabaseManager
from utils.texts import get_text
from utils.keyboards import (
    main_menu_keyboard,
    back_keyboard,
    yes_no_keyboard,
    feedback_reply_inline_keyboard
)
from utils.formatters import (
    format_phone_display,
    format_verification_status,
    format_datetime
)
from utils.helpers import check_user_approved

logger = logging.getLogger(__name__)
router = Router()
db = DatabaseManager()


# ==================== STATES ====================

class UserStates(StatesGroup):
    viewing_profile = State()
    entering_feedback = State()
    confirming_china_address = State()


# ==================== PROFIL ====================

@router.message(F.text.in_([
    get_text('uz', 'profile'),
    get_text('ru', 'profile')
]))
async def show_profile(message: Message, state: FSMContext):
    """Profilni ko'rsatish"""
    user, lang, is_approved = await check_user_approved(message, state)

    if not user or not is_approved:
        return
    
    profile_text = get_text(
        lang, 'profile_info',
        fullname=user['fullname'],
        client_code=user['client_code'],
        phone=format_phone_display(user['phone']),
        passport=user['passport_number'],
        birth_date=user['birth_date'],
        pinfl=user['pinfl'],
        address=user['address'],
        status=format_verification_status(user['verification_status'], lang),
        registered_at=format_datetime(user['registered_at'])
    )
    
    await message.answer(profile_text)
    
    # Pasport muddati ogohlantiruvi
    if user['passport_expiry_date']:
        from utils.validators import Validators
        from datetime import datetime
        
        try:
            expiry_date = datetime.strptime(user['passport_expiry_date'], '%d.%m.%Y')
            today = datetime.now()
            
            months_until = (expiry_date.year - today.year) * 12 + (expiry_date.month - today.month)
            
            if months_until < 0:
                await message.answer(
                    get_text(lang, 'passport_expired', expiry_date=user['passport_expiry_date'])
                )
            elif months_until <= 6:
                await message.answer(
                    get_text(lang, 'passport_expiry_warning', expiry_date=user['passport_expiry_date'])
                )
        except:
            pass


# ==================== XITOY MANZILI ====================

@router.message(F.text.in_([
    get_text('uz', 'china_address'),
    get_text('ru', 'china_address')
]))
async def show_china_address(message: Message, state: FSMContext):
    """Xitoy sklad manzilini ko'rsatish"""
    user, lang, is_approved = await check_user_approved(message, state)

    if not user or not is_approved:
        return
    
    # Template rasmni yuborish
    if CHINA_ADDRESS_TEMPLATE and os.path.exists(CHINA_ADDRESS_TEMPLATE):
        try:
            caption_text = f"""🇨🇳 Xitoy sklad manzili

收货人：{user['client_code']}
电话:18161955318
西安市 雁塔区 丈八沟街道
高新区丈八六路49号103室中京仓库({user['client_code']})"""

            await message.answer_photo(
                FSInputFile(CHINA_ADDRESS_TEMPLATE),
                caption=caption_text
            )
        except:
            pass

    # Agar tasdiqlagan bo'lsa
    if user['china_address_confirmed']:
        await message.answer(
            "✅ Siz allaqachon manzilni tasdiqlagansiz!"
            if lang == 'uz' else
            "✅ Вы уже подтвердили адрес!"
        )


@router.message(UserStates.confirming_china_address, F.text)
async def confirm_china_address(message: Message, state: FSMContext):
    """Xitoy manzilini tasdiqlash"""
    user = await db.get_user_by_telegram_id(message.from_user.id)
    lang = user['language']
    
    if message.text in ["✅ Ha", "✅ Да"]:
        # Tasdiqlash
        success = await db.confirm_china_address(user['id'])
        
        if success:
            await state.clear()
            await message.answer(
                get_text(lang, 'china_address_confirmed'),
                reply_markup=main_menu_keyboard(lang, is_admin(message.from_user.id))
            )
        else:
            await message.answer(get_text(lang, 'error_general'))
    
    elif message.text in ["❌ Yo'q", "❌ Нет"]:
        await state.clear()
        await message.answer(
            "Qaytadan manzilni diqqat bilan ko'rib chiqing." 
            if lang == 'uz' else 
            "Пожалуйста, внимательно проверьте адрес еще раз.",
            reply_markup=main_menu_keyboard(lang, is_admin(message.from_user.id))
        )
    else:
        await message.answer(
            "Iltimos, quyidagi tugmalardan birini tanlang:" 
            if lang == 'uz' else 
            "Пожалуйста, выберите одну из кнопок:",
            reply_markup=yes_no_keyboard(lang)
        )


# ==================== FEEDBACK ====================

@router.message(F.text.in_([
    get_text('uz', 'feedback'),
    get_text('ru', 'feedback')
]))
async def start_feedback(message: Message, state: FSMContext):
    """Feedback yozishni boshlash"""
    user, lang, is_approved = await check_user_approved(message, state)

    if not user or not is_approved:
        return
    
    await state.set_state(UserStates.entering_feedback)
    await message.answer(
        get_text(lang, 'enter_feedback'),
        reply_markup=back_keyboard(lang)
    )


@router.message(UserStates.entering_feedback, F.text)
async def process_feedback(message: Message, state: FSMContext, bot: Bot):
    """Feedbackni qabul qilish va guruhga yuborish"""
    user = await db.get_user_by_telegram_id(message.from_user.id)
    lang = user['language']
    
    if message.text == get_text(lang, 'back'):
        await state.clear()
        await message.answer(
            get_text(lang, 'back_to_main'),
            reply_markup=main_menu_keyboard(lang, is_admin(message.from_user.id))
        )
        return
    
    # Feedbackni saqlash
    feedback_id = await db.save_feedback(
        user['id'],
        message.from_user.id,
        message.text
    )
    
    if not feedback_id:
        await message.answer(get_text(lang, 'error_general'))
        return
    
    # Feedback guruhga yuborish
    try:
        feedback_text = f"""
💬 YANGI FEEDBACK

👤 {user['fullname']}
🆔 {user['client_code']}
📱 {format_phone_display(user['phone'])}

📝 Xabar:
{message.text}
"""
        
        await bot.send_message(
            FEEDBACK_GROUP_ID,
            feedback_text,
            reply_markup=feedback_reply_inline_keyboard(
                message.from_user.id,
                feedback_id
            )
        )
        
        await state.clear()
        await message.answer(
            get_text(lang, 'feedback_sent'),
            reply_markup=main_menu_keyboard(lang, is_admin(message.from_user.id))
        )
    
    except Exception as e:
        logger.error(f"Send feedback to group error: {e}")
        await message.answer(get_text(lang, 'error_general'))


# ==================== KONTAKTLAR ====================

@router.message(F.text.in_([
    get_text('uz', 'contacts'),
    get_text('ru', 'contacts')
]))
async def show_contacts(message: Message, state: FSMContext):
    """Kontaktlarni ko'rsatish"""
    data = await state.get_data()
    lang = data.get('language', 'uz')
    
    # Agar user registered bo'lsa
    user = await db.get_user_by_telegram_id(message.from_user.id)
    if user:
        lang = user['language']
    
    await message.answer(get_text(lang, 'contact_info'))


# ==================== TIL TANLASH ====================

@router.message(F.text.in_([
    get_text('uz', 'language'),
    get_text('ru', 'language')
]))
async def select_language(message: Message, state: FSMContext):
    """Til tanlash"""
    from utils.keyboards import language_keyboard
    
    await message.answer(
        "Iltimos, tilni tanlang / Пожалуйста, выберите язык:",
        reply_markup=language_keyboard()
    )


@router.message(F.text.in_(["🇺🇿 O'zbek", "🇷🇺 Русский"]))
async def process_language_selection(message: Message, state: FSMContext):
    """Tilni o'rnatish"""
    user = await db.get_user_by_telegram_id(message.from_user.id)
    
    if message.text == "🇺🇿 O'zbek":
        new_lang = 'uz'
    else:
        new_lang = 'ru'
    
    await state.update_data(language=new_lang)
    
    # Database ga saqlash
    if user:
        import aiosqlite
        from config import DB_FILE
        
        async with aiosqlite.connect(DB_FILE) as db_conn:
            await db_conn.execute(
                'UPDATE users SET language = ? WHERE id = ?',
                (new_lang, user['id'])
            )
            await db_conn.commit()
    
    await message.answer(
        get_text(new_lang, f'language_changed_{new_lang}'),
        reply_markup=main_menu_keyboard(new_lang, is_admin(message.from_user.id))
    )


# ==================== LOGOUT ====================

@router.message(F.text.in_([
    get_text('uz', 'logout'),
    get_text('ru', 'logout')
]))
async def logout(message: Message, state: FSMContext):
    """Chiqish"""
    user = await db.get_user_by_telegram_id(message.from_user.id)
    
    if user:
        lang = user['language']
        await message.answer(
            get_text(lang, 'logout_confirm'),
            reply_markup=yes_no_keyboard(lang)
        )
    else:
        await state.clear()
        await message.answer("👋 Xayr!")


@router.message(F.text.in_(["✅ Ha", "✅ Да"]))
async def confirm_logout(message: Message, state: FSMContext):
    """Logout ni tasdiqlash"""
    data = await state.get_data()

    # Faqat logout confirm holatida
    current_state = await state.get_state()
    if current_state:
        return

    lang = data.get('language', 'uz')

    await state.clear()

    from aiogram.types import ReplyKeyboardRemove
    await message.answer(
        get_text(lang, 'logout_success'),
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(F.text.in_(["❌ Yo'q", "❌ Нет"]))
async def cancel_logout(message: Message, state: FSMContext):
    """Logout ni bekor qilish"""
    user = await db.get_user_by_telegram_id(message.from_user.id)

    if user:
        lang = user['language']
    else:
        data = await state.get_data()
        lang = data.get('language', 'uz')

    await state.clear()
    await message.answer(
        get_text(lang, 'back_to_main'),
        reply_markup=main_menu_keyboard(lang, is_admin(message.from_user.id))
    )


# ==================== BEKOR QILISH ====================

@router.message(F.text.in_([get_text('uz', 'cancel'), get_text('ru', 'cancel')]))
async def handle_cancel(message: Message, state: FSMContext):
    """Bekor qilish - har qanday holatdan chiqish"""
    user = await db.get_user_by_telegram_id(message.from_user.id)

    if user:
        lang = user['language']
    else:
        data = await state.get_data()
        lang = data.get('language', 'uz')

    await state.clear()
    await message.answer(
        get_text(lang, 'operation_cancelled'),
        reply_markup=main_menu_keyboard(lang, is_admin(message.from_user.id))
    )


# ==================== ORQAGA ====================

@router.message(F.text.in_([get_text('uz', 'back'), get_text('ru', 'back')]))
async def handle_back(message: Message, state: FSMContext):
    """Orqaga qaytish"""
    user = await db.get_user_by_telegram_id(message.from_user.id)

    if user:
        lang = user['language']
    else:
        data = await state.get_data()
        lang = data.get('language', 'uz')

    await state.clear()
    await message.answer(
        get_text(lang, 'back_to_main'),
        reply_markup=main_menu_keyboard(lang, is_admin(message.from_user.id))
    )


# ==================== IMPORT ====================
import os
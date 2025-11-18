"""
Auth Handlers - Ro'yxatdan o'tish va Login
"""
import os
import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, FSInputFile

from config import (
    is_admin,
    PASSPORT_TEMPLATE,
    PINFL_TEMPLATE,
    PassportType,
    VERIFICATION_GROUP_ID
)
from database.db_manager import DatabaseManager
from utils.validators import Validators
from utils.texts import get_text
from utils.keyboards import (
    welcome_keyboard,
    main_menu_keyboard,
    cancel_keyboard,
    passport_type_keyboard,
    confirm_keyboard,
    verification_inline_keyboard
)
from utils.formatters import format_phone_display, format_verification_status

logger = logging.getLogger(__name__)
router = Router()
db = DatabaseManager()


# ==================== STATES ====================

class RegistrationStates(StatesGroup):
    entering_fullname = State()
    entering_phone = State()
    selecting_passport_type = State()
    uploading_passport_front = State()
    uploading_passport_back = State()
    uploading_passport_booklet = State()
    entering_passport_number = State()
    entering_birth_date = State()
    entering_pinfl = State()
    entering_address = State()
    confirming_registration = State()


class LoginStates(StatesGroup):
    entering_client_code = State()
    entering_phone_verify = State()


# ==================== START ====================

@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    """Start komandasi"""
    await state.clear()
    
    if message.chat.type != "private":
        return
    
    user_id = message.from_user.id
    
    # Admin auto-login
    if is_admin(user_id):
        # Admin uchun alohida handler bor (handlers/admin.py da)
        from handlers.admin import show_admin_panel
        await show_admin_panel(message, state)
        return
    
    # Oddiy foydalanuvchi
    is_registered = await db.is_user_registered(user_id)
    
    if is_registered:
        user = await db.get_user_by_telegram_id(user_id)
        lang = user['language']

        await state.update_data(language=lang, user_id=user['id'])

        # Status xabari
        status_text = format_verification_status(user['verification_status'], lang)

        if user['verification_status'] == 'approved':
            status_msg = get_text(lang, 'status_approved')
            # Faqat tasdiqlangan foydalanuvchilar uchun asosiy menyu
            await message.answer(
                get_text(lang, 'welcome_registered',
                        fullname=user['fullname'],
                        client_code=user['client_code'],
                        phone=user['phone'],
                        status=status_text,
                        status_message=status_msg),
                reply_markup=main_menu_keyboard(lang, is_admin(user_id))
            )
        elif user['verification_status'] == 'rejected':
            status_msg = get_text(lang, 'status_rejected', reason=user['rejection_reason'] or "—")
            # Rad etilgan foydalanuvchilar uchun qayta ro'yxatdan o'tish
            await message.answer(
                get_text(lang, 'welcome_registered',
                        fullname=user['fullname'],
                        client_code=user['client_code'],
                        phone=user['phone'],
                        status=status_text,
                        status_message=status_msg),
                reply_markup=welcome_keyboard(lang)
            )
        else:
            status_msg = get_text(lang, 'status_pending')
            # Kutilayotgan foydalanuvchilar uchun faqat status
            from aiogram.types import ReplyKeyboardRemove
            await message.answer(
                get_text(lang, 'welcome_registered',
                        fullname=user['fullname'],
                        client_code=user['client_code'],
                        phone=user['phone'],
                        status=status_text,
                        status_message=status_msg),
                reply_markup=ReplyKeyboardRemove()
            )
    else:
        # Yangi foydalanuvchi
        data = await state.get_data()
        lang = data.get('language', 'uz')
        
        await message.answer(
            get_text(lang, 'welcome_new'),
            reply_markup=welcome_keyboard(lang)
        )


# ==================== RO'YXATDAN O'TISH ====================

@router.message(F.text.in_([
    get_text('uz', 'register'),
    get_text('ru', 'register')
]))
async def start_registration(message: Message, state: FSMContext):
    """Ro'yxatdan o'tishni boshlash"""
    data = await state.get_data()
    lang = data.get('language', 'uz')
    
    await state.set_state(RegistrationStates.entering_fullname)
    await message.answer(
        get_text(lang, 'enter_fullname'),
        reply_markup=cancel_keyboard(lang)
    )


@router.message(RegistrationStates.entering_fullname, F.text)
async def process_fullname(message: Message, state: FSMContext):
    """F.I.O ni qabul qilish"""
    data = await state.get_data()
    lang = data.get('language', 'uz')
    
    if message.text == get_text(lang, 'cancel'):
        await state.clear()
        await message.answer(
            get_text(lang, 'operation_cancelled'),
            reply_markup=welcome_keyboard(lang)
        )
        return
    
    valid, msg, formatted = Validators.validate_fullname(message.text)
    
    if not valid:
        await message.answer(f"❌ {msg}\n\n{get_text(lang, 'enter_fullname')}")
        return
    
    await state.update_data(fullname=formatted)
    await state.set_state(RegistrationStates.entering_phone)
    
    await message.answer(
        get_text(lang, 'enter_phone'),
        reply_markup=cancel_keyboard(lang)
    )


@router.message(RegistrationStates.entering_phone, F.text)
async def process_phone(message: Message, state: FSMContext):
    """Telefon raqamini qabul qilish"""
    data = await state.get_data()
    lang = data.get('language', 'uz')
    
    if message.text == get_text(lang, 'cancel'):
        await state.clear()
        await message.answer(
            get_text(lang, 'operation_cancelled'),
            reply_markup=welcome_keyboard(lang)
        )
        return
    
    valid, msg, phone = Validators.validate_phone(message.text)
    
    if not valid:
        await message.answer(f"❌ {msg}\n\n{get_text(lang, 'enter_phone')}")
        return
    
    await state.update_data(phone=phone)
    await state.set_state(RegistrationStates.selecting_passport_type)
    
    await message.answer(
        get_text(lang, 'select_passport_type'),
        reply_markup=passport_type_keyboard(lang)
    )


@router.message(RegistrationStates.selecting_passport_type, F.text)
async def process_passport_type(message: Message, state: FSMContext):
    """Pasport turi tanlash"""
    data = await state.get_data()
    lang = data.get('language', 'uz')
    
    if message.text == get_text(lang, 'cancel'):
        await state.clear()
        await message.answer(
            get_text(lang, 'operation_cancelled'),
            reply_markup=welcome_keyboard(lang)
        )
        return
    
    if message.text == get_text(lang, 'passport_id_card'):
        await state.update_data(passport_type=PassportType.ID_CARD)
        await state.set_state(RegistrationStates.uploading_passport_front)
        
        await message.answer(
            get_text(lang, 'upload_passport_front'),
            reply_markup=cancel_keyboard(lang)
        )
    elif message.text == get_text(lang, 'passport_booklet'):
        await state.update_data(passport_type=PassportType.BOOKLET)
        await state.set_state(RegistrationStates.uploading_passport_booklet)
        
        await message.answer(
            get_text(lang, 'upload_passport_booklet'),
            reply_markup=cancel_keyboard(lang)
        )
    else:
        await message.answer(
            get_text(lang, 'invalid_command'),
            reply_markup=passport_type_keyboard(lang)
        )


@router.message(RegistrationStates.uploading_passport_front, F.photo)
async def process_passport_front(message: Message, state: FSMContext):
    """Pasport old tomonini qabul qilish (ID card)"""
    data = await state.get_data()
    lang = data.get('language', 'uz')

    try:
        # Eng katta rasmni olish
        photo = message.photo[-1]

        # File ID va File Unique ID ni saqlash (rasmni yuklamasdan)
        await state.update_data(
            passport_front_file_id=photo.file_id,
            passport_front_file_unique_id=photo.file_unique_id
        )
        await state.set_state(RegistrationStates.uploading_passport_back)

        await message.answer(
            get_text(lang, 'upload_passport_back'),
            reply_markup=cancel_keyboard(lang)
        )
    except Exception as e:
        logger.error(f"Photo upload error: {e}")
        await message.answer(get_text(lang, 'error_photo'))


@router.message(RegistrationStates.uploading_passport_back, F.photo)
async def process_passport_back(message: Message, state: FSMContext):
    """Pasport orqa tomonini qabul qilish (ID card)"""
    data = await state.get_data()
    lang = data.get('language', 'uz')

    try:
        photo = message.photo[-1]

        # File ID va File Unique ID ni saqlash (rasmni yuklamasdan)
        await state.update_data(
            passport_back_file_id=photo.file_id,
            passport_back_file_unique_id=photo.file_unique_id
        )
        await state.set_state(RegistrationStates.entering_passport_number)

        # Template ni yuborish
        await send_passport_template(message, lang)

        await message.answer(
            get_text(lang, 'enter_passport_number'),
            reply_markup=cancel_keyboard(lang)
        )
    except Exception as e:
        logger.error(f"Photo upload error: {e}")
        await message.answer(get_text(lang, 'error_photo'))


@router.message(RegistrationStates.uploading_passport_booklet, F.photo)
async def process_passport_booklet(message: Message, state: FSMContext):
    """Pasport rasmini qabul qilish (Kitobli)"""
    data = await state.get_data()
    lang = data.get('language', 'uz')

    try:
        photo = message.photo[-1]

        # File ID va File Unique ID ni saqlash (kitobli uchun front va back bir xil)
        await state.update_data(
            passport_front_file_id=photo.file_id,
            passport_back_file_id=photo.file_id,
            passport_front_file_unique_id=photo.file_unique_id,
            passport_back_file_unique_id=photo.file_unique_id
        )
        await state.set_state(RegistrationStates.entering_passport_number)

        # Template ni yuborish
        await send_passport_template(message, lang)

        await message.answer(
            get_text(lang, 'enter_passport_number'),
            reply_markup=cancel_keyboard(lang)
        )
    except Exception as e:
        logger.error(f"Photo upload error: {e}")
        await message.answer(get_text(lang, 'error_photo'))


async def send_passport_template(message: Message, lang: str):
    """Pasport template rasmni yuborish"""
    if os.path.exists(PASSPORT_TEMPLATE):
        try:
            await message.answer_photo(
                FSInputFile(PASSPORT_TEMPLATE),
                caption="📸 Pasport seriya va raqami SHU YERDA"
            )
        except:
            pass


# Keyingi qism handlers/auth.py (2/2) da davom etadi...
# handlers/auth.py ga qo'shish (davomi)

@router.message(RegistrationStates.entering_passport_number, F.text)
async def process_passport_number(message: Message, state: FSMContext):
    """Pasport raqamini qabul qilish"""
    data = await state.get_data()
    lang = data.get('language', 'uz')
    
    if message.text == get_text(lang, 'cancel'):
        await state.clear()
        await message.answer(
            get_text(lang, 'operation_cancelled'),
            reply_markup=welcome_keyboard(lang)
        )
        return
    
    valid, msg, passport = Validators.validate_passport_number(message.text)
    
    if not valid:
        await message.answer(f"❌ {msg}")
        return
    
    await state.update_data(passport_number=passport)
    await state.set_state(RegistrationStates.entering_birth_date)
    
    await message.answer(
        get_text(lang, 'enter_birth_date'),
        reply_markup=cancel_keyboard(lang)
    )


@router.message(RegistrationStates.entering_birth_date, F.text)
async def process_birth_date(message: Message, state: FSMContext):
    """Tug'ilgan sanani qabul qilish"""
    data = await state.get_data()
    lang = data.get('language', 'uz')
    
    if message.text == get_text(lang, 'cancel'):
        await state.clear()
        await message.answer(
            get_text(lang, 'operation_cancelled'),
            reply_markup=welcome_keyboard(lang)
        )
        return
    
    valid, msg, birth_date, warning, expiry_date = Validators.validate_birth_date(message.text)
    
    if not valid:
        await message.answer(f"❌ {msg}")
        return
    
    await state.update_data(
        birth_date=birth_date,
        passport_expiry_date=expiry_date
    )
    
    # Pasport muddati ogohlantiruvi
    if warning:
        await message.answer(warning)
    
    await state.set_state(RegistrationStates.entering_pinfl)
    
    # PINFL template
    if os.path.exists(PINFL_TEMPLATE):
        try:
            await message.answer_photo(
                FSInputFile(PINFL_TEMPLATE),
                caption="📸 PINFL SHU YERDA"
            )
        except:
            pass
    
    await message.answer(
        get_text(lang, 'enter_pinfl'),
        reply_markup=cancel_keyboard(lang)
    )


@router.message(RegistrationStates.entering_pinfl, F.text)
async def process_pinfl(message: Message, state: FSMContext):
    """PINFL ni qabul qilish"""
    data = await state.get_data()
    lang = data.get('language', 'uz')
    
    if message.text == get_text(lang, 'cancel'):
        await state.clear()
        await message.answer(
            get_text(lang, 'operation_cancelled'),
            reply_markup=welcome_keyboard(lang)
        )
        return
    
    valid, msg, pinfl = Validators.validate_pinfl(message.text)
    
    if not valid:
        await message.answer(f"❌ {msg}")
        return
    
    await state.update_data(pinfl=pinfl)
    await state.set_state(RegistrationStates.entering_address)
    
    await message.answer(
        get_text(lang, 'enter_address'),
        reply_markup=cancel_keyboard(lang)
    )


@router.message(RegistrationStates.entering_address, F.text)
async def process_address(message: Message, state: FSMContext):
    """Manzilni qabul qilish"""
    data = await state.get_data()
    lang = data.get('language', 'uz')
    
    if message.text == get_text(lang, 'cancel'):
        await state.clear()
        await message.answer(
            get_text(lang, 'operation_cancelled'),
            reply_markup=welcome_keyboard(lang)
        )
        return
    
    valid, msg, address = Validators.validate_address(message.text)
    
    if not valid:
        await message.answer(f"❌ {msg}")
        return
    
    await state.update_data(address=address)
    await state.set_state(RegistrationStates.confirming_registration)
    
    # Ma'lumotlarni ko'rsatish
    data = await state.get_data()
    
    await message.answer(
        get_text(lang, 'confirm_registration',
                fullname=data['fullname'],
                phone=format_phone_display(data['phone']),
                passport=data['passport_number'],
                birth_date=data['birth_date'],
                pinfl=data['pinfl'],
                address=data['address']),
        reply_markup=confirm_keyboard(lang)
    )


@router.message(RegistrationStates.confirming_registration, F.text)
async def confirm_registration(message: Message, state: FSMContext, bot: Bot):
    """Ro'yxatdan o'tishni tasdiqlash"""
    data = await state.get_data()
    lang = data.get('language', 'uz')
    
    if message.text == get_text(lang, 'confirm'):
        import asyncio

        # Foydalanuvchini saqlash
        success, msg, client_code = await db.register_user(message.from_user.id, data)

        if success:
            # User ni olish
            user = await db.get_user_by_telegram_id(message.from_user.id)

            # Verification guruhga yuborishni background taskda ishlatish
            asyncio.create_task(send_to_verification_group(bot, user, data))

            await state.clear()
            await message.answer(
                get_text(lang, 'registration_submitted'),
                reply_markup=main_menu_keyboard(lang)
            )
        else:
            await message.answer(f"❌ Xatolik: {msg}")
    
    elif message.text == get_text(lang, 'cancel'):
        await state.clear()
        await message.answer(
            get_text(lang, 'operation_cancelled'),
            reply_markup=welcome_keyboard(lang)
        )


async def send_to_verification_group(bot: Bot, user: dict, data: dict):
    """Ma'lumotlarni verification guruhga yuborish"""
    import asyncio

    try:
        # Matn
        text = f"""
🆕 YANGI RO'YXATDAN O'TUVCHI

👤 F.I.O: {user['fullname']}
📱 Telefon: {format_phone_display(user['phone'])}
🆔 Pasport: {user['passport_number']}
📅 Tug'ilgan: {user['birth_date']}
🔢 PINFL: {user['pinfl']}
📍 Manzil: {user['address']}

🔐 Mijoz kodi: {user['client_code']}
📅 Ro'yxat: {user['registered_at']}
"""

        # Async tasklar ro'yxati
        tasks = []

        # Pasport rasmlarini yuborish (file_id orqali)
        if data.get('passport_front_file_id'):
            tasks.append(
                bot.send_photo(
                    VERIFICATION_GROUP_ID,
                    data['passport_front_file_id'],
                    caption="📸 Pasport (OLD)"
                )
            )

        if data.get('passport_back_file_id') and data['passport_back_file_id'] != data.get('passport_front_file_id'):
            tasks.append(
                bot.send_photo(
                    VERIFICATION_GROUP_ID,
                    data['passport_back_file_id'],
                    caption="📸 Pasport (ORQA)"
                )
            )

        # Rasmlarni parallel yuborish
        if tasks:
            await asyncio.gather(*tasks)

        # Xabarni yuborish
        msg = await bot.send_message(
            VERIFICATION_GROUP_ID,
            text,
            reply_markup=verification_inline_keyboard(user['id'], 'uz')
        )

        # Verification queue ga qo'shish
        await db.add_to_verification_queue(user['id'], msg.message_id)

    except Exception as e:
        logger.error(f"Send to verification group error: {e}")


# ==================== LOGIN ====================

@router.message(F.text.in_([
    get_text('uz', 'login'),
    get_text('ru', 'login')
]))
async def start_login(message: Message, state: FSMContext):
    """Loginni boshlash"""
    data = await state.get_data()
    lang = data.get('language', 'uz')
    
    await state.set_state(LoginStates.entering_client_code)
    await message.answer(
        get_text(lang, 'enter_client_code'),
        reply_markup=cancel_keyboard(lang)
    )


@router.message(LoginStates.entering_client_code, F.text)
async def process_client_code(message: Message, state: FSMContext):
    """Mijoz kodini qabul qilish"""
    data = await state.get_data()
    lang = data.get('language', 'uz')
    
    if message.text == get_text(lang, 'cancel'):
        await state.clear()
        await message.answer(
            get_text(lang, 'operation_cancelled'),
            reply_markup=welcome_keyboard(lang)
        )
        return
    
    await state.update_data(temp_client_code=message.text.strip().upper())
    await state.set_state(LoginStates.entering_phone_verify)
    
    await message.answer(
        get_text(lang, 'enter_phone_verify'),
        reply_markup=cancel_keyboard(lang)
    )


@router.message(LoginStates.entering_phone_verify, F.text)
async def process_phone_verify(message: Message, state: FSMContext):
    """Telefon raqamini tekshirish va login"""
    data = await state.get_data()
    lang = data.get('language', 'uz')
    
    if message.text == get_text(lang, 'cancel'):
        await state.clear()
        await message.answer(
            get_text(lang, 'operation_cancelled'),
            reply_markup=welcome_keyboard(lang)
        )
        return
    
    client_code = data['temp_client_code']
    user = await db.verify_login(client_code, message.text)
    
    if user:
        await state.clear()
        await state.update_data(language=user['language'], user_id=user['id'])
        
        await message.answer(
            get_text(user['language'], 'login_success', fullname=user['fullname']),
            reply_markup=main_menu_keyboard(user['language'], is_admin(message.from_user.id))
        )
    else:
        await message.answer(get_text(lang, 'login_failed'))
        await state.clear()
        await message.answer(
            get_text(lang, 'welcome_new'),
            reply_markup=welcome_keyboard(lang)
        )
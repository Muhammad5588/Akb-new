"""
Barcha klaviaturalar
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from utils.texts import get_text


# ==================== ASOSIY KLAVIATURALAR ====================

def welcome_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    """Boshlang'ich klaviatura (ro'yxat/login)"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, 'register'))],
            [KeyboardButton(text=get_text(lang, 'login'))]
        ],
        resize_keyboard=True
    )


def main_menu_keyboard(lang: str = 'uz', is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Asosiy menyu"""
    buttons = [
        [KeyboardButton(text=get_text(lang, 'search'))],
        [KeyboardButton(text=get_text(lang, 'profile')), KeyboardButton(text=get_text(lang, 'china_address'))],
        [KeyboardButton(text=get_text(lang, 'feedback')), KeyboardButton(text=get_text(lang, 'contacts'))],
        [KeyboardButton(text=get_text(lang, 'language')), KeyboardButton(text=get_text(lang, 'logout'))]
    ]
    
    if is_admin:
        buttons.insert(0, [KeyboardButton(text=get_text(lang, 'admin_panel'))])
    
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def admin_menu_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    """Admin panel menyu"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, 'manage_users'))],
            [KeyboardButton(text=get_text(lang, 'search_user'))],
            [KeyboardButton(text=get_text(lang, 'upload_db'))],
            [KeyboardButton(text=get_text(lang, 'broadcast'))],
            [KeyboardButton(text=get_text(lang, 'admin_search'))],
            [KeyboardButton(text=get_text(lang, 'back'))]
        ],
        resize_keyboard=True
    )


# ==================== YORDAMCHI KLAVIATURALAR ====================

def cancel_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    """Bekor qilish"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=get_text(lang, 'cancel'))]],
        resize_keyboard=True
    )


def back_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    """Orqaga qaytish"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=get_text(lang, 'back'))]],
        resize_keyboard=True
    )


def confirm_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    """Tasdiqlash klaviaturasi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, 'confirm'))],
            [KeyboardButton(text=get_text(lang, 'cancel'))]
        ],
        resize_keyboard=True
    )


def yes_no_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    """Ha/Yo'q"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Ha" if lang == 'uz' else "✅ Да")],
            [KeyboardButton(text="❌ Yo'q" if lang == 'uz' else "❌ Нет")]
        ],
        resize_keyboard=True
    )


# ==================== RO'YXATDAN O'TISH ====================

def passport_type_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    """Pasport turi tanlash"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, 'passport_id_card'))],
            [KeyboardButton(text=get_text(lang, 'passport_booklet'))],
            [KeyboardButton(text=get_text(lang, 'cancel'))]
        ],
        resize_keyboard=True
    )


# ==================== QIDIRUV ====================

def search_type_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    """Qidiruv turi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, 'by_trek'))],
            [KeyboardButton(text=get_text(lang, 'by_my_code'))],
            [KeyboardButton(text=get_text(lang, 'back'))]
        ],
        resize_keyboard=True
    )


# ==================== TIL TANLASH ====================

def language_keyboard() -> ReplyKeyboardMarkup:
    """Til tanlash"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🇺🇿 O'zbek"),
                KeyboardButton(text="🇷🇺 Русский")
            ],
            [KeyboardButton(text=get_text('uz', 'back'))]
        ],
        resize_keyboard=True
    )


# ==================== INLINE KLAVIATURALAR ====================

def verification_inline_keyboard(user_id: int, lang: str = 'uz') -> InlineKeyboardMarkup:
    """Tasdiq uchun inline klaviatura (admin uchun)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text(lang, 'approve_user'),
                callback_data=f"approve:{user_id}"
            ),
            InlineKeyboardButton(
                text=get_text(lang, 'reject_user'),
                callback_data=f"reject:{user_id}"
            )
        ]
    ])


def user_management_inline_keyboard(user_id: int, lang: str = 'uz') -> InlineKeyboardMarkup:
    """Foydalanuvchini boshqarish (admin)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text(lang, 'edit_user'),
                callback_data=f"edit:{user_id}"
            ),
            InlineKeyboardButton(
                text=get_text(lang, 'delete_user'),
                callback_data=f"delete:{user_id}"
            )
        ]
    ])


def broadcast_confirm_inline_keyboard(lang: str = 'uz') -> InlineKeyboardMarkup:
    """Broadcast tasdiqlash"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Yuborish" if lang == 'uz' else "✅ Отправить",
                callback_data="broadcast:confirm"
            ),
            InlineKeyboardButton(
                text="❌ Bekor qilish" if lang == 'uz' else "❌ Отмена",
                callback_data="broadcast:cancel"
            )
        ]
    ])


def feedback_reply_inline_keyboard(user_telegram_id: int, feedback_id: int) -> InlineKeyboardMarkup:
    """Feedback ga javob berish (admin uchun)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💬 Javob berish / Ответить",
                callback_data=f"feedback_reply:{user_telegram_id}:{feedback_id}"
            )
        ]
    ])

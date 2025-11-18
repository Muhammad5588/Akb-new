"""
Button Matcher - Tugma matnlarini to'g'ri aniqlash
"""

def matches_button(text: str, button_keywords: list) -> bool:
    """
    Tugma matni berilgan keywords bilan mos kelishini tekshirish
    
    Args:
        text: Xabar matni
        button_keywords: Kalit so'zlar ro'yxati
        
    Returns:
        True agar mos kelsa
    """
    if not text:
        return False
    
    text_lower = text.lower().strip()
    
    for keyword in button_keywords:
        if keyword.lower() in text_lower:
            return True
    
    return False


# Tugma identifikatorlari
BUTTON_PATTERNS = {
    'profile': ['👤', 'профиль', 'profilim', 'profil'],
    'china_address': ['🇨🇳', 'xitoy', 'китае', 'адрес'],
    'feedback': ['💬', 'izoh', 'отзыв', 'feedback'],
    'contacts': ['📍', 'aloqa', 'контакт', 'manzil', 'адрес'],
    'language': ['🌐', 'til', 'язык', 'language'],
    'logout': ['🚪', 'chiqish', 'выход', 'logout'],
    'back': ['⬅️', 'orqaga', 'назад', 'back'],
    'search': ['🔍', 'qidirish', 'поиск', 'search'],
    'admin_panel': ['⚙️', 'admin', 'админ', 'panel'],
    'manage_users': ['👥', 'foydalanuvchi', 'пользовател'],
    'broadcast': ['📢', 'xabar', 'рассылка', 'yuborish'],
    'upload_db': ['📂', 'database', 'базу', 'yuklash'],
    'admin_search': ['🔎', 'trek qidirish'],
    'by_trek': ['🔢', 'trek kod'],
    'by_my_code': ['🆔', 'mening yuk'],
}


def identify_button(text: str) -> str:
    """
    Tugma turini aniqlash
    
    Returns:
        Button type yoki None
    """
    for button_type, patterns in BUTTON_PATTERNS.items():
        if matches_button(text, patterns):
            return button_type
    
    return None
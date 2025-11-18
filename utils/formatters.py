"""
Matnlarni formatlash funksiyalari
"""
import re
from datetime import datetime
from typing import Optional


def format_phone_display(phone: str) -> str:
    """
    Telefon raqamini chiroyli formatda ko'rsatish
    998901234567 -> +998 90 123 45 67
    """
    if not phone:
        return ""
    
    # Faqat raqamlar (+ ni olib tashlash)
    digits = re.sub(r'\D', '', phone)
    
    # Agar 998 bilan boshlanmasa
    if not digits.startswith('998'):
        if len(digits) == 9:
            digits = '998' + digits
    
    # Format: +998 XX XXX XX XX
    if len(digits) == 12 and digits.startswith('998'):
        return f"+998 {digits[3:5]} {digits[5:8]} {digits[8:10]} {digits[10:12]}"
    elif len(digits) >= 9:
        # Agar boshqa format bo'lsa
        return f"+{digits}"
    
    return phone


def format_client_code_display(code: str) -> str:
    """Client code ni formatlash"""
    return code.upper() if code else ""


def format_datetime(dt_str: Optional[str], format_type: str = 'full') -> str:
    """
    Datetime ni formatlash
    
    Args:
        dt_str: Datetime string
        format_type: 'full', 'date', 'time'
    """
    if not dt_str:
        return "—"
    
    try:
        dt = datetime.fromisoformat(dt_str)
        
        if format_type == 'date':
            return dt.strftime('%d.%m.%Y')
        elif format_type == 'time':
            return dt.strftime('%H:%M')
        else:  # full
            return dt.strftime('%d.%m.%Y %H:%M')
    except:
        return dt_str


def format_verification_status(status: str, lang: str = 'uz') -> str:
    """Verification statusni formatlash"""
    status_map = {
        'uz': {
            'pending': '⏳ Kutilmoqda',
            'approved': '✅ Tasdiqlangan',
            'rejected': '❌ Rad etilgan'
        },
        'ru': {
            'pending': '⏳ На рассмотрении',
            'approved': '✅ Подтверждено',
            'rejected': '❌ Отклонено'
        }
    }
    
    return status_map.get(lang, status_map['uz']).get(status, status)


def truncate_text(text: str, max_length: int = 100) -> str:
    """Matnni qisqartirish"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def format_weight(weight: float) -> str:
    """Vaznni formatlash"""
    if weight == int(weight):
        return f"{int(weight)}"
    return f"{weight:.2f}"
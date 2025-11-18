"""
Validatorlar - Ma'lumotlarni tekshirish
"""
import re
from datetime import datetime, timedelta
from typing import Tuple, Optional
from config import (
    VALID_PASSPORT_PREFIXES, 
    VALID_KARAKALPAK_PREFIX,
    VALID_PINFL_FIRST_DIGITS,
    PASSPORT_EXPIRY_WARNING_MONTHS
)


class Validators:
    """Ma'lumotlarni tekshirish klassi"""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str, str]:
        """
        Telefon raqamini tekshirish va normalize qilish
        
        Returns:
            (valid, message, normalized_phone)
        """
        # Faqat raqamlarni olish
        digits = re.sub(r'\D', '', phone)
        
        if not digits:
            return False, "Telefon raqam kiritilmadi", ""
        
        # Agar 998 bilan boshlanmasa, qo'shish
        if not digits.startswith('998'):
            if len(digits) == 9:
                digits = '998' + digits
            else:
                return False, "Telefon raqam noto'g'ri formatda", ""
        
        if len(digits) != 12:
            return False, "Telefon raqam 12 ta raqamdan iborat bo'lishi kerak", ""
        
        return True, "OK", digits
    
    @staticmethod
    def validate_passport_number(passport: str) -> Tuple[bool, str, str]:
        """
        Pasport raqamini tekshirish
        
        Returns:
            (valid, message, clean_passport)
        """
        # Bo'sh joylarni olib tashlash
        clean = passport.replace(' ', '').replace('-', '').upper()
        
        # Format: 2 harf + 7 raqam
        if len(clean) != 9:
            return False, (
                "Pasport raqami 9 ta belgidan iborat bo'lishi kerak!\n"
                "To'g'ri format: AA1234567"
            ), ""
        
        # Harflarni tekshirish
        letters = clean[:2]
        
        # O'zbekiston pasportlari
        if letters in VALID_PASSPORT_PREFIXES:
            pass  # Valid
        # Qoraqalpog'iston pasportlari (K bilan boshlanuvchi)
        elif letters[0] == VALID_KARAKALPAK_PREFIX and letters[1].isalpha():
            pass  # Valid
        else:
            return False, (
                f"Pasport raqami noto'g'ri!\n\n"
                f"Qabul qilinadigan harflar:\n"
                f"• {', '.join(VALID_PASSPORT_PREFIXES)} (O'zbekiston)\n"
                f"• K bilan boshlanuvchi (Qoraqalpog'iston)\n\n"
                f"Siz kiritdingiz: {letters}"
            ), ""
        
        # Raqamlarni tekshirish
        numbers = clean[2:]
        if not numbers.isdigit():
            return False, "Pasport raqami oxirgi 7 belgisi raqam bo'lishi kerak", ""
        
        return True, "OK", clean
    
    @staticmethod
    def validate_birth_date(date_str: str) -> Tuple[bool, str, str, Optional[str], Optional[str]]:
        """
        Tug'ilgan sanani tekshirish va pasport muddatini hisoblash
        
        Returns:
            (valid, message, formatted_date, warning, expiry_date)
        """
        # Har xil formatlarni qo'llab-quvvatlash
        patterns = [
            r'(\d{1,2})[./-](\d{1,2})[./-](\d{4})',  # dd.mm.yyyy, dd/mm/yyyy, dd-mm-yyyy
            r'(\d{4})[./-](\d{1,2})[./-](\d{1,2})',  # yyyy.mm.dd
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_str)
            if match:
                parts = match.groups()
                
                try:
                    if len(parts[0]) == 4:  # yyyy-mm-dd format
                        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    else:  # dd-mm-yyyy format
                        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                    
                    # Sana validatsiyasi
                    birth_date = datetime(year, month, day)
                    
                    # Yoshni tekshirish (18+ bo'lishi kerak)
                    today = datetime.now()
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    
                    if age < 18:
                        return False, "Siz 18 yoshdan kichik bo'la olmaysiz", "", None, None
                    
                    if age > 100:
                        return False, "Tug'ilgan sana noto'g'ri", "", None, None
                    
                    formatted_date = birth_date.strftime('%d.%m.%Y')
                    
                    # Pasport muddatini hisoblash
                    expiry_date, warning = Validators._calculate_passport_expiry(birth_date, age)
                    
                    return True, "OK", formatted_date, warning, expiry_date
                
                except ValueError:
                    continue
        
        return False, (
            "Sana formati noto'g'ri!\n"
            "To'g'ri format: dd.mm.yyyy (masalan: 15.03.1990)"
        ), "", None, None
    
    @staticmethod
    def _calculate_passport_expiry(birth_date: datetime, age: int) -> Tuple[Optional[str], Optional[str]]:
        """
        Pasport muddatini hisoblash
        
        O'zbekistonda pasport muddati:
        - 16 yoshgacha: Farzandlik guvohnomasi
        - 16 yoshda: Birinchi pasport (9 yil)
        - 25 yoshda: Ikkinchi pasport (20 yil)
        - 45 yoshda: Uchinchi pasport (umrbod)
        
        Returns:
            (expiry_date_str, warning)
        """
        today = datetime.now()
        
        if age < 25:
            # 16 yoshda olingan pasport 25 yoshda tugaydi
            expiry_age = 25
            expiry_date = datetime(birth_date.year + expiry_age, birth_date.month, birth_date.day)
        elif age < 45:
            # 25 yoshda olingan pasport 45 yoshda tugaydi
            expiry_age = 45
            expiry_date = datetime(birth_date.year + expiry_age, birth_date.month, birth_date.day)
        else:
            # 45 yoshdan keyin umrbod pasport
            return None, None
        
        expiry_str = expiry_date.strftime('%d.%m.%Y')
        
        # Muddati tugashiga necha oy qolganini hisoblash
        months_until_expiry = (expiry_date.year - today.year) * 12 + (expiry_date.month - today.month)
        
        warning = None
        
        if months_until_expiry < 0:
            warning = (
                "🚨 MUHIM OGOHLANTIRISH!\n\n"
                f"Pasportingiz muddati {expiry_str} da tugagan!\n"
                "Yangi pasport olishingiz SHART!\n\n"
                "Muddati tugagan pasport bilan xizmatlardan foydalana olmaysiz."
            )
        elif months_until_expiry <= PASSPORT_EXPIRY_WARNING_MONTHS:
            warning = (
                "⚠️ ESLATMA!\n\n"
                f"Pasportingiz muddati tez orada tugaydi: {expiry_str}\n"
                f"Yangi pasport olishga tayyorgarlik ko'ring.\n\n"
                f"Qolgan vaqt: {months_until_expiry} oy"
            )
        
        return expiry_str, warning
    
    @staticmethod
    def validate_pinfl(pinfl: str) -> Tuple[bool, str, str]:
        """
        PINFL ni tekshirish
        
        Returns:
            (valid, message, clean_pinfl)
        """
        digits = re.sub(r'\D', '', pinfl)
        
        if len(digits) != 14:
            return False, "PINFL 14 ta raqamdan iborat bo'lishi kerak", ""
        
        # Birinchi raqam 3, 4, 5, 6 dan boshlanishi kerak
        if digits[0] not in VALID_PINFL_FIRST_DIGITS:
            return False, (
                f"PINFL birinchi raqami {', '.join(VALID_PINFL_FIRST_DIGITS)} dan biri bo'lishi kerak\n"
                f"Siz kiritdingiz: {digits[0]}"
            ), ""
        
        return True, "OK", digits
    
    @staticmethod
    def validate_fullname(fullname: str) -> Tuple[bool, str, str]:
        """
        Ism-familiyani tekshirish va formatlash
        
        Returns:
            (valid, message, formatted_name)
        """
        # Bo'sh joylarni tozalash
        name = ' '.join(fullname.strip().split())
        
        if len(name) < 5:
            return False, "Ism va familiyani to'liq kiriting (kamida 5 ta belgi)", ""
        
        # Har bir so'zning birinchi harfini katta qilish
        formatted = ' '.join(word.capitalize() for word in name.split())
        
        return True, "OK", formatted
    
    @staticmethod
    def validate_address(address: str) -> Tuple[bool, str, str]:
        """
        Manzilni tekshirish
        
        Returns:
            (valid, message, clean_address)
        """
        clean = address.strip()
        
        if len(clean) < 10:
            return False, "Manzilni to'liqroq kiriting (kamida 10 ta belgi)", ""
        
        return True, "OK", clean
"""
Excel fayldan foydalanuvchilarni import qilish va validatsiya
"""
import re
import pandas as pd
import logging
from typing import Tuple, List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class ExcelUserImporter:
    """Excel fayldan foydalanuvchilarni import qilish"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def validate_passport_series(self, series) -> Tuple[bool, str]:
        """
        Passport seriyasini tekshirish
        O'zbekiston passporti: 2 ta harf + raqamlar (masalan: AA1234567)
        """
        if series is None or pd.isna(series):
            return False, ""
        
        # Excel'dan float kelishi mumkin (masalan: 1234567.0)
        # Lekin bizga harf kerak, shuning uchun to'g'ridan-to'g'ri string qilamiz
        series_str = str(series).strip().upper()
        
        # .0 ni olib tashlash (agar raqam sifatida kelgan bo'lsa)
        series_str = series_str.replace('.0', '')
        
        # Kamida 2 ta belgi bo'lishi kerak
        if len(series_str) < 2:
            return False, ""
        
        # Birinchi 2 ta belgi harf bo'lishi kerak
        if not series_str[:2].isalpha():
            return False, ""
        
        return True, series_str
    
    def validate_phone_number(self, phone: str) -> Tuple[bool, str]:
        """
        Telefon raqamni tekshirish va formatlash
        To'g'ri formatlar: +998901234567, 998901234567, 901234567
        """
        if not phone or pd.isna(phone):
            return False, ""
        
        # Barcha bo'sh joylar va maxsus belgilarni olib tashlash
        phone_str = str(phone).strip()
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone_str)
        
        # + belgisini olib tashlash
        if clean_phone.startswith('+'):
            clean_phone = clean_phone[1:]
        
        # 998 bilan boshlanmasa, qo'shish
        if not clean_phone.startswith('998'):
            # Agar 9 ta raqam bo'lsa (901234567)
            if len(clean_phone) == 9 and clean_phone[0] == '9':
                clean_phone = '998' + clean_phone
            else:
                return False, ""
        
        # Endi 998 + 9 ta raqam = 12 ta raqam bo'lishi kerak
        if len(clean_phone) != 12:
            return False, ""
        
        # Faqat raqamlardan iborat ekanligini tekshirish
        if not clean_phone.isdigit():
            return False, ""
        
        # 998 dan keyin 9 bilan boshlanishini tekshirish
        if clean_phone[3] != '9':
            return False, ""
        
        # + belgisi bilan qaytarish
        return True, '+' + clean_phone
    
    def validate_pinfl(self, pinfl) -> Tuple[bool, str]:
        """
        PINFL raqamini tekshirish
        - 14 ta raqam bo'lishi kerak
        - 3-6 raqamlar [3, 4, 5, 6] dan biri bilan boshlanishi kerak
        """
        if pinfl is None or pd.isna(pinfl):
            logger.debug(f"PINFL None yoki NaN: {pinfl}")
            return False, ""
        
        # String ga o'tkazish
        pinfl_str = str(pinfl).strip()
        
        # 'nan' yoki bo'sh string tekshirish
        if pinfl_str.lower() == 'nan' or not pinfl_str:
            logger.debug(f"PINFL bo'sh yoki nan: {pinfl_str}")
            return False, ""
        
        # Agar nuqta bo'lsa (float formatda kelgan bo'lsa)
        if '.' in pinfl_str:
            try:
                # Float ga o'tkazib, keyin int ga
                pinfl_float = float(pinfl_str)
                pinfl_str = str(int(pinfl_float))
                logger.debug(f"PINFL float dan int ga: {pinfl} -> {pinfl_str}")
            except:
                logger.debug(f"PINFL konvertatsiya xatosi: {pinfl_str}")
                return False, ""
        
        # Bo'sh joy va boshqa belgilarni olib tashlash
        pinfl_str = pinfl_str.replace(' ', '').replace('-', '')
        
        # Faqat raqamlar ekanligini tekshirish
        if not pinfl_str.isdigit():
            logger.debug(f"PINFL faqat raqamlardan emas: {pinfl_str}")
            return False, ""
        
        # 14 ta raqam bo'lishi kerak
        if len(pinfl_str) != 14:
            logger.debug(f"PINFL uzunligi noto'g'ri: {len(pinfl_str)} (kerak: 14), qiymat: {pinfl_str}")
            return False, ""
        
        # 3-raqam (0-indexda 2) [3, 4, 5, 6] dan biri bo'lishi kerak
        third_char = pinfl_str[2]
        if third_char not in ['3', '4', '5', '6']:
            logger.debug(f"PINFL 3-raqami noto'g'ri: {third_char} (kerak: 3,4,5,6), to'liq: {pinfl_str}")
            return False, ""
        
        logger.debug(f"PINFL to'g'ri: {pinfl_str}")
        return True, pinfl_str
    
    async def import_users_from_excel(
        self, 
        file_path: str
    ) -> Tuple[int, int, str]:
        """
        Excel fayldan foydalanuvchilarni import qilish
        
        Returns:
            (success_count, failed_count, failed_excel_path)
        """
        try:
            # Excel faylni o'qish
            df = pd.read_excel(file_path)
            
            # Kerakli ustunlarni tekshirish
            required_columns = [
                'code_str',
                'fullname_passport',
                'passport_series',
                'birth_date',
                'address_region',
                'phone_number',
                'passport_pinfl'
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                error_msg = f"Kerakli ustunlar topilmadi: {', '.join(missing_columns)}"
                logger.error(error_msg)
                return 0, 0, ""
            
            success_count = 0
            failed_rows = []
            
            # Har bir qatorni tekshirish va import qilish
            for index, row in df.iterrows():
                try:
                    # 1. code_str - bo'sh joylarni olib tashlash
                    code_str = str(row['code_str']).strip() if pd.notna(row['code_str']) else ""
                    code_str = code_str.replace(' ', '')
                    
                    if not code_str:
                        logger.warning(f"Row {index + 2}: code_str bo'sh")
                        failed_rows.append(row)
                        continue
                    
                    # 2. fullname_passport - hech qanday tekshiruvsiz
                    fullname = str(row['fullname_passport']).strip() if pd.notna(row['fullname_passport']) else ""
                    
                    if not fullname:
                        logger.warning(f"Row {index + 2}: fullname bo'sh")
                        failed_rows.append(row)
                        continue
                    
                    # 3. passport_series - validatsiya
                    series_valid, passport_series = self.validate_passport_series(row['passport_series'])
                    if not series_valid:
                        logger.warning(f"Row {index + 2}: Passport series noto'g'ri: {row['passport_series']}")
                        failed_rows.append(row)
                        continue
                    
                    # 4. birth_date - hech qanday tekshiruvsiz
                    birth_date = str(row['birth_date']).strip() if pd.notna(row['birth_date']) else ""
                    
                    # 5. address_region - hech qanday tekshiruvsiz
                    address_region = str(row['address_region']).strip() if pd.notna(row['address_region']) else ""
                    
                    # 6. phone_number - validatsiya va formatlash
                    phone_valid, phone_formatted = self.validate_phone_number(row['phone_number'])
                    if not phone_valid:
                        logger.warning(f"Row {index + 2}: Telefon raqam noto'g'ri: {row['phone_number']}")
                        failed_rows.append(row)
                        continue
                    
                    # 7. passport_pinfl - validatsiya
                    pinfl_valid, pinfl = self.validate_pinfl(row['passport_pinfl'])
                    if not pinfl_valid:
                        logger.warning(f"Row {index + 2}: PINFL noto'g'ri: {row['passport_pinfl']}")
                        failed_rows.append(row)
                        continue
                    
                    # Ma'lumotlarni bazaga yozish
                    user_data = {
                        'client_code': code_str,
                        'fullname': fullname,
                        'passport_number': passport_series,
                        'birth_date': birth_date,
                        'address': address_region,
                        'phone': phone_formatted,
                        'pinfl': pinfl,
                        'verification_status': 'approved',  # Import qilinganlar avtomatik tasdiqlangan
                        'language': 'uz'
                    }
                    
                    # Bazaga qo'shish
                    success = await self._insert_user_from_excel(user_data)
                    
                    if success:
                        success_count += 1
                        logger.info(f"Row {index + 2}: Muvaffaqiyatli import qilindi - {code_str}")
                    else:
                        failed_rows.append(row)
                        logger.warning(f"Row {index + 2}: Bazaga yozishda xatolik")
                
                except Exception as e:
                    logger.error(f"Row {index + 2}: Xatolik - {str(e)}")
                    failed_rows.append(row)
                    continue
            
            # Muvaffaqiyatsiz qatorlarni yangi Excel faylga yozish
            failed_excel_path = ""
            if failed_rows:
                failed_df = pd.DataFrame(failed_rows)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                failed_excel_path = f"failed_imports_{timestamp}.xlsx"
                failed_df.to_excel(failed_excel_path, index=False)
                logger.info(f"Failed rows saved to: {failed_excel_path}")
            
            logger.info(f"Import completed: {success_count} success, {len(failed_rows)} failed")
            return success_count, len(failed_rows), failed_excel_path
        
        except Exception as e:
            logger.error(f"Excel import error: {str(e)}")
            raise
    
    async def _insert_user_from_excel(self, user_data: Dict) -> bool:
        """
        Excel dan olingan ma'lumotlarni bazaga yozish
        """
        try:
            async with aiosqlite.connect(self.db_manager.db_path) as db:
                # Avval client_code yoki PINFL mavjudligini tekshirish
                cursor = await db.execute('''
                    SELECT id FROM users 
                    WHERE client_code = ? OR pinfl = ?
                ''', (user_data['client_code'], user_data['pinfl']))
                
                existing = await cursor.fetchone()
                
                if existing:
                    # Agar mavjud bo'lsa, update qilish
                    await db.execute('''
                        UPDATE users 
                        SET fullname = ?, 
                            passport_number = ?,
                            birth_date = ?,
                            address = ?,
                            phone = ?,
                            verification_status = ?,
                            verified_at = CURRENT_TIMESTAMP
                        WHERE client_code = ? OR pinfl = ?
                    ''', (
                        user_data['fullname'],
                        user_data['passport_number'],
                        user_data['birth_date'],
                        user_data['address'],
                        user_data['phone'],
                        user_data['verification_status'],
                        user_data['client_code'],
                        user_data['pinfl']
                    ))
                else:
                    # Yangi foydalanuvchi qo'shish
                    await db.execute('''
                        INSERT INTO users 
                        (client_code, fullname, passport_number, birth_date, 
                         address, phone, pinfl, verification_status, 
                         verified_at, language, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, 1)
                    ''', (
                        user_data['client_code'],
                        user_data['fullname'],
                        user_data['passport_number'],
                        user_data['birth_date'],
                        user_data['address'],
                        user_data['phone'],
                        user_data['pinfl'],
                        user_data['verification_status'],
                        user_data['language']
                    ))
                
                await db.commit()
                return True
        
        except Exception as e:
            logger.error(f"Insert user error: {str(e)}")
            return False


# DatabaseManager klassiga qo'shiladigan metod
async def import_users_excel_background(
    self,
    file_path: str,
    bot,
    admin_id: int
) -> None:
    """
    Background taskda foydalanuvchilarni import qilish
    """
    import os
    from aiogram.types import FSInputFile
    
    try:
        await bot.send_message(
            admin_id,
            "📥 Excel fayl import qilish boshlandi...\n"
            "Bu biroz vaqt olishi mumkin."
        )
        
        importer = ExcelUserImporter(self)
        success_count, failed_count, failed_file = await importer.import_users_from_excel(file_path)
        
        # Natijani adminga yuborish
        result_message = (
            f"✅ Import yakunlandi!\n\n"
            f"✅ Muvaffaqiyatli: {success_count} ta\n"
            f"❌ Xatolik: {failed_count} ta"
        )
        
        await bot.send_message(admin_id, result_message)
        
        # Agar muvaffaqiyatsiz qatorlar bo'lsa, Excel faylni yuborish
        if failed_file and os.path.exists(failed_file):
            document = FSInputFile(failed_file)
            await bot.send_document(
                admin_id,
                document,
                caption=f"❌ Bu faylda {failed_count} ta foydalanuvchi ro'yxati (xatoliklar bilan)"
            )
            
            # Faylni o'chirish
            os.remove(failed_file)
    
    except Exception as e:
        logger.error(f"Background import error: {str(e)}")
        await bot.send_message(
            admin_id,
            f"❌ Import jarayonida xatolik yuz berdi:\n{str(e)}"
        )


# ============ AIOGRAM HANDLER MISOL ============
"""
# admin_handlers.py ga qo'shiladigan kod

from aiogram import Router, F
from aiogram.types import Message
import asyncio
import os

router = Router()

@router.message(F.document)
async def handle_excel_import(message: Message, db: DatabaseManager):
    # Faqat adminlar uchun
    if message.from_user.id not in ADMIN_IDS:
        return
    
    file = message.document
    
    # Faqat Excel fayllarni qabul qilish
    if not file.file_name.endswith(('.xlsx', '.xls')):
        await message.answer("❌ Faqat Excel fayl (.xlsx yoki .xls) yuborish mumkin!")
        return
    
    # Faylni yuklab olish
    file_path = f"temp_{file.file_id}.xlsx"
    await message.bot.download(file, destination=file_path)
    
    # Background taskda import qilish
    asyncio.create_task(
        db.import_users_excel_background(
            file_path=file_path,
            bot=message.bot,
            admin_id=message.from_user.id
        )
    )
    
    # Taskdan keyin faylni o'chirish
    async def cleanup():
        await asyncio.sleep(300)  # 5 daqiqadan keyin
        if os.path.exists(file_path):
            os.remove(file_path)
    
    asyncio.create_task(cleanup())
"""
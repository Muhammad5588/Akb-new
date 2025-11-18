"""
Database Manager - Barcha CRUD operatsiyalar
"""
import aiosqlite
import logging
from typing import Optional, List, Dict, Tuple
from datetime import datetime
import pandas as pd

from config import (
    DB_FILE, 
    CLIENT_CODE_PREFIX, 
    CLIENT_CODE_START,
    VerificationStatus
)
from utils.excel import ExcelUserImporter

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Asinxron database boshqaruvchi"""
    
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
    
    async def init_db(self):
        """Database jadvallarini yaratish"""
        async with aiosqlite.connect(self.db_path) as db:
            # Users jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE,
                    client_code TEXT UNIQUE NOT NULL,
                    fullname TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    passport_number TEXT NOT NULL,
                    birth_date TEXT NOT NULL,
                    passport_expiry_date TEXT,
                    pinfl TEXT NOT NULL,
                    address TEXT NOT NULL,
                    china_address_confirmed BOOLEAN DEFAULT 0,
                    passport_front_photo TEXT,
                    passport_back_photo TEXT,
                    passport_front_file_id TEXT,
                    passport_back_file_id TEXT,
                    passport_front_file_unique_id TEXT,
                    passport_back_file_unique_id TEXT,
                    verification_status TEXT DEFAULT 'pending',
                    rejection_reason TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    language TEXT DEFAULT 'uz',
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verified_at TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Shipments jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS shipments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tracking_code TEXT NOT NULL,
                    shipping_name TEXT,
                    package_number TEXT,
                    weight REAL,
                    quantity INTEGER,
                    flight TEXT,
                    customer_code TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Feedbacks jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS feedbacks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    telegram_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    admin_reply TEXT,
                    replied_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Verification queue jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS verification_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    telegram_message_id INTEGER,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Indexlar
            await db.execute('CREATE INDEX IF NOT EXISTS idx_telegram_id ON users(telegram_id)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_client_code ON users(client_code)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_phone ON users(phone)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_tracking_code ON shipments(tracking_code)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_customer_code ON shipments(customer_code)')
            
            await db.commit()
            logger.info("Database initialized successfully")
    
    # ==================== USER MANAGEMENT ====================
    
    async def is_user_registered(self, telegram_id: int) -> bool:
        """Foydalanuvchi ro'yxatdan o'tganmi?"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT id FROM users WHERE telegram_id = ? AND is_active = 1',
                (telegram_id,)
            )
            result = await cursor.fetchone()
            return result is not None
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict]:
        """Telegram ID bo'yicha foydalanuvchini olish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM users WHERE telegram_id = ? AND is_active = 1',
                (telegram_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """ID bo'yicha foydalanuvchini olish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM users WHERE id = ? AND is_active = 1',
                (user_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def get_user_by_client_code(self, client_code: str) -> Optional[Dict]:
        """Mijoz kodi bo'yicha foydalanuvchini olish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM users WHERE UPPER(client_code) = UPPER(?) AND is_active = 1',
                (client_code,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def search_users(self, query: str) -> List[Dict]:
        """Foydalanuvchilarni qidirish (client_code yoki phone)"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Telefon raqam bo'lishi mumkin
            clean_query = query.replace('+', '').replace(' ', '').replace('-', '')
            
            cursor = await db.execute('''
                SELECT * FROM users 
                WHERE (UPPER(client_code) = UPPER(?) OR phone LIKE ?)
                AND is_active = 1
                ORDER BY registered_at DESC
            ''', (query, f'%{clean_query}%'))
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def generate_client_code(self) -> str:
        """Yangi client code generatsiya qilish"""
        async with aiosqlite.connect(self.db_path) as db:
            # Barcha client_code larni olish va raqamli qiymatni topish
            cursor = await db.execute('''
                SELECT client_code FROM users
                WHERE UPPER(client_code) LIKE UPPER(?)
            ''', (f'{CLIENT_CODE_PREFIX}%',))
            rows = await cursor.fetchall()

            if rows:
                # Barcha raqamlarni ajratib olish va eng kattasini topish
                max_number = CLIENT_CODE_START - 1
                for row in rows:
                    try:
                        code = row[0].upper()  # Katta harfga o'tkazish
                        number = int(code.replace(CLIENT_CODE_PREFIX, ''))
                        if number > max_number:
                            max_number = number
                    except:
                        continue

                next_number = max_number + 1
            else:
                # Agar hech kim bo'lmasa, boshlang'ich qiymatdan boshlash
                next_number = CLIENT_CODE_START

            # AKB600, AKB601, ...
            return f"{CLIENT_CODE_PREFIX}{next_number:03d}"
    
    async def register_user(self, telegram_id: int, user_data: Dict) -> Tuple[bool, str, str]:
        """
        Yangi foydalanuvchini ro'yxatdan o'tkazish
        
        Returns:
            (success, message, client_code)
        """
        try:
            client_code = await self.generate_client_code()
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO users
                    (telegram_id, client_code, fullname, phone, passport_number,
                     birth_date, passport_expiry_date, pinfl, address,
                     passport_front_photo, passport_back_photo,
                     passport_front_file_id, passport_back_file_id,
                     passport_front_file_unique_id, passport_back_file_unique_id,
                     language, verification_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    telegram_id,
                    client_code,
                    user_data['fullname'],
                    user_data['phone'],
                    user_data['passport_number'],
                    user_data['birth_date'],
                    user_data.get('passport_expiry_date'),
                    user_data['pinfl'],
                    user_data['address'],
                    user_data.get('passport_front_photo'),
                    user_data.get('passport_back_photo'),
                    user_data.get('passport_front_file_id'),
                    user_data.get('passport_back_file_id'),
                    user_data.get('passport_front_file_unique_id'),
                    user_data.get('passport_back_file_unique_id'),
                    user_data.get('language', 'uz'),
                    VerificationStatus.PENDING
                ))
                await db.commit()
                
                # User ID ni olish
                cursor = await db.execute(
                    'SELECT id FROM users WHERE client_code = ?',
                    (client_code,)
                )
                row = await cursor.fetchone()
                user_id = row[0]
            
            logger.info(f"User registered: {telegram_id} -> {client_code}")
            return True, "Success", client_code
        
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False, str(e), ""
    
    async def verify_login(self, client_code: str, phone: str) -> Optional[Dict]:
        """Login ma'lumotlarini tekshirish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Telefon raqamini normalize qilish
            clean_phone = phone.replace('+', '').replace(' ', '').replace('-', '')
            
            cursor = await db.execute('''
                SELECT * FROM users 
                WHERE UPPER(client_code) = UPPER(?) 
                AND phone LIKE ? 
                AND is_active = 1
            ''', (client_code, f'%{clean_phone}%'))
            
            row = await cursor.fetchone()
            
            if row:
                # Last login ni yangilash
                await db.execute(
                    'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                    (row['id'],)
                )
                await db.commit()
            
            return dict(row) if row else None
    
    # ==================== VERIFICATION ====================
    
    async def add_to_verification_queue(self, user_id: int, message_id: int) -> bool:
        """Verification queuega qo'shish"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO verification_queue (user_id, telegram_message_id)
                    VALUES (?, ?)
                ''', (user_id, message_id))
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"Add to queue error: {e}")
            return False
    
    async def approve_user(self, user_id: int) -> bool:
        """Foydalanuvchini tasdiqlash"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE users 
                    SET verification_status = ?, 
                        verified_at = CURRENT_TIMESTAMP,
                        rejection_reason = NULL
                    WHERE id = ?
                ''', (VerificationStatus.APPROVED, user_id))
                await db.commit()
            
            logger.info(f"User {user_id} approved")
            return True
        except Exception as e:
            logger.error(f"Approve error: {e}")
            return False
    
    async def reject_user(self, user_id: int, reason: str) -> bool:
        """Foydalanuvchini rad etish"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE users 
                    SET verification_status = ?, 
                        rejection_reason = ?
                    WHERE id = ?
                ''', (VerificationStatus.REJECTED, reason, user_id))
                await db.commit()
            
            logger.info(f"User {user_id} rejected: {reason}")
            return True
        except Exception as e:
            logger.error(f"Reject error: {e}")
            return False
    
    async def confirm_china_address(self, user_id: int) -> bool:
        """Xitoy manzilini tasdiqlash"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'UPDATE users SET china_address_confirmed = 1 WHERE id = ?',
                    (user_id,)
                )
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"China address confirm error: {e}")
            return False
    
    # ==================== SHIPMENTS ====================
    
    async def search_by_tracking_code(self, code: str) -> List[Dict]:
        """Trek kodi bo'yicha qidirish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('''
                SELECT * FROM shipments 
                WHERE LOWER(tracking_code) = LOWER(?)
            ''', (code.strip(),))
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def search_by_customer_code(self, code: str) -> List[Dict]:
        """Mijoz kodi bo'yicha qidirish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('''
                SELECT * FROM shipments 
                WHERE LOWER(customer_code) = LOWER(?)
                ORDER BY id DESC
            ''', (code.strip(),))
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def import_shipments_from_file(self, file_path: str) -> Tuple[bool, str]:
        """Excel yoki CSV fayldan yuklar import qilish"""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8')
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                return False, "Noto'g'ri fayl formati"
            
            required_columns = ['Shipment Tracking Code', 'Customer code']
            if not all(col in df.columns for col in required_columns):
                return False, f"Kerakli ustunlar topilmadi: {required_columns}"
            
            df = df.fillna('')
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('DELETE FROM shipments')
                
                for _, row in df.iterrows():
                    await db.execute('''
                        INSERT INTO shipments 
                        (tracking_code, shipping_name, package_number, 
                         weight, quantity, flight, customer_code)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        str(row.get('Shipment Tracking Code', '')).strip(),
                        str(row.get('Shipping Name', '')).strip(),
                        str(row.get('Package Number', '')).strip(),
                        float(row.get('Weight/KG', 0) or 0),
                        int(row.get('Quantity', 0) or 0),
                        str(row.get('Flight', '')).strip(),
                        str(row.get('Customer code', '')).strip()
                    ))
                
                await db.commit()
                count = len(df)
                logger.info(f"Imported {count} shipments")
                return True, f"{count} ta yuk yuklandi"
        
        except Exception as e:
            logger.error(f"Import error: {e}")
            return False, str(e)
    
    # ==================== FEEDBACK ====================
    
    async def save_feedback(self, user_id: int, telegram_id: int, message: str) -> Optional[int]:
        """Feedbackni saqlash"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute('''
                    INSERT INTO feedbacks (user_id, telegram_id, message)
                    VALUES (?, ?, ?)
                ''', (user_id, telegram_id, message))
                await db.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Save feedback error: {e}")
            return None
    
    async def save_feedback_reply(self, feedback_id: int, reply: str) -> bool:
        """Feedbackga admin javobini saqlash"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE feedbacks 
                    SET admin_reply = ?, replied_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (reply, feedback_id))
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"Save reply error: {e}")
            return False
    
    async def sdel(self) -> bool:
        """Feedbackga admin javobini saqlash"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    DELETE FROM users
                ''')
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"delete users error: {e}")
            return False
    
    async def get_feedback_by_id(self, feedback_id: int) -> Optional[Dict]:
        """Feedback ni ID bo'yicha olish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM feedbacks WHERE id = ?',
                (feedback_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    # ==================== STATISTICS ====================
    
    async def get_all_active_users(self) -> List[Dict]:
        """Barcha faol foydalanuvchilar"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('''
                SELECT * FROM users 
                WHERE is_active = 1 AND verification_status = ?
                ORDER BY registered_at DESC
            ''', (VerificationStatus.APPROVED,))
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_user_count(self) -> int:
        """Foydalanuvchilar soni"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT COUNT(*) FROM users WHERE is_active = 1'
            )
            row = await cursor.fetchone()
            return row[0] if row else 0


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

            # 2. Baza faylini zaxira nusxasi sifatida yuborish (oxirida, har holda!)
            try:
                database_file = FSInputFile(self.db_path)
                await bot.send_document(
                    admin_id,
                    database_file,
                    caption=f"💾 Yangilangan bazaning zaxira nusxasi"
                )
                logger.info("Database backup sent successfully")
            except Exception as e:
                logger.error(f"Database send error: {str(e)}")
                try:
                    await bot.send_message(
                        admin_id,
                        f"⚠️ Bazani yuborishda xatolik: {str(e)}"
                    )
                except:
                    pass

        except Exception as e:
            logger.error(f"Background import error: {str(e)}")
            await bot.send_message(
                admin_id,
                f"❌ Import jarayonida xatolik yuz berdi:\n{str(e)}"
            )


if __name__ == "__main__":
    import asyncio

    async def test():
        db_manager = DatabaseManager()
        await db_manager.init_db()
        print("Database initialized for testing.")

    asyncio.run(test())

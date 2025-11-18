import asyncio
import os
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database.db_manager import DatabaseManager
from config import ADMINS
from states import AdminStates

router = Router()
db = DatabaseManager()

@router.message(AdminStates.user_exel_importing_process)
async def handle_excel_import(message: Message, state: FSMContext):
    # Faqat adminlar uchun
    if message.from_user.id not in ADMINS:
        return

    # Agar document yuborilmagan bo'lsa, state'ni tozalash
    if not message.document:
        await state.clear()
        return

    file = message.document

    # Faqat Excel fayllarni qabul qilish
    if not file.file_name.endswith(('.xlsx', '.xls')):
        await message.answer("❌ Faqat Excel fayl (.xlsx yoki .xls) yuborish mumkin!")
        await state.clear()
        return
    
    # Faylni yuklab olish
    file_path = f"temp_{file.file_id}.xlsx"
    # file_path = f"akb.xlsx"
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
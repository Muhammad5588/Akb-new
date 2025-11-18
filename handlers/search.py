"""
Search Handlers - Yuklar bo'yicha qidiruv
"""
import logging
from site import PREFIXES
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from config import CLIENT_CODE_PREFIX, is_admin
from database.db_manager import DatabaseManager
from utils.texts import get_text
from utils.keyboards import (
    search_type_keyboard,
    back_keyboard,
    main_menu_keyboard
)
from utils.formatters import format_weight
from utils.helpers import check_user_approved

logger = logging.getLogger(__name__)
router = Router()
db = DatabaseManager()


# ==================== STATES ====================

class SearchStates(StatesGroup):
    selecting_search_type = State()
    searching_by_trek = State()
    viewing_my_shipments = State()


# ==================== QIDIRUV BOSHLASH ====================

@router.message(F.text.in_([
    get_text('uz', 'search'),
    get_text('ru', 'search')
]))
async def start_search(message: Message, state: FSMContext):
    """Qidirishni boshlash"""
    # Admin uchun tekshiruv yo'q
    if is_admin(message.from_user.id):
        user = await db.get_user_by_telegram_id(message.from_user.id)
        data = await state.get_data()
        lang = data.get('language', 'uz')
    else:
        # Oddiy foydalanuvchilar uchun tasdiqlangan bo'lishi kerak
        user, lang, is_approved = await check_user_approved(message, state)
        if not user or not is_approved:
            return
    
    await state.set_state(SearchStates.selecting_search_type)
    await message.answer(
        get_text(lang, 'select_search_type'),
        reply_markup=search_type_keyboard(lang)
    )


# ==================== TREK KODI BO'YICHA ====================

@router.message(SearchStates.selecting_search_type, F.text.in_([
    get_text('uz', 'by_trek'),
    get_text('ru', 'by_trek')
]))
async def start_trek_search(message: Message, state: FSMContext):
    """Trek kodi bo'yicha qidirishni boshlash"""
    user = await db.get_user_by_telegram_id(message.from_user.id)
    lang = user['language']
    
    await state.set_state(SearchStates.searching_by_trek)
    await message.answer(
        get_text(lang, 'enter_trek_code'),
        reply_markup=back_keyboard(lang)
    )


@router.message(SearchStates.searching_by_trek, F.text)
async def process_trek_search(message: Message, state: FSMContext):
    """Trek kodi bo'yicha qidirish"""
    user = await db.get_user_by_telegram_id(message.from_user.id)
    lang = user['language']
    
    if message.text == get_text(lang, 'back'):
        await state.set_state(SearchStates.selecting_search_type)
        await message.answer(
            get_text(lang, 'select_search_type'),
            reply_markup=search_type_keyboard(lang)
        )
        return
    
    # Bir nechta kodni qidirish
    codes = [c.strip() for c in message.text.replace(',', ' ').split() if c.strip()]
    
    if not codes:
        await message.answer(
            "Iltimos, trek kodni kiriting!" if lang == 'uz' else "Пожалуйста, введите трек-код!"
        )
        return
    
    found_any = False
    
    for code in codes:
        results = await db.search_by_tracking_code(code)
        
        if results:
            found_any = True
            
            for item in results:
                
                # Faqat o'zining yukini ko'rishi mumkin (admin emas bo'lsa)
                if not is_admin(message.from_user.id):
                    if item['customer_code'].upper().startswith(CLIENT_CODE_PREFIX) and item['customer_code'].upper().split(CLIENT_CODE_PREFIX)[1].isdigit():
                        if item['customer_code'].upper() != user['client_code'].upper():
                            await message.answer(
                                f"❌ {code} - Bu yuk sizga tegishli emas!" 
                                if lang == 'uz' else 
                                f"❌ {code} - Этот груз вам не принадлежит!"
                            )
                            continue
                    else:
                        pass # Noma'lum prefiksli yuklar uchun cheklov yo'q
                
                # Yuk ma'lumotlari
                response = f"{get_text(lang, 'shipment_found')}\n\n"
                response += get_text(
                    lang, 'shipment_details',
                    name=item['shipping_name'] or "—",
                    tracking=item['tracking_code'],
                    package=item['package_number'] or "—",
                    weight=format_weight(item['weight']),
                    quantity=item['quantity'],
                    flight=item['flight'] or "—"
                )
                
                await message.answer(response)
        else:
            await message.answer(
                get_text(lang, 'shipment_not_found', code=code)
            )
    
    # if found_any:
    #     try:
    #         await message.answer("✅")
    #     except:
    #         pass
    # else:
    #     try:
    #         await message.answer("❌")
    #     except:
    #         pass


# ==================== MENING YUKLARIM ====================

@router.message(SearchStates.selecting_search_type, F.text.in_([
    get_text('uz', 'by_my_code'),
    get_text('ru', 'by_my_code')
]))
async def show_my_shipments(message: Message, state: FSMContext):
    """Foydalanuvchining barcha yuklar"""
    user = await db.get_user_by_telegram_id(message.from_user.id)
    lang = user['language']
    
    # Foydalanuvchining client_code bo'yicha barcha yuklar
    results = await db.search_by_customer_code(user['client_code'])
    
    if not results:
        await message.answer(
            get_text(lang, 'no_shipments'),
            reply_markup=back_keyboard(lang)
        )
        return
    
    # Yuklar soni
    await message.answer(
        get_text(lang, 'my_shipments', count=len(results))
    )
    
    # Har bir yukni ko'rsatish
    for idx, item in enumerate(results, 1):
        response = f"📦 #{idx}\n\n"
        response += get_text(
            lang, 'shipment_details',
            name=item['shipping_name'] or "—",
            tracking=item['tracking_code'],
            package=item['package_number'] or "—",
            weight=format_weight(item['weight']),
            quantity=item['quantity'],
            flight=item['flight'] or "—"
        )
        
        await message.answer(response)
        
        # Telegram rate limit uchun
        import asyncio
        await asyncio.sleep(0.3)
    
    # Success sticker
    # try:
    #     await message.answer("✅")
    # except:
    #     pass
    
    await message.answer(
        "Barcha yuklar ko'rsatildi!" if lang == 'uz' else "Все грузы показаны!",
        reply_markup=back_keyboard(lang)
    )


# ==================== ORQAGA ====================

@router.message(SearchStates.selecting_search_type, F.text.in_([
    get_text('uz', 'back'),
    get_text('ru', 'back')
]))
async def search_back(message: Message, state: FSMContext):
    """Qidiruvdan orqaga"""
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


# # ==================== NOMA'LUM XABARLAR ====================

# @router.message(F.text)
# async def handle_unknown_message(message: Message, state: FSMContext):
#     """Noma'lum xabarlarni qayta ishlash"""
#     user = await db.get_user_by_telegram_id(message.from_user.id)
#     if user:
#         lang = user['language']
        
#         await message.answer(
#             get_text(lang, 'invalid_command'),
#             reply_markup=main_menu_keyboard(lang, is_admin(message.from_user.id))
#         )
#     else:
#         # Ro'yxatdan o'tmagan
#         from utils.keyboards import welcome_keyboard
#         data = await state.get_data()
#         lang = data.get('language', 'uz')
        
#         await message.answer(
#             get_text(lang, 'welcome_new'),
#             reply_markup=welcome_keyboard(lang)
#         )
"""
Admin Handlers - Admin Panel va Boshqaruv
"""
import os
import logging
import asyncio
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
)

from config import (
    is_admin,
    VERIFIED_GROUP_ID,
)
from database.db_manager import DatabaseManager
from states import AdminStates
from utils.texts import get_text
from utils.keyboards import (
    admin_menu_keyboard,
    main_menu_keyboard,
    back_keyboard,
    broadcast_confirm_inline_keyboard,
    user_management_inline_keyboard,
)
from utils.formatters import (
    format_phone_display, 
    format_datetime,
    format_verification_status
)

logger = logging.getLogger(__name__)
router = Router()
db = DatabaseManager()







# ==================== ADMIN PANEL ====================

async def show_admin_panel(message: Message, state: FSMContext):
    """Admin panelni ko'rsatish"""
    if not is_admin(message.from_user.id):
        await message.answer(get_text('uz', 'access_denied'))
        return
    
    await state.set_state(AdminStates.in_admin_panel)
    await state.update_data(language='uz')
    await message.answer(
        get_text('uz', 'admin_welcome'),
        reply_markup=admin_menu_keyboard('uz')
    )


@router.message(F.text.in_([
    get_text('uz', 'admin_panel'),
    get_text('ru', 'admin_panel')
]))
async def admin_panel_button(message: Message, state: FSMContext):
    """Admin panel tugmasi"""
    await show_admin_panel(message, state)


# ==================== APPROVAL / REJECTION ====================

@router.callback_query(F.data.startswith("approve:"))
async def approve_user_callback(callback: CallbackQuery, bot: Bot):
    """Foydalanuvchini tasdiqlash"""
    # Admin tekshiruvi
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    try:
        user_id = int(callback.data.split(":")[1])
        
        # Tasdiqlash
        success = await db.approve_user(user_id)
        
        if success:
            user = await db.get_user_by_id(user_id)

            if user and user['telegram_id']:
                # Foydalanuvchiga xabar va verified guruhga yuborishni background taskda ishlatish
                async def send_notifications():
                    # Foydalanuvchiga xabar
                    try:
                        await bot.send_message(
                            user['telegram_id'],
                            get_text(
                                user['language'],
                                'registration_approved',
                                client_code=user['client_code'],
                                phone=format_phone_display(user['phone'])
                            ),
                            reply_markup=main_menu_keyboard(user['language'], False)
                        )
                    except:
                        logger.warning(f"Could not send approval message to user {user_id}")

                    # Xitoy manzilini yuborish
                    try:
                        from config import CHINA_ADDRESS_TEMPLATE, CHINA_ADDRESS_TEMPLATE_TEXT
                        from aiogram.types import FSInputFile
                        import os

                        # Template rasmni yuborish
                        if CHINA_ADDRESS_TEMPLATE and os.path.exists(CHINA_ADDRESS_TEMPLATE):
                            try:
                                await bot.send_photo(
                                    user['telegram_id'],
                                    FSInputFile(CHINA_ADDRESS_TEMPLATE),
                                    caption="🇨🇳 Xitoy sklad manzili"
                                )
                            except:
                                pass

                        # Manzil matni
                        address_text = CHINA_ADDRESS_TEMPLATE_TEXT.format(
                            client_code=user['client_code']
                        )
                        await bot.send_message(user['telegram_id'], address_text)

                        # Muhim ogohlantirish xabari
                        warning_message = (
                            "⚠️ MUHIM OGOHLANTIRISH!\n\n"
                            "Xitoy manzilini to'g'ri kiritganingizni tekshiring va "
                            "@AKB_CARGO adminga yozib, manzilni tasdiqlatishingizni so'raymiz.\n\n"
                            "❗️ Admin tomonidan tasdiqlanmagan manzilga yuborilgan yuklar "
                            "uchun javobgarlik o'z zimmamizga olinmaydi!\n\n"
                            "📞 Manzilni tasdiqlash uchun: @AKB_CARGO"
                            if user['language'] == 'uz' else
                            "⚠️ ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ!\n\n"
                            "Проверьте правильность указанного адреса в Китае и "
                            "свяжитесь с @AKB_CARGO для подтверждения адреса.\n\n"
                            "❗️ Мы не несем ответственности за грузы, "
                            "отправленные на адрес, не подтвержденный администратором!\n\n"
                            "📞 Для подтверждения адреса: @AKB_CARGO"
                        )
                        await bot.send_message(user['telegram_id'], warning_message)

                    except Exception as e:
                        logger.warning(f"Could not send China address to user {user_id}: {e}")

                    # Verified guruhga yuborish
                    await send_to_verified_group(bot, user)

                # Background taskda yuborish
                asyncio.create_task(send_notifications())

            # Callback javob
            await callback.answer("✅ Foydalanuvchi tasdiqlandi!", show_alert=True)
            
            # Xabarni tahrirlash
            try:
                await callback.message.edit_text(
                    callback.message.text + "\n\n✅ TASDIQLANDI",
                    reply_markup=None
                )
            except:
                pass
        else:
            await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)
    
    except Exception as e:
        logger.error(f"Approve callback error: {e}")
        await callback.answer("❌ Xatolik!", show_alert=True)


@router.callback_query(F.data.startswith("reject:"))
async def reject_user_callback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Foydalanuvchini rad etish - sabab so'rash"""
    # Admin tekshiruvi
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    try:
        user_id = int(callback.data.split(":")[1])

        # State ga saqlash (guruhda ham, private chatda ham)
        await state.update_data(
            rejecting_user_id=user_id,
            rejection_message_id=callback.message.message_id,
            rejection_chat_id=callback.message.chat.id
        )
        await state.set_state(AdminStates.entering_rejection_reason)

        # Guruhda yoki private chatda - bir xil javob
        reply_text = f"❌ User ID {user_id} ni rad etish uchun sabab yozing:"

        await callback.message.reply(reply_text)
        await callback.answer()

    except Exception as e:
        logger.error(f"Reject callback error: {e}")
        await callback.answer("❌ Xatolik!", show_alert=True)


@router.message(AdminStates.entering_rejection_reason, F.text)
async def process_rejection_reason(message: Message, state: FSMContext, bot: Bot):
    """Rad etish sababini qabul qilish"""
    data = await state.get_data()
    user_id = data.get('rejecting_user_id')
    rejection_message_id = data.get('rejection_message_id')
    rejection_chat_id = data.get('rejection_chat_id')

    if message.text == get_text('uz', 'back'):
        await state.clear()
        await message.answer(
            "❌ Rad etish bekor qilindi",
            reply_markup=admin_menu_keyboard('uz')
        )
        return

    if not user_id:
        await message.answer("❌ Xatolik: User ID topilmadi")
        return

    reason = message.text.strip()

    # Rad etish
    success = await db.reject_user(user_id, reason)

    if success:
        user = await db.get_user_by_id(user_id)

        if user and user['telegram_id']:
            # Foydalanuvchiga xabar
            try:
                await bot.send_message(
                    user['telegram_id'],
                    get_text(user['language'], 'registration_rejected', reason=reason)
                )
            except:
                logger.warning(f"Could not send rejection message to user {user_id}")

        # Asl xabarni yangilash (guruhda yoki private chatda)
        if rejection_message_id and rejection_chat_id:
            try:
                # Tugmalarni olib tashlash
                try:
                    await bot.edit_message_reply_markup(
                        chat_id=rejection_chat_id,
                        message_id=rejection_message_id,
                        reply_markup=None
                    )
                except:
                    pass

                # Guruhga rad etilgani haqida xabar yuborish
                await bot.send_message(
                    rejection_chat_id,
                    f"❌ RAD ETILDI\nSabab: {reason}",
                    reply_to_message_id=rejection_message_id
                )
            except Exception as e:
                logger.error(f"Error updating rejection message: {e}")

        await message.answer(
            f"✅ User ID {user_id} rad etildi!\nSabab: {reason}"
        )
    else:
        await message.answer("❌ Xatolik yuz berdi!")

    await state.clear()


async def send_to_verified_group(bot: Bot, user: dict):
    """Tasdiqlangan foydalanuvchini verified guruhga yuborish (RASM BILAN)"""
    import asyncio

    try:
        text = f"""
✅ YANGI TASDIQLANGAN MIJOZ

👤 {user['fullname']}
🆔 {user['client_code']}
📱 {format_phone_display(user['phone'])}
🔖 Pasport: {user['passport_number']}
📅 Tug'ilgan: {user['birth_date']}
🔢 PINFL: {user['pinfl']}
📍 {user['address']}

📅 Tasdiqlangan: {format_datetime(user.get('verified_at', 'now'))}
"""

        # Async tasklar ro'yxati
        tasks = []

        # Pasport rasmlarini yuborish (file_id orqali)
        if user.get('passport_front_file_id'):
            tasks.append(
                bot.send_photo(
                    VERIFIED_GROUP_ID,
                    user['passport_front_file_id'],
                    caption=f"📸 Pasport (OLD) - {user['client_code']}"
                )
            )

        # Agar ID card bo'lsa (2 ta rasm)
        if user.get('passport_back_file_id') and user['passport_back_file_id'] != user.get('passport_front_file_id'):
            tasks.append(
                bot.send_photo(
                    VERIFIED_GROUP_ID,
                    user['passport_back_file_id'],
                    caption=f"📸 Pasport (ORQA) - {user['client_code']}"
                )
            )

        # Rasmlarni parallel yuborish
        if tasks:
            await asyncio.gather(*tasks)

        # Matnni yuborish
        await bot.send_message(VERIFIED_GROUP_ID, text)

    except Exception as e:
        logger.error(f"Send to verified group error: {e}")


# ==================== BARCHA FOYDALANUVCHILARNI KO'RISH ====================

@router.message(F.text.contains("👥") | F.text.contains("Foydalanuvchilar") | F.text.contains("пользовател"))
async def show_all_users(message: Message, state: FSMContext):
    """Barcha foydalanuvchilarni ko'rsatish"""
    if not is_admin(message.from_user.id):
        await message.answer(get_text('uz', 'access_denied'))
        return

    # Foydalanuvchilar soni
    user_count = await db.get_user_count()

    # Statistika
    stats_text = f"""
📊 FOYDALANUVCHILAR STATISTIKASI

👥 Jami: {user_count} ta

📤 Excel faylni yuklash uchun fayl yuboring.
"""
    await message.answer(stats_text)
    await state.set_state(AdminStates.user_exel_importing_process)


# ==================== FOYDALANUVCHINI TO'LIQ KO'RISH ====================

@router.callback_query(F.data.startswith("viewuser:"))
async def view_user_details(callback: CallbackQuery):
    """Foydalanuvchi to'liq ma'lumotlarini ko'rish"""
    # Admin tekshiruvi
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    try:
        user_id = int(callback.data.split(":")[1])
        user = await db.get_user_by_id(user_id)
        
        if not user:
            await callback.answer("❌ Foydalanuvchi topilmadi!", show_alert=True)
            return
        
        # To'liq ma'lumotlar
        full_info = f"""
👤 TO'LIQ MA'LUMOTLAR

🆔 ID: {user['id']}
👨‍💼 F.I.O: {user['fullname']}
🔐 Mijoz kodi: {user['client_code']}
📱 Telefon: {format_phone_display(user['phone'])}
🔖 Pasport: {user['passport_number']}
📅 Tug'ilgan: {user['birth_date']}
📅 Muddat: {user['passport_expiry_date'] or '—'}
🔢 PINFL: {user['pinfl']}
📍 Manzil: {user['address']}

✅ Holat: {format_verification_status(user['verification_status'], 'uz')}
🇨🇳 Xitoy manzil: {'✅ Tasdiqlangan' if user['china_address_confirmed'] else '❌ Tasdiqlanmagan'}
🌐 Til: {user['language'].upper()}

📅 Ro'yxat: {format_datetime(user['registered_at'])}
📅 Oxirgi kirish: {format_datetime(user['last_login']) if user['last_login'] else '—'}

💬 Telegram ID: {user['telegram_id'] if user['telegram_id'] else '—'}
"""
        
        # Pasport rasmlar
        photos_text = "\n📸 Pasport rasmlari:\n"
        if user['passport_front_photo']:
            photos_text += f"• Old: {user['passport_front_photo']}\n"
        if user['passport_back_photo']:
            photos_text += f"• Orqa: {user['passport_back_photo']}\n"
        
        await callback.message.answer(full_info + photos_text)
        await callback.answer()
    
    except Exception as e:
        logger.error(f"View user error: {e}")
        await callback.answer("❌ Xatolik!", show_alert=True)



# ==================== USER QIDIRISH ====================

@router.message(F.text.in_([
    get_text('uz', 'search_user'),
    get_text('ru', 'search_user')
]))
async def start_user_search(message: Message, state: FSMContext):
    """User qidirishni boshlash"""
    if not is_admin(message.from_user.id):
        await message.answer(get_text('uz', 'access_denied'))
        return
    
    await state.set_state(AdminStates.searching_user)
    await message.answer(
        get_text('uz', 'enter_user_search'),
        reply_markup=back_keyboard('uz')
    )


@router.message(AdminStates.searching_user, F.text)
async def process_user_search(message: Message, state: FSMContext):
    """User ni qidirish"""
    if message.text == get_text('uz', 'back'):
        await state.set_state(AdminStates.in_admin_panel)
        await message.answer(
            get_text('uz', 'admin_welcome'),
            reply_markup=admin_menu_keyboard('uz')
        )
        return
    
    query = message.text.strip()
    users = await db.search_users(query)
    
    if not users:
        await message.answer(get_text('uz', 'user_not_found'))
        return
    
    # Natijalarni ko'rsatish
    for user in users:
        user_info = get_text(
            'uz', 'admin_user_info',
            user_id=user['id'],
            fullname=user['fullname'],
            phone=format_phone_display(user['phone']),
            passport=user['passport_number'],   
            birth_date=user['birth_date'],
            pinfl=user['pinfl'],
            address=user['address'],
            status=user['verification_status'],
            registered_at=format_datetime(user['registered_at'])
        )
        
        await message.answer(
            user_info,
            reply_markup=user_management_inline_keyboard(user['id'], 'uz')
        )


# ==================== BROADCAST ====================

@router.message(F.text.in_([
    get_text('uz', 'broadcast'),
    get_text('ru', 'broadcast')
]))
async def start_broadcast(message: Message, state: FSMContext):
    """Broadcast ni boshlash"""
    if not is_admin(message.from_user.id):
        await message.answer(get_text('uz', 'access_denied'))
        return
    
    await state.set_state(AdminStates.entering_broadcast_message)
    await message.answer(
        get_text('uz', 'enter_broadcast_message'),
        reply_markup=back_keyboard('uz')
    )


@router.message(AdminStates.entering_broadcast_message, F.text)
async def process_broadcast_message(message: Message, state: FSMContext):
    """Broadcast xabarini qabul qilish"""
    if message.text == get_text('uz', 'back'):
        await state.set_state(AdminStates.in_admin_panel)
        await message.answer(
            get_text('uz', 'admin_welcome'),
            reply_markup=admin_menu_keyboard('uz')
        )
        return
    
    broadcast_text = message.text
    
    # Foydalanuvchilar sonini olish
    user_count = await db.get_user_count()
    
    # Tasdiqlash
    await state.update_data(broadcast_message=broadcast_text)
    
    await message.answer(
        get_text('uz', 'broadcast_confirm', count=user_count, message=broadcast_text),
        reply_markup=broadcast_confirm_inline_keyboard('uz')
    )


@router.callback_query(F.data == "broadcast:confirm")
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Broadcast ni tasdiqlash va yuborish"""
    # Admin tekshiruvi
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    data = await state.get_data()
    broadcast_text = data.get('broadcast_message')
    
    if not broadcast_text:
        await callback.answer("❌ Xabar topilmadi!", show_alert=True)
        return
    
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    
    # Yuborish jarayoni
    await callback.message.answer(get_text('uz', 'broadcast_sending'))
    
    users = await db.get_all_active_users()
    
    sent = 0
    failed = 0
    
    for user in users:
        try:
            await bot.send_message(user['telegram_id'], broadcast_text)
            sent += 1
            await asyncio.sleep(0.05)  # Rate limit
        except Exception as e:
            logger.warning(f"Broadcast to {user['telegram_id']} failed: {e}")
            failed += 1
    
    # Natija
    await callback.message.answer(
        get_text('uz', 'broadcast_completed', sent=sent, total=len(users)),
        reply_markup=admin_menu_keyboard('uz')
    )
    
    await state.set_state(AdminStates.in_admin_panel)


@router.callback_query(F.data == "broadcast:cancel")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    """Broadcast ni bekor qilish"""
    # Admin tekshiruvi
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("❌ Bekor qilindi")
    
    await state.set_state(AdminStates.in_admin_panel)
    await callback.message.answer(
        get_text('uz', 'admin_welcome'),
        reply_markup=admin_menu_keyboard('uz')
    )


# ==================== DATABASE YUKLASH ====================

@router.message(F.text.in_([
    get_text('uz', 'upload_db'),
    get_text('ru', 'upload_db')
]))
async def start_db_upload(message: Message, state: FSMContext):
    """Database yuklashni boshlash"""
    if not is_admin(message.from_user.id):
        await message.answer(get_text('uz', 'access_denied'))
        return
    
    await state.set_state(AdminStates.uploading_database)
    await message.answer(
        get_text('uz', 'upload_file_prompt'),
        reply_markup=back_keyboard('uz')
    )


@router.message(AdminStates.uploading_database, F.document)
async def process_db_upload(message: Message, state: FSMContext, bot: Bot):
    """Database faylini yuklash"""
    if not is_admin(message.from_user.id):
        await message.answer(get_text('uz', 'access_denied'))
        return
    
    doc = message.document
    
    if not doc.file_name.endswith(('.xlsx', '.xls', '.csv')):
        await message.answer(get_text('uz', 'invalid_file_format'))
        return
    
    try:
        # Faylni yuklab olish
        file = await bot.get_file(doc.file_id)
        file_path = f"temp_{doc.file_name}"
        
        await bot.download_file(file.file_path, file_path)
        
        # Import qilish
        success, msg = await db.import_shipments_from_file(file_path)
        
        # Temp faylni o'chirish
        if os.path.exists(file_path):
            os.remove(file_path)
        
        if success:
            await message.answer(
                f"{get_text('uz', 'database_uploaded')}\n{msg}",
                reply_markup=admin_menu_keyboard('uz')
            )
        else:
            await message.answer(
                f"{get_text('uz', 'upload_error')}: {msg}",
                reply_markup=admin_menu_keyboard('uz')
            )
        
        await state.set_state(AdminStates.in_admin_panel)
    
    except Exception as e:
        logger.error(f"DB upload error: {e}")
        await message.answer(
            f"{get_text('uz', 'upload_error')}: {str(e)}",
            reply_markup=admin_menu_keyboard('uz')
        )


# ==================== ADMIN TREK QIDIRISH ====================

@router.message(F.text.in_([
    get_text('uz', 'admin_search'),
    get_text('ru', 'admin_search')
]))
async def start_admin_search(message: Message, state: FSMContext):
    """Admin trek qidirishni boshlash"""
    if not is_admin(message.from_user.id):
        await message.answer(get_text('uz', 'access_denied'))
        return
    
    await state.set_state(AdminStates.admin_searching_trek)
    await message.answer(
        get_text('uz', 'enter_trek_code'),
        reply_markup=back_keyboard('uz')
    )


@router.message(AdminStates.admin_searching_trek, F.text)
async def process_admin_search(message: Message, state: FSMContext):
    """Admin trek qidirish (full access)"""
    if message.text == get_text('uz', 'back'):
        await state.set_state(AdminStates.in_admin_panel)
        await message.answer(
            get_text('uz', 'admin_welcome'),
            reply_markup=admin_menu_keyboard('uz')
        )
        return
    
    codes = [c.strip() for c in message.text.replace(',', ' ').split() if c.strip()]
    
    found_any = False
    
    for code in codes:
        results = await db.search_by_tracking_code(code)
        
        if results:
            found_any = True
            for item in results:
                response = f"{get_text('uz', 'shipment_found')} (Trek: {code})\n\n"
                response += get_text(
                    'uz', 'shipment_details',
                    name=item['shipping_name'],
                    tracking=item['tracking_code'],
                    package=item['package_number'],
                    weight=item['weight'],
                    quantity=item['quantity'],
                    flight=item['flight']
                )
                response += f"\n👤 Customer: {item['customer_code']}"
                
                await message.answer(response)
        else:
            await message.answer(f"{get_text('uz', 'trek_not_found')}: {code}")
    
    if not found_any:
        await message.answer("❌ Hech qanday yuk topilmadi")


# ==================== FEEDBACK REPLY ====================

@router.callback_query(F.data.startswith("feedback_reply:"))
async def feedback_reply_callback(callback: CallbackQuery, state: FSMContext):
    """Feedbackga javob berish"""
    # Admin tekshiruvi
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    try:
        parts = callback.data.split(":")
        user_telegram_id = int(parts[1])
        feedback_id = int(parts[2])
        
        # State ga saqlash
        await state.update_data(
            replying_to_user=user_telegram_id,
            replying_to_feedback=feedback_id
        )
        await state.set_state(AdminStates.replying_to_feedback)
        
        await callback.message.answer(
            "💬 Javobingizni yozing:",
            reply_markup=back_keyboard('uz')
        )
        
        await callback.answer()
    
    except Exception as e:
        logger.error(f"Feedback reply callback error: {e}")
        await callback.answer("❌ Xatolik!", show_alert=True)


@router.message(AdminStates.replying_to_feedback, F.text)
async def process_feedback_reply(message: Message, state: FSMContext, bot: Bot):
    """Admin javobini yuborish"""
    data = await state.get_data()
    user_telegram_id = data.get('replying_to_user')
    feedback_id = data.get('replying_to_feedback')
    
    if message.text == get_text('uz', 'back'):
        await state.clear()
        await message.answer(
            get_text('uz', 'admin_welcome'),
            reply_markup=admin_menu_keyboard('uz')
        )
        return
    
    if not user_telegram_id or not feedback_id:
        await message.answer("❌ Xatolik: Ma'lumotlar topilmadi")
        return
    
    reply_text = message.text
    
    # Database ga saqlash
    success = await db.save_feedback_reply(feedback_id, reply_text)
    
    if success:
        # User ga yuborish
        try:
            user = await db.get_user_by_telegram_id(user_telegram_id)
            if user:
                await bot.send_message(
                    user_telegram_id,
                    get_text(user['language'], 'feedback_reply', reply=reply_text)
                )
                
                await message.answer(
                    "✅ Javob foydalanuvchiga yuborildi!",
                    reply_markup=admin_menu_keyboard('uz')
                )
            else:
                await message.answer("❌ Foydalanuvchi topilmadi")
        
        except Exception as e:
            logger.error(f"Send reply error: {e}")
            await message.answer(f"❌ Yuborishda xatolik: {e}")
    else:
        await message.answer("❌ Saqlashda xatolik")
    
    await state.clear()


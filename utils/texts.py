"""
Barcha matnlar va tarjimalar
"""

TEXTS = {
    'uz': {
        # ==================== UMUMIY ====================
        'welcome_new': (
            "👋 Assalomu alaykum!\n\n"
            "AKB CARGO botiga xush kelibsiz!\n\n"
            "Botdan foydalanish uchun ro'yxatdan o'tishingiz kerak."
        ),
        'welcome_registered': (
            "🎉 Xush kelibsiz, {fullname}!\n\n"
            "📋 Sizning ma'lumotlaringiz:\n"
            "🆔 Mijoz kodi: {client_code}\n"                                                         
            "📱 Telefon: {phone}\n"
            "✅ Holat: {status}\n\n"
            "{status_message}"
        ),
        'status_pending': "⏳ Ma'lumotlaringiz ko'rib chiqilmoqda...",
        'status_approved': "✅ Tasdiqlangan! Barcha xizmatlardan foydalanishingiz mumkin.",
        'status_rejected': "❌ Ma'lumotlaringiz rad etildi.\n\n📝 Sabab: {reason}\n\nQaytadan ro'yxatdan o'ting.",
        
        # ==================== TUGMALAR ====================
        'register': "Ro'yxatdan o'tish 📝",
        'login': "Kirish 🔐",
        'cancel': "Bekor qilish ❌",
        'back': "⬅️ Orqaga",
        'confirm': "✅ Tasdiqlash",
        'search': "🔍 Yukni qidirish",
        'profile': "👤 Profilim",
        'feedback': "💬 Izoh qoldirish",
        'contacts': "📍 Aloqa",
        'language': "🌐 Til",
        'logout': "🚪 Chiqish",
        'china_address': "🇨🇳 Xitoy manzili",
        
        # Admin
        'admin_panel': "⚙️ Admin Panel",
        'manage_users': "👥 Foydalanuvchilar",
        'add_user': "➕ Foydalanuvchi qo'shish",
        'search_user': "🔍 Foydalanuvchini qidirish",
        'upload_db': "📂 Database yuklash",
        'broadcast': "📢 Xabar yuborish",
        'admin_search': "🔎 Trek qidirish",
        
        # ==================== RO'YXATDAN O'TISH ====================
        'enter_fullname': (
            "👤 Ism va familiyangizni kiriting:\n\n"
            "Misol: Alisher Navoiy"
        ),
        'enter_phone': (
            "📱 Telefon raqamingizni kiriting:\n\n"
            "Format:\n"
            "• +998 XX XXX XX XX\n"
            "• 998 XX XXX XX XX\n"
            "• XX XXX XX XX\n\n"
            "Misol: 90 123 45 67"
        ),
        'select_passport_type': (
            "🆔 Pasportingiz qanday?\n\n"
            "ID karta (2 ta rasm)\n"
            "Biometrik pasport - Yashil pasport (1 ta rasm)"
        ),
        'passport_id_card': "🆔 ID karta",
        'passport_booklet': "📖 Biometrik pasport (yashil)",
        'upload_passport_front': (
            "📸 Pasport OLD tomonini yuklang\n\n"
            "Rasmda:\n"
            "✓ Yaxshi sifatli\n"
            "✓ Barcha ma'lumotlar aniq ko'rinadi\n"
            "✓ Burchaklar to'g'ri"
        ),
        'upload_passport_back': (
            "📸 Pasport ORQA tomonini yuklang\n\n"
            "Rasmda:\n"
            "✓ Yaxshi sifatli\n"
            "✓ Barcha ma'lumotlar aniq ko'rinadi\n"
            "✓ Burchaklar to'g'ri"
        ),
        'upload_passport_booklet': (
            "📸 Pasport rasmini yuklang\n\n"
            "Biometrik pasport (yashil) uchun 1 ta rasm:\n"
            "✓ Foto va ma'lumotlar sahifasi\n"
            "✓ Yaxshi sifatli\n"
            "✓ Barcha ma'lumotlar aniq ko'rinadi"
        ),
        'enter_passport_number': (
            "🔢 Pasport seriya va raqamini kiriting\n\n"
            "Misol: AA1234567"
        ),
        'enter_birth_date': (
            "📅 Tug'ilgan sanangizni kiriting\n\n"
            "Misol: 15.03.1990"
        ),
        'enter_pinfl': (
            "🆔 PINFL raqamingizni kiriting\n\n"
            "PINFL - 14 xonali shaxsiy identifikatsiya raqami\n\n"
            "PINFL ni pasportingizdan topishingiz mumkin"
        ),
        'enter_address': (
            "📍 To'liq yashash manzilingizni kiriting\n\n"
            "Misol:\n"
            "Toshkent sh., Chilonzor t.,\n"
            "Chigʻatoy 2B, 5-uy\n\n"
            "To'liq manzil: Viloyat, tuman, ko'cha, uy"
        ),
        'confirm_registration': (
            "✅ Ma'lumotlaringizni tekshiring:\n\n"
            "👤 F.I.O: {fullname}\n"
            "📱 Telefon: {phone}\n"
            "🆔 Pasport: {passport}\n"
            "📅 Tug'ilgan: {birth_date}\n"
            "🔢 PINFL: {pinfl}\n"
            "📍 Manzil: {address}\n\n"
            "To'g'rimi?"
        ),
        'registration_submitted': (
            "📋 Ma'lumotlaringiz qabul qilindi!\n\n"
            "⏳ Admin tez orada ko'rib chiqadi va tasdiqlaydi.\n\n"
            "Sizga xabar keladi. Biroz kutib turing! 😊"
        ),
        'registration_approved': (
            "🎉 TABRIKLAYMIZ!\n\n"
            "Ma'lumotlaringiz tasdiqlandi!\n\n"
            "🆔 Sizning mijoz kodingiz: {client_code}\n"
            "📱 Telefon: {phone}\n\n"
            "⚠️ Bu ma'lumotlarni saqlang!\n"
            "Keyingi safar kirish uchun kerak bo'ladi."
        ),
        'registration_rejected': (
            "❌ Ma'lumotlaringiz rad etildi\n\n"
            "📝 Sabab:\n{reason}\n\n"
            "Iltimos, qaytadan to'g'ri ma'lumotlar bilan ro'yxatdan o'ting."
        ),
        
        # ==================== LOGIN ====================
        'enter_client_code': (
            "🔐 Mijoz kodingizni kiriting\n\n"
            "Format: AKB600, AKB601, ...\n\n"
            "Misol: AKB600"
        ),
        'enter_phone_verify': "📱 Telefon raqamingizni kiriting:",
        'login_success': "✅ Xush kelibsiz, {fullname}!",
        'login_failed': "❌ Mijoz kodi yoki telefon raqam noto'g'ri!\n\nQaytadan urinib ko'ring.",
        
        # ==================== PROFIL ====================
        'profile_info': (
            "👤 MENING PROFILIM\n\n"
            "👨‍💼 F.I.O: {fullname}\n"
            "🆔 Mijoz kodi: {client_code}\n"
            "📱 Telefon: {phone}\n"
            "🔖 Pasport: {passport}\n"
            "📅 Tug'ilgan: {birth_date}\n"
            "🔢 PINFL: {pinfl}\n"
            "📍 Manzil: {address}\n\n"
            "✅ Holat: {status}\n"
            "📅 Ro'yxat: {registered_at}"
        ),
        
        # ==================== XITOY MANZILI ====================
        'china_address_info': (
            "🇨🇳 XITOY SKLAD MANZILI\n\n"
            "收货人：{client_code}\n"
            "电话：18161955318\n"
            "西安市 雁塔区 丈八沟街道\n"
            "高新区丈八六路49号103室中京仓库 {client_code}\n\n"
            "⚠️ MUHIM OGOHLANTIRISH:\n\n"
            "Manzilni to'g'ri kiritganingizga ishonch hosil qiling!\n\n"
            "Admin tomonidan tasdiqlanmagan manzilga yuborilgan "
            "buyurtmalar uchun javobgarlik olinmaydi!\n\n"
            "Manzilni to'g'ri kiritganingizni tasdiqlaysizmi?"
        ),
        'china_address_confirmed': (
            "✅ Ajoyib!\n\n"
            "Endi siz xitoydan buyurtma berishingiz mumkin.\n\n"
            "Yuqoridagi manzilni nusxalab olganingizga ishonch hosil qiling! 🇨🇳"
        ),
        
        # ==================== QIDIRUV ====================
        'select_search_type': "Qanday qidirishni xohlaysiz?",
        'by_trek': "🔢 Trek kodi orqali",
        'by_my_code': "🆔 Mening yuklarim",
        'enter_trek_code': (
            "🔢 Trek kodni kiriting\n\n"
            "Bir nechta bo'lsa, vergul bilan ajrating:\n"
            "Misol: TRACK001, TRACK002, TRACK003"
        ),
        'shipment_found': "✅ Yuk topildi!",
        'shipment_not_found': "❌ Trek kod topilmadi: {code}",
        'my_shipments': "📦 Mening yuklarim ({count} ta):",
        'no_shipments': "📭 Sizda hali yuklar yo'q",
        'shipment_details': (
            "📦 {name}\n"
            "🔢 Trek: {tracking}\n"
            "📍 Paket: {package}\n"
            "⚖️ Vazn: {weight} kg\n"
            "🔢 Miqdor: {quantity}\n"
            "✈️ Parvoz: {flight}"
        ),
        
        # ==================== FEEDBACK ====================
        'enter_feedback': (
            "💬 Fikr-mulohazangizni yozing\n\n"
            "Savolingiz bo'lsa ham yozishingiz mumkin.\n"
            "Admin tez orada javob beradi."
        ),
        'feedback_sent': "✅ Xabaringiz yuborildi! Admin tez orada javob beradi.",
        'feedback_reply': "💬 Admin javobi:\n\n{reply}",
        
        # ==================== ADMIN ====================
        'admin_welcome': (
            "⚙️ ADMIN PANEL\n\n"
            "Quyidagi funksiyalardan foydalanishingiz mumkin:"
        ),
        'admin_user_info': (
            "👤 FOYDALANUVCHI\n\n"
            "🆔 ID: {user_id}\n"
            "👨‍💼 Ism: {fullname}\n"
            "📱 Telefon: {phone}\n"
            "🔖 Pasport: {passport}\n"
            "📅 Tug'ilgan: {birth_date}\n"
            "🔢 PINFL: {pinfl}\n"
            "📍 Manzil: {address}\n\n"
            "✅ Holat: {status}\n"
            "📅 Ro'yxat: {registered_at}"
        ),
        'approve_user': "✅ Tasdiqlash",
        'reject_user': "❌ Rad etish",
        'edit_user': "✏️ Tahrirlash",
        'delete_user': "🗑 O'chirish",
        'enter_rejection_reason': "📝 Rad etish sababini yozing:",
        'user_approved': "✅ Foydalanuvchi tasdiqlandi!",
        'user_rejected': "❌ Foydalanuvchi rad etildi.",
        'enter_broadcast_message': (
            "📢 XABAR YUBORISH\n\n"
            "Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yozing:"
        ),
        'broadcast_confirm': (
            "📢 Xabar {count} ta foydalanuvchiga yuborilsinmi?\n\n"
            "Xabar:\n{message}"
        ),
        'broadcast_sending': "📤 Xabar yuborilmoqda...",
        'broadcast_completed': "✅ Xabar {sent}/{total} ta foydalanuvchiga yuborildi!",
        'enter_user_search': "🔍 Mijoz kodini yoki telefon raqamini kiriting:",
        'user_not_found': "❌ Foydalanuvchi topilmadi",
        
        # ==================== XATOLAR ====================
        'error_general': "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
        'error_photo': "❌ Rasm yuklashda xatolik. Qaytadan urinib ko'ring.",
        'error_validation': "❌ {error}",
        'invalid_command': "❌ Noto'g'ri buyruq. Quyidagi tugmalardan foydalaning.",
        'access_denied': "🚫 Sizda bu amalga ruxsat yo'q.",
        
        # ==================== PASSPORT EXPIRY ====================
        'passport_expiry_warning': (
            "⚠️ ESLATMA\n\n"
            "Pasportingiz muddati tez orada tugaydi:\n"
            "📅 Muddat: {expiry_date}\n\n"
            "Yangi pasport olishga tayyorgarlik ko'ring."
        ),
        'passport_expired': (
            "🚨 OGOHLANTIRISH\n\n"
            "Pasportingiz muddati tugagan!\n"
            "📅 Tugagan sana: {expiry_date}\n\n"
            "Yangi pasport olishingiz SHART!"
        ),
        
        # ==================== BOSHQALAR ====================
        'logout_confirm': "Haqiqatan ham chiqmoqchimisiz?",
        'logout_success': "👋 Tizimdan chiqdingiz. Qayta kirish uchun /start",
        'back_to_main': "Asosiy menyuga qaytdingiz.",
        'operation_cancelled': "❌ Amal bekor qilindi.",
        'contact_info': (
            "📞 KONTAKTLAR\n\n"
            "📱 Telefon: +998 XX XXX XX XX\n"
            "📧 Email: info@akbcargo.uz\n"
            "🌐 Website: www.akbcargo.uz\n"
            "📍 Manzil: Toshkent shahar\n\n"
            "Ish vaqti: 9:00 - 18:00"
        ),
        'language_changed_uz': "✅ Til o'zgartirildi: O'zbek",
        'language_changed_ru': "✅ Til o'zgartirildi: Русский",
    },
    
    # ==================== RUSCHA ====================
    'ru': {
        # Asosiy matnlar
        'welcome_new': (
            "👋 Здравствуйте!\n\n"
            "Добро пожаловать в бот AKB CARGO!\n\n"
            "Для использования бота необходимо зарегистрироваться."
        ),
        'welcome_registered': (
            "🎉 Добро пожаловать, {fullname}!\n\n"
            "📋 Ваша информация:\n"
            "🆔 Код клиента: {client_code}\n"
            "📱 Телефон: {phone}\n"
            "✅ Статус: {status}\n\n"
            "{status_message}"
        ),
        'status_pending': "⏳ Ваши данные на рассмотрении...",
        'status_approved': "✅ Подтверждено! Можете пользоваться всеми услугами.",
        'status_rejected': "❌ Ваши данные отклонены.\n\n📝 Причина: {reason}\n\nЗарегистрируйтесь заново.",
        
        # Tugmalar
        'register': "Регистрация 📝",
        'login': "Вход 🔐",
        'cancel': "Отмена ❌",
        'back': "⬅️ Назад",
        'confirm': "✅ Подтвердить",
        'search': "🔍 Поиск груза",
        'profile': "👤 Профиль",
        'feedback': "💬 Отзыв",
        'contacts': "📍 Контакты",
        'language': "🌐 Язык",
        'logout': "🚪 Выход",
        'china_address': "🇨🇳 Адрес в Китае",
        
        # Admin
        'admin_panel': "⚙️ Админ Панель",
        'manage_users': "👥 Пользователи",
        'add_user': "➕ Добавить пользователя",
        'search_user': "🔍 Найти пользователя",
        'upload_db': "📂 Загрузить базу",
        'broadcast': "📢 Рассылка",
        'admin_search': "🔎 Поиск трек-кода",
        
        # Ro'yxat
        'enter_fullname': (
            "👤 Введите ваше имя и фамилию:\n\n"
            "Пример: Алишер Навои"
        ),
        'enter_phone': (
            "📱 Введите номер телефона:\n\n"
            "Формат:\n"
            "• +998 XX XXX XX XX\n"
            "• 998 XX XXX XX XX\n"
            "• XX XXX XX XX\n\n"
            "Пример: 90 123 45 67"
        ),
        'select_passport_type': (
            "🆔 Какой у вас паспорт?\n\n"
            "ID карта (2 фото)\n"
            "Биометрический паспорт - Зелёный паспорт (1 фото)"
        ),
        'passport_id_card': "🆔 ID карта",
        'passport_booklet': "📖 Биометрический паспорт (зелёный)",
        'upload_passport_front': (
            "📸 Загрузите ЛИЦЕВУЮ сторону паспорта\n\n"
            "На фото:\n"
            "✓ Хорошее качество\n"
            "✓ Все данные видны\n"
            "✓ Углы прямые"
        ),
        'upload_passport_back': (
            "📸 Загрузите ОБРАТНУЮ сторону паспорта\n\n"
            "На фото:\n"
            "✓ Хорошее качество\n"
            "✓ Все данные видны\n"
            "✓ Углы прямые"
        ),
        'upload_passport_booklet': (
            "📸 Загрузите фото паспорта\n\n"
            "Для биометрического паспорта (зелёного) 1 фото:\n"
            "✓ Страница с фото и данными\n"
            "✓ Хорошее качество\n"
            "✓ Все данные видны"
        ),
        'enter_passport_number': (
            "🔢 Введите серию и номер паспорта\n\n"
            "Формат: AA1234567\n\n"
            "Допустимы:\n"
            "• AA, AB, AD, AE (Узбекистан)\n"
            "• Начинающиеся с K (Каракалпакстан)\n\n"
            "Пример: AA1234567, KA7654321"
        ),
        'enter_birth_date': (
            "📅 Введите дату рождения\n\n"
            "Формат: день.месяц.год\n\n"
            "Пример: 15.03.1990"
        ),
        'enter_pinfl': (
            "🆔 Введите номер ПИНФЛ\n\n"
            "ПИНФЛ - 14-значный личный идентификационный номер\n\n"
            "ПИНФЛ можно найти в паспорте"
        ),
        'enter_address': (
            "📍 Введите полный адрес проживания\n\n"
            "Пример:\n"
            "г. Ташкент, Чиланзарский р-н,\n"
            "ул. Чигатой 2Б, дом 5\n\n"
            "Полный адрес: Область, район, улица, дом"
        ),
        'confirm_registration': (
            "✅ Проверьте ваши данные:\n\n"
            "👤 Ф.И.О: {fullname}\n"
            "📱 Телефон: {phone}\n"
            "🆔 Паспорт: {passport}\n"
            "📅 Дата рожд.: {birth_date}\n"
            "🔢 ПИНФЛ: {pinfl}\n"
            "📍 Адрес: {address}\n\n"
            "Все верно?"
        ),
        'registration_submitted': (
            "📋 Ваши данные приняты!\n\n"
            "⏳ Администратор скоро проверит и подтвердит.\n\n"
            "Вам придет уведомление. Подождите! 😊"
        ),
        'registration_approved': (
            "🎉 ПОЗДРАВЛЯЕМ!\n\n"
            "Ваши данные подтверждены!\n\n"
            "🆔 Ваш код клиента: {client_code}\n"
            "📱 Телефон: {phone}\n\n"
            "⚠️ Сохраните эти данные!\n"
            "Они понадобятся для входа."
        ),
        'registration_rejected': (
            "❌ Ваши данные отклонены\n\n"
            "📝 Причина:\n{reason}\n\n"
            "Пожалуйста, зарегистрируйтесь заново с правильными данными."
        ),
        
        # Login
        'enter_client_code': (
            "🔐 Введите ваш код клиента\n\n"
            "Формат: AKB600, AKB601, ...\n\n"
            "Пример: AKB600"
        ),
        'enter_phone_verify': "📱 Введите ваш номер телефона:",
        'login_success': "✅ Добро пожаловать, {fullname}!",
        'login_failed': "❌ Код клиента или номер телефона неверны!\n\nПопробуйте снова.",
        
        # Profil
        'profile_info': (
            "👤 МОЙ ПРОФИЛЬ\n\n"
            "👨‍💼 Ф.И.О: {fullname}\n"
            "🆔 Код: {client_code}\n"
            "📱 Телефон: {phone}\n"
            "🔖 Паспорт: {passport}\n"
            "📅 Дата рожд.: {birth_date}\n"
            "🔢 ПИНФЛ: {pinfl}\n"
            "📍 Адрес: {address}\n\n"
            "✅ Статус: {status}\n"
            "📅 Регистрация: {registered_at}"
        ),
        
        # Xitoy
        'china_address_info': (
            "🇨🇳 АДРЕС СКЛАДА В КИТАЕ\n\n"
            "收货人：{client_code}\n"
            "电话：18161955318\n"
            "西安市 雁塔区 丈八沟街道\n"
            "高新区丈八六路49号103室中京仓库 {client_code}\n\n"
            "⚠️ ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ:\n\n"
            "Убедитесь, что правильно указали адрес!\n\n"
            "Ответственность за заказы, отправленные на неподтвержденный "
            "администратором адрес, не принимается!\n\n"
            "Подтверждаете, что правильно указали адрес?"
        ),
        'china_address_confirmed': (
            "✅ Отлично!\n\n"
            "Теперь вы можете заказывать из Китая.\n\n"
            "Убедитесь, что скопировали адрес выше! 🇨🇳"
        ),
        
        # Qidiruv
        'select_search_type': "Как хотите искать?",
        'by_trek': "🔢 По трек-коду",
        'by_my_code': "🆔 Мои грузы",
        'enter_trek_code': (
            "🔢 Введите трек-код\n\n"
            "Если несколько, разделите запятыми:\n"
            "Пример: TRACK001, TRACK002, TRACK003"
        ),
        'shipment_found': "✅ Груз найден!",
        'shipment_not_found': "❌ Трек-код не найден: {code}",
        'my_shipments': "📦 Мои грузы ({count} шт):",
        'no_shipments': "📭 У вас пока нет грузов",
        'shipment_details': (
            "📦 {name}\n"
            "🔢 Трек: {tracking}\n"
            "📍 Пакет: {package}\n"
            "⚖️ Вес: {weight} кг\n"
            "🔢 Количество: {quantity}\n"
            "✈️ Рейс: {flight}"
        ),
        
        # Feedback
        'enter_feedback': (
            "💬 Напишите ваш отзыв\n\n"
            "Если есть вопрос, тоже можете написать.\n"
            "Администратор скоро ответит."
        ),
        'feedback_sent': "✅ Ваше сообщение отправлено! Админ скоро ответит.",
        'feedback_reply': "💬 Ответ администратора:\n\n{reply}",
        
        # Admin
        'admin_welcome': (
            "⚙️ ПАНЕЛЬ АДМИНИСТРАТОРА\n\n"
            "Доступные функции:"
        ),
        'admin_user_info': (
            "👤 ПОЛЬЗОВАТЕЛЬ\n\n"
            "🆔 ID: {user_id}\n"
            "👨‍💼 Имя: {fullname}\n"
            "📱 Телефон: {phone}\n"
            "🔖 Паспорт: {passport}\n"
            "📅 Дата рожд.: {birth_date}\n"
            "🔢 ПИНФЛ: {pinfl}\n"
            "📍 Адрес: {address}\n\n"
            "✅ Статус: {status}\n"
            "📅 Регистрация: {registered_at}"
        ),
        'approve_user': "✅ Подтвердить",
        'reject_user': "❌ Отклонить",
        'edit_user': "✏️ Редактировать",
        'delete_user': "🗑 Удалить",
        'enter_rejection_reason': "📝 Напишите причину отклонения:",
        'user_approved': "✅ Пользователь подтвержден!",
        'user_rejected': "❌ Пользователь отклонен.",
        'enter_broadcast_message': (
            "📢 РАССЫЛКА\n\n"
            "Напишите сообщение для всех пользователей:"
        ),
        'broadcast_confirm': (
            "📢 Отправить сообщение {count} пользователям?\n\n"
            "Сообщение:\n{message}"
        ),
        'broadcast_sending': "📤 Отправка сообщения...",
        'broadcast_completed': "✅ Сообщение отправлено {sent}/{total} пользователям!",
        'enter_user_search': "🔍 Введите код клиента или номер телефона:",
        'user_not_found': "❌ Пользователь не найден",
        
        # Xatolar
        'error_general': "❌ Произошла ошибка. Попробуйте еще раз.",
        'error_photo': "❌ Ошибка загрузки фото. Попробуйте еще раз.",
        'error_validation': "❌ {error}",
        'invalid_command': "❌ Неверная команда. Используйте кнопки ниже.",
        'access_denied': "🚫 У вас нет доступа к этой функции.",
        
        # Passport expiry
        'passport_expiry_warning': (
            "⚠️ НАПОМИНАНИЕ\n\n"
            "Срок действия вашего паспорта скоро истекает:\n"
            "📅 Срок: {expiry_date}\n\n"
            "Подготовьтесь к получению нового паспорта."
        ),
        'passport_expired': (
            "🚨 ПРЕДУПРЕЖДЕНИЕ\n\n"
            "Срок действия вашего паспорта истек!\n"
            "📅 Истек: {expiry_date}\n\n"
            "Необходимо получить новый паспорт!"
        ),
        
        # Boshqalar
        'logout_confirm': "Вы действительно хотите выйти?",
        'logout_success': "👋 Вы вышли из системы. Для входа /start",
        'back_to_main': "Вы вернулись в главное меню.",
        'operation_cancelled': "❌ Операция отменена.",
        'contact_info': (
            "📞 КОНТАКТЫ\n\n"
            "📱 Телефон: +998 XX XXX XX XX\n"
            "📧 Email: info@akbcargo.uz\n"
            "🌐 Website: www.akbcargo.uz\n"
            "📍 Адрес: г. Ташкент\n\n"
            "Рабочее время: 9:00 - 18:00"
        ),
        'language_changed_uz': "✅ Язык изменён: O'zbek",
        'language_changed_ru': "✅ Язык изменён: Русский",
    }
}


def get_text(lang: str, key: str, **kwargs) -> str:
    """
    Til bo'yicha matnni olish
    
    Args:
        lang: Til kodi ('uz' yoki 'ru')
        key: Matn kaliti
        **kwargs: Format parametrlari
        
    Returns:
        Formatlanangan matn
    """
    text = TEXTS.get(lang, TEXTS['uz']).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError as e:
            return text
    return text
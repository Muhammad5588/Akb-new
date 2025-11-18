# ==================== STATES ====================

from aiogram.filters.state import State, StatesGroup

class AdminStates(StatesGroup):
    in_admin_panel = State()
    entering_rejection_reason = State()
    searching_user = State()
    entering_broadcast_message = State()
    uploading_database = State()
    admin_searching_trek = State()
    replying_to_feedback = State()
    bulk_importing_users = State()
    user_exel_importing_process = State()
    
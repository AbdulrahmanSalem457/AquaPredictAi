# =====================================================================
# ملف الإعدادات المركزية المحدث (Configuration Management)
# الوظيفة: قراءة المتغيرات البيئية والأمان من ملف .env بطريقة آمنة
# =====================================================================

from pydantic_settings import BaseSettings, SettingsConfigDict
import os

# تحديد مسار المجلد الحالي لضمان قراءة ملف .env بدقة من أي مكان
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    """
    فئة إعدادات النظام (Settings Class)
    تقوم بقراءة البيانات الآمنة والتأكد من وجود ملف .env في المجلد الرئيسي
    """
    SECRET_API_KEY: str = "AQUA_SECURE_KEY_2026"
    TELEGRAM_BOT_TOKEN: str = "8783164450:AAGdZGpWaz6bzaimOdRaf95EhQP1mswC5mE"
    TELEGRAM_CHAT_ID: str = "1078743972"

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
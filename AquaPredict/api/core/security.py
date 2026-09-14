# =====================================================================
# ملف الأمان والتحقق من الهوية (Security & Authentication)
# الوظيفة: التحقق من مفتاح الحماية (API Key) المرفق مع كل طلب لضمان الأمان
# =====================================================================

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from api.core.config import settings

# تحديد اسم الهيدر المطلوب استقباله في الطلبات وبرمجته
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    دالة التحقق من صحة مفتاح الـ API
    تقارن المفتاح المرسل مع المفتاح المخزن سراً في ملف الإعدادات (config.py)
    """
    if api_key != settings.SECRET_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="عذراً يا مهندس، مفتاح المرور (API Key) غير صحيح أو غير مسموح بالوصول!"
        )
    return api_key
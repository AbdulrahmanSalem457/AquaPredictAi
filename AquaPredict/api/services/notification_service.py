# =====================================================================
# خدمة التنبيهات والاتصال بتليجرام (Telegram Notification Service)
# الوظيفة: إرسال التنبيهات والتقارير الهندسية الحية إلى مستخدم النظام عبر بوت تليجرام
# =====================================================================

import requests
from api.core.config import settings

class NotificationService:
    """
    فئة إدارة الإشعارات والتنبيهات
    تستخدم المتغيرات البيئية الآمنة لربط البوت وإرسال الرسائل
    """
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_alert(self, message: str) -> bool:
        """
        دالة إرسال رسالة تنبيه نصية عبر تليجرام
        
        المعاملات:
            - message (str): نص الرسالة أو التقرير الهندسي
        المخرجات:
            - bool: True في حال نجاح الإرسال، و False في حال الفشل
        """
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(self.base_url, json=payload, timeout=5)
            if response.status_code == 200:
                print("📲 تم إرسال تنبيه تليجرام بنجاح!")
                return True
            else:
                print(f"⚠️ فشل إرسال تليجرام، كود الاستجابة: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ خطأ شبكي أثناء محاولة إرسال تنبيه تليجرام: {str(e)}")
            return False

# إنشاء كائن عام للاستخدام المباشر في خدمات المحطة
notification_service = NotificationService()
# =====================================================================
# خدمة المساعد الصوتي والتحكم الذكي (Voice Assistant & Intent Service)
# الوظيفة: تحليل الأوامر الصادرة صوتياً، استخراج النوايا، والتحقق من سلامتها
# =====================================================================

class VoiceAssistantService:
    """
    فئة المساعد الصوتي الصناعي
    تقوم بتحويل النصوص الصوتية إلى نوايا وأوامر تشغيلية معتمدة بعد فحص الأمان
    """
    def __init__(self):
        # قاموس النوايا المدعومة والمطابقة لأوامر المحطة
        self.supported_intents = {
            "إيقاف المضخة": "SHUTDOWN_MAIN_PUMP",
            "وقف المضخة الرئيسية": "SHUTDOWN_MAIN_PUMP",
            "stop pump": "SHUTDOWN_MAIN_PUMP",
            "الغسيل العكسي": "TRIGGER_BACKWASH",
            "تنظيف الأغشية": "TRIGGER_BACKWASH",
            "backwash": "TRIGGER_BACKWASH",
            "حالة المحطة": "GET_STATION_STATUS",
            "status": "GET_STATION_STATUS"
        }

    def process_voice_command(self, transcribed_text: str) -> dict:
        """
        دالة معالجة النص المستخرج من الصوت واستخراج النوايا التشغيلية
        
        المعاملات:
            - transcribed_text (str): النص الكلامي المحول من التسجيل الصوتي
            
        المخرجات:
            - dict: تفاصيل النية، درجة الثقة، والإجراء الأمني المقترح
        """
        clean_text = transcribed_text.strip().lower()
        detected_intent = "UNKNOWN_INTENT"
        mapped_command = "NONE"
        confidence = 0.45
        requires_confirmation = False

        # مطابقة النص مع النوايا المعروفة
        for phrase, command in self.supported_intents.items():
            if phrase in clean_text:
                detected_intent = f"INTENT_{command}"
                mapped_command = command
                confidence = 0.95
                break

        # تحديد ما إذا كان الأمر خطيراً ويحتاج خطوة تأكيد إضافية
        critical_commands = ["SHUTDOWN_MAIN_PUMP"]
        if mapped_command in critical_commands:
            requires_confirmation = True

        safety_message = "الأمر آمن ومقبول للتنفيذ."
        if requires_confirmation:
            safety_message = "⚠️ تنبيه حرج: هذا الأمر يتطلب تأكيداً ثنائياً قبل إرساله لمحول التنفيذ."

        return {
            "original_text": transcribed_text,
            "detected_intent": detected_intent,
            "mapped_command": mapped_command,
            "confidence_score": confidence,
            "requires_confirmation": requires_confirmation,
            "safety_validation_message": safety_message
        }

# إنشاء كائن عام للاستخدام في مسارات الـ API الخاصة بالصوت
voice_assistant = VoiceAssistantService()
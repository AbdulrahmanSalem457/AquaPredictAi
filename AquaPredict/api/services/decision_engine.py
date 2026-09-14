# =====================================================================
# محرك القرار وسلامة المحطة (Decision & Safety Engine)
# الوظيفة: تقييم حالة الحساسات، اتخاذ القرارات الصناعية الحرجة، وتوجيه الإشعارات
# =====================================================================

from datetime import datetime
from api.services.notification_service import notification_service
from api.database.database import get_db_connection

class DecisionEngine:
    """
    فئة محرك القرار
    تقوم بتحليل درجات الخطورة وإصدار التوصيات وتوثيق تذاكر الصيانة
    """
    def __init__(self):
        # تتبع الحالة السابقة لمنع إرسال تنبيهات مكررة لنفس المشكلة
        self.last_status = {"fouling": False, "pump_danger": False}

    def evaluate_and_decide(self, sensors_data: dict) -> dict:
        """
        دالة تقييم البيانات واتخاذ القرار التشغيلي
        
        المعاملات:
            - sensors_data (dict): قراءات الحساسات الحية
        المخرجات:
            - dict: القرار النهائي، الإجراء الموصى به، ومستوى الخطورة
        """
        pressure = sensors_data.get("Pressure", 0.0)
        turbidity = sensors_data.get("Turbidity", 0.0)
        vibration = sensors_data.get("Vibration", 0.0)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        recommended_action = "NONE"
        station_status = "Safe"
        severity = "LOW"
        telegram_sent = False

        # 1. فحص خطر المضخة الرئيسية (الحالة الحرجة جداً)
        is_pump_danger = (pressure > 95.0 or vibration > 4.5)
        if is_pump_danger:
            station_status = "CRITICAL_PUMP_RISK"
            recommended_action = "SHUTDOWN_MAIN_PUMP"
            severity = "CRITICAL"

            if not self.last_status["pump_danger"]:
                # إنشاء تذكرة صيانة عاجلة وإسنادها للفني المسؤول
                self._create_maintenance_ticket("High", "خطر اهتزاز أو ضغط بالمضخة - يتطلب إيقاف فوري", "م. محمود الباز")
                
                # إرسال تنبيه فوري عبر تليجرام
                alert_msg = f"🚨 *[AquaPredict EMERGENCY]* خطر بالمضخة الرئيسية!\n- الضغط: {pressure} Bar\n- الاهتزاز: {vibration} mm/s\n📌 *الإجراء المقترح:* إيقاف المضخة فوراً."
                notification_service.send_alert(alert_msg)
                
                self.last_status["pump_danger"] = True
                telegram_sent = True
        else:
            self.last_status["pump_danger"] = False

        # 2. فحص ترسبات الأغشية (حالة تحذيرية)
        is_fouling = (turbidity > 2.5 or pressure > 80.0) and not is_pump_danger
        if is_fouling:
            station_status = "WARNING_MEMBRANE_FOULING"
            recommended_action = "TRIGGER_BACKWASH"
            severity = "MEDIUM"

            if not self.last_status["fouling"]:
                # إنشاء تذكرة صيانة متوسطة وإسنادها للفني المختص
                self._create_maintenance_ticket("Medium", "ترسبات محتملة على الأغشية - يتطلب غسيل عكسي", "م. أحمد الشناوي")
                
                # إرسال تنبيه عبر تليجرام
                alert_msg = f"⚠️ *[AquaPredict Warning]* ترسبات على الأغشية!\n- الضغط: {pressure} Bar\n- التعكر: {turbidity} NTU\n📌 *الإجراء المقترح:* تشغيل الغسيل العكسي."
                notification_service.send_alert(alert_msg)
                
                self.last_status["fouling"] = True
                telegram_sent = True
        else:
            self.last_status["fouling"] = False

        return {
            "timestamp": now,
            "station_status": station_status,
            "severity": severity,
            "recommended_action": recommended_action,
            "telegram_notification_sent": telegram_sent
        }

    def _create_maintenance_ticket(self, priority: str, description: str, technician: str):
        """
        دالة مساعدة لإنشاء تذكرة صيانة وتخزينها في قاعدة البيانات أتمتياً
        """
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO maintenance_tickets (timestamp, priority_level, issue_description, assigned_technician, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (now, priority, description, technician, "Pending"))
            conn.commit()
            conn.close()
            # تم تصحيح حرف الطباعة هنا ليعمل f-string بشكل سليم
            print(f"🎫 تم إنشاء تذكرة صيانة جديدة وأُسندت إلى: {technician}")
        except Exception as e:
            print(f"⚠️ فشل إنشاء تذكرة الصيانة: {str(e)}")

# إنشاء كائن عام للاستخدام في مسارات التحليل
decision_engine = DecisionEngine()
# =====================================================================
# خدمة الأمن السيبراني الصناعي (Industrial Cybersecurity Service)
# الوظيفة: فحص عناوين الـ IP، اكتشاف الأوامر غير المصرح بها، وتأمين شبكة المحطة
# =====================================================================

from datetime import datetime
from api.database.database import get_db_connection
from api.services.notification_service import notification_service

class IndustrialCybersecurity:
    """
    فئة إدارة وحماية الأمن السيبراني
    تقوم بالتحقق من مصدر الطلبات (IP) ونوع الأوامر لحماية المحطة من الاختراق
    """
    def __init__(self):
        # قائمة عناوين الـ IP الموثوقة والمصرح لها بإرسال أوامر تحكم للمحطة
        self.whitelisted_ips = ["127.0.0.1", "192.168.1.50", "10.0.0.15"]

    def inspect_command_request(self, client_ip: str, command_name: str) -> dict:
        """
        دالة فحص الطلب الوارد للتأكد من أمانه السيبراني
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        is_authorized_ip = client_ip in self.whitelisted_ips
        
        # قائمة الأوامر الخطيرة التي تتطلب صلاحيات صارمة
        critical_commands = ["SHUTDOWN_MAIN_PUMP", "OVERRIDE_VALVES"]
        is_critical = command_name in critical_commands

        threat_detected = False
        attack_type = "NONE"
        action_taken = "ALLOW"
        block_status = "PASSED"

        # 1. فحص ما إذا كان الـ IP غير مرخص
        if not is_authorized_ip:
            threat_detected = True
            attack_type = "UNAUTHORIZED_IP_COMMAND_ATTEMPT"
            action_taken = "BLOCK_REQUEST"
            block_status = "BLOCKED_SIMULATED"
        elif is_critical and client_ip != "127.0.0.1":
            threat_detected = True
            attack_type = "SUSPICIOUS_CRITICAL_COMMAND"
            action_taken = "REQUIRE_ADDITIONAL_AUTH"
            block_status = "CHALLENGED"

        # تسجيل الحدث السيبراني في قاعدة البيانات
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO cybersecurity_logs (timestamp, source_ip, attack_type, action_taken, block_status)
                VALUES (?, ?, ?, ?, ?)
            ''', (now, client_ip, attack_type, action_taken, block_status))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ خطأ أثناء حفظ سجل الأمن السيبراني: {str(e)}")

        if threat_detected:
            alert_msg = f"🛡️ *[AquaPredict Security Alert]* محاولة اختراق سيبراني!\n- المصدر IP: `{client_ip}`\n- الأمر المستهدف: `{command_name}`\n- الإجراء: `{action_taken}`"
            notification_service.send_alert(alert_msg)

        return {
            "timestamp": now,
            "client_ip": client_ip,
            "threat_detected": threat_detected,
            "attack_type": attack_type,
            "action_taken": action_taken,
            "block_status": block_status
        }

# إنشاء كائن عام للاستخدام في مسارات النظام
cybersecurity_guard = IndustrialCybersecurity()
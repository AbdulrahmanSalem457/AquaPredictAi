# =====================================================================
# محول المحاكاة الصناعية (Simulation Actuator Adapter)
# الوظيفة: تنفيذ الأوامر التشغيلية في بيئة محاكاة رقمية (Digital Twin Simulation)
# =====================================================================

from datetime import datetime
import logging

# إعداد نظام تسجيل الأحداث (Logging) لمتابعة الأوامر المنفذة
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SimulationAdapter")

class SimulationAdapter:
    """
    فئة محول المحاكاة
    تمثل الواجهة البرمجية (Interface) لتنفيذ الأوامر في بيئة افتراضية
    """
    
    def __init__(self):
        self.mode = "SIMULATION"

    def execute_command(self, command_name: str, parameters: dict = None) -> dict:
        """
        دالة تنفيذ الأمر التشغيلي في وضع المحاكاة
        
        المعاملات (Parameters):
            - command_name (str): اسم الأمر المراد تنفيذه (مثل: SHUTDOWN_MAIN_PUMP)
            - parameters (dict): أي بيانات إضافية مرتبطة بالأمر
            
        المخرجات (Returns):
            - dict: نتيجة التنفيذ وحالة المحاكاة
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"[{timestamp}] [SIMULATION MODE] Executing command: {command_name} with params: {parameters}")

        # محاكاة الاستجابة الناجحة لتنفيذ الأمر
        execution_result = {
            "execution_mode": self.mode,
            "command": command_name,
            "execution_status": "SIMULATED_SUCCESS",
            "timestamp": timestamp,
            "message": f"تم تنفيذ الأمر '{command_name}' بنجاح في بيئة المحاكاة التوأم الرقمي."
        }

        return execution_result

# إنشاء كائن عام للاستخدام المباشر في المسارات (Routes)
simulation_adapter = SimulationAdapter()
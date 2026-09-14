# =====================================================================
# مسارات الأتمتة وتنفيذ الأوامر (Automation & Command Execution Routes)
# الوظيفة: استقبال الأوامر التشغيلية، التحقق منها، وتوجيهها عبر محول المحاكاة (Simulation Adapter)
# =====================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime

# استيراد حارس الأمان ومحول المحاكاة وقاعدة البيانات
from api.core.security import verify_api_key
from api.integrations.simulation_adapter import simulation_adapter
from api.database.database import get_db_connection

# إنشاء موجه مسارات (APIRouter) خاص بملف الأتمتة
router = APIRouter(
    prefix="/api/v1",
    tags=["Automation & Actuator Control"]
)

# نموذج استقبال بيانات الأمر التشغيلي (Pydantic Model)
class CommandExecutionRequest(BaseModel):
    command_name: str = Field(..., description="اسم الأمر المراد تنفيذه (مثل: SHUTDOWN_MAIN_PUMP)")
    parameters: dict = Field(default_factory=dict, description="معاملات وبيانات إضافية مرتبطة بالأمر")

@router.post("/commands/execute")
def execute_station_command(request: CommandExecutionRequest, api_key: str = Depends(verify_api_key)):
    """
    مسار تنفيذ الأوامر عبر محول المحاكاة (Execution Phase)
    يستقبل الأمر، يمرره لمحول المحاكاة، يسجل الحدث في قاعدة البيانات، ويرجع نتيجة التنفيذ
    """
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # تنفيذ الأمر باستخدام محول المحاكاة (Simulation Adapter)
        execution_response = simulation_adapter.execute_command(
            command_name=request.command_name,
            parameters=request.parameters
        )

        # تخزين سجل عملية التنفيذ في جدول طوارئ المحطة
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO emergency_logs (timestamp, pressure, turbidity, vibration, anomaly_detected, station_status, automated_action)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            now, 
            0.0, 
            0.0, 
            0.0, 
            False, 
            "AUTOMATED_COMMAND_EXECUTED", 
            request.command_name
        ))
        conn.commit()
        conn.close()

        return {
            "success": True,
            "timestamp": now,
            "execution_details": execution_response,
            "message": f"تم معالجة وتفيذ الأمر '{request.command_name}' بنجاح."
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"حدث خطأ داخلي أثناء تنفيذ الأمر التشغيلي: {str(e)}"
        )
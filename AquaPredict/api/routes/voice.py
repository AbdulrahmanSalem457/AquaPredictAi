# =====================================================================
# مسار المساعد الصوتي والتحكم الذكي (Voice Control API Routes)
# الوظيفة: استقبال الأوامر الصوتية النصية، تحليلها أمنياً، وتنفيذها عبر محول المحاكاة
# =====================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime

# استيراد حارس الأمان، خدمة المساعد الصوتي، ومحول المحاكاة وقاعدة البيانات
from api.core.security import verify_api_key
from api.services.voice_service import voice_assistant
from api.integrations.simulation_adapter import simulation_adapter
from api.database.database import get_db_connection

# إنشاء موجه مسارات (APIRouter) خاص بالتحكم الصوتي
router = APIRouter(
    prefix="/api/v1",
    tags=["Voice Assistant & Speech Control"]
)

# نموذج استقبال بيانات الأمر الصوتي (Pydantic Model)
class VoiceCommandRequest(BaseModel):
    transcribed_text: str = Field(..., description="النص الكلامي المستخرج من الصوت (مثل: إيقاف المضخة)")
    confirmed: bool = Field(False, description="تأكيد تنفيذ الأوامر الحرجة (True إذا وافق المستخدم)")

@router.post("/voice/command")
def process_voice_endpoint(request: VoiceCommandRequest, api_key: str = Depends(verify_api_key)):
    """
    مسار معالجة الأوامر الصوتية (Voice Processing Pipeline)
    يحلل النص، يفحص الأمان، وينفذ الأمر إذا كان مأذوناً به أو مؤكداً
    """
    try:
        # 1. تحليل النص الصوتي واستخراج النية
        analysis = voice_assistant.process_voice_command(request.transcribed_text)
        
        command_to_execute = analysis["mapped_command"]
        requires_confirmation = analysis["requires_confirmation"]
        
        execution_response = None
        status_message = analysis["safety_validation_message"]

        # 2. التحقق من متطلبات التأكيد للأوامر الحرجة
        if requires_confirmation and not request.confirmed:
            return {
                "success": False,
                "status": "REQUIRES_CONFIRMATION",
                "analysis": analysis,
                "message": "⚠️ هذا الأمر حرج ويحتاج تأكيداً صريحاً (confirmed=True) قبل التنفيذ."
            }

        # 3. إذا كان الأمر صالحاً ومقبولاً، يتم تنفيذه عبر محول المحاكاة
        if command_to_execute != "NONE":
            execution_response = simulation_adapter.execute_command(
                command_name=command_to_execute,
                parameters={"source": "Voice Assistant", "original_phrase": request.transcribed_text}
            )
            status_message = f"تم تنفيذ الأمر الصوتي '{command_to_execute}' بنجاح."
        else:
            status_message = "لم يتم التعرف على أمر تشغيلي صالح في النص الصوتي المدخل."

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 4. توثيق الحدث في سجلات الطوارئ بقاعدة البيانات
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
            "VOICE_COMMAND_PROCESSED", 
            command_to_execute
        ))
        conn.commit()
        conn.close()

        return {
            "success": True,
            "timestamp": now,
            "voice_analysis": analysis,
            "execution_result": execution_response,
            "message": status_message
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"حدث خطأ داخلي أثناء معالجة الأمر الصوتي: {str(e)}"
        )
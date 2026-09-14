# =====================================================================
# مسارات مراقبة الحساسات والتحليل الصناعي المحدثة (Monitoring & Analysis Routes)
# الوظيفة: استقبال قراءات الحساسات، فحص الأمان السيبراني، تشغيل الذكاء الاصطناعي، وتوثيق القرارات
# =====================================================================

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# استيراد حارس الأمان، محرك القرار، وخدمة الأمن السيبراني
from api.core.security import verify_api_key
from api.services.decision_engine import decision_engine
from api.services.cyber_service import cybersecurity_guard
from api.database.database import get_db_connection

# إنشاء موجه مسارات (APIRouter) خاص بملف المراقبة
router = APIRouter(
    prefix="/api/v1",
    tags=["Monitoring, AI Analytics & Cybersecurity"]
)

# نموذج استقبال بيانات الحساسات والتحقق من صحتها (Pydantic Model)
class StationSensors(BaseModel):
    Pressure: float = Field(..., ge=0.0, le=250.0, description="ضغط التغذية (Bar)")
    Salinity: float = Field(..., ge=0.0, le=100000.0, description="الملوحة (PPM)")
    Temperature: float = Field(..., ge=0.0, le=100.0, description="درجة الحرارة (C)")
    Flow_Rate: float = Field(..., ge=0.0, le=500.0, description="معدل التدفق (m3/h)")
    pH: float = Field(..., ge=0.0, le=14.0, description="مستوى الحموضة")
    Turbidity: float = Field(..., ge=0.0, le=100.0, description="التعكر (NTU)")
    Vibration: float = Field(..., ge=0.0, le=100.0, description="الاهتزاز (mm/s)")

# تهيئة نماذج الذكاء الاصطناعي التجريبية
np.random.seed(42)
n_samples = 500
p_dummy = np.random.normal(65, 10, n_samples)
s_dummy = np.random.normal(35000, 3000, n_samples)
t_dummy = np.random.normal(25, 5, n_samples)
f_dummy = np.random.normal(100, 15, n_samples)
ph_dummy = np.random.normal(7.5, 0.5, n_samples)
turb_dummy = np.random.normal(1.5, 0.8, n_samples)
vib_dummy = np.random.normal(2.0, 1.2, n_samples)

training_df = pd.DataFrame({
    'Pressure': p_dummy, 'Salinity': s_dummy, 'Temperature': t_dummy,
    'Flow_Rate': f_dummy, 'pH': ph_dummy, 'Turbidity': turb_dummy, 'Vibration': vib_dummy
})

scaler = StandardScaler()
X_scaled = scaler.fit_transform(training_df)
ai_anomaly = IsolationForest(contamination=0.05, random_state=42).fit(X_scaled)

@router.post("/analyze")
def analyze_station_data(request: Request, sensors: StationSensors, api_key: str = Depends(verify_api_key)):
    """
    مسار تحليل حالة المحطة وقراءات الحساسات المتكامل (Detection & Security Phase)
    يقوم بفحص الـ IP سيبرانياً، تحليل الشذوذ بالذكاء الاصطناعي، اتخاذ القرار، وتخزين السجلات
    """
    try:
        # استخراج عنوان الـ IP الخاص بالمرسل
        client_ip = request.client.host if request.client else "127.0.0.1"
        
        # 1. فحص الأمن السيبراني للطلب
        cyber_check = cybersecurity_guard.inspect_command_request(client_ip, "ANALYZE_DATA")
        if cyber_check["threat_detected"] and cyber_check["action_taken"] == "BLOCK_REQUEST":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="⚠️ تم حظر الطلب أمنياً بسبب الاشتباه بسياسات الاتصال غير المصرح بها."
            )

        # 2. تحويل البيانات ومعالجة الذكاء الاصطناعي لشذوذ الحساسات
        input_data = pd.DataFrame([sensors.model_dump()])
        input_scaled = scaler.transform(input_data)
        anomaly_prediction = int(ai_anomaly.predict(input_scaled)[0])
        is_anomaly = True if anomaly_prediction == -1 else False

        # 3. تشغيل محرك القرار والسلامة الصناعية
        decision_result = decision_engine.evaluate_and_decide(sensors.model_dump())

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 4. تخزين السجلات في قاعدة البيانات
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # تخزين في مستودع البيانات الحية (Data Lake)
        cursor.execute('''
            INSERT INTO data_lake (pressure, salinity, temperature, flow_rate, ph, turbidity, vibration)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (sensors.Pressure, sensors.Salinity, sensors.Temperature, sensors.Flow_Rate, sensors.pH, sensors.Turbidity, sensors.Vibration))

        # تخزين في سجلات الطوارئ والحالة
        cursor.execute('''
            INSERT INTO emergency_logs (timestamp, pressure, turbidity, vibration, anomaly_detected, station_status, automated_action)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            now, 
            sensors.Pressure, 
            sensors.Turbidity, 
            sensors.Vibration, 
            is_anomaly, 
            decision_result["station_status"], 
            decision_result["recommended_action"]
        ))
        
        conn.commit()
        conn.close()

        return {
            "success": True,
            "timestamp": now,
            "client_ip": client_ip,
            "cybersecurity_status": cyber_check["block_status"],
            "anomaly_detected": is_anomaly,
            "station_status": decision_result["station_status"],
            "severity_level": decision_result["severity"],
            "recommended_action": decision_result["recommended_action"],
            "telegram_alert_sent": decision_result["telegram_notification_sent"],
            "message": "تم تحليل بيانات الحساسات، فحص الأمان، وتوثيق السجلات بنجاح."
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"حدث خطأ داخلي أثناء معالجة مسار التحليل: {str(e)}"
        )
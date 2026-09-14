# =====================================================================
# مشروع AquaPredict - واجهة برمجة التطبيقات الصناعية الشاملة (Enterprise API)
# النسخة النهائية المحدثة: منع تكرار التذاكر والسجلات، رسالة تليجرام ثنائية اللغة (عربي/إنجليزي)
# =====================================================================

from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.responses import StreamingResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
import sqlite3
from datetime import datetime, timedelta
import io
import os

app = FastAPI(
    title="AquaPredict Industrial Enterprise API",
    description="النظام الذكي المتكامل للتوأم الرقمي لمحطات التحلية",
    version="23.0"
)

SECRET_API_KEY = os.getenv("AQUA_API_KEY", "AQUA_SECURE_KEY_2026")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != SECRET_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="عذراً، مفتاح المرور غير صحيح!")
    return api_key_header

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8783164450:AAGdZGpWaz6bzaimOdRaf95EhQP1mswC5mE")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1078743972")

# حارس زمني لمنع تكرار إرسال رسائل تليجرام
last_alert_time = datetime.min
last_sent_severity = ""

def send_unique_telegram_alert(message: str, severity: str):
    global last_alert_time, last_sent_severity
    now = datetime.now()
    if (now - last_alert_time > timedelta(seconds=12)) or (severity != last_sent_severity):
        try:
            import requests
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
            response = requests.post(url, json=payload, timeout=3)
            if response.status_code == 200:
                last_alert_time = now
                last_sent_severity = severity
                return True
        except Exception as e:
            print(f"⚠️ فشل إرسال تليجرام: {e}")
    return False

conn = sqlite3.connect('station_database.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS emergency_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME, pressure REAL, turbidity REAL, vibration REAL, anomaly_detected BOOLEAN, station_status TEXT, automated_action TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS maintenance_tickets (ticket_id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME, priority_level TEXT, issue_description TEXT, assigned_technician TEXT, status TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS cybersecurity_logs (cyber_id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME, source_ip TEXT, attack_type TEXT, action_taken TEXT, block_status TEXT)''')
conn.commit()

class StationSensors(BaseModel):
    Pressure: float = Field(..., ge=0.0, le=250.0)
    Salinity: float = Field(..., ge=0.0, le=100000.0)
    Temperature: float = Field(..., ge=0.0, le=100.0)
    Flow_Rate: float = Field(..., ge=0.0, le=500.0)
    pH: float = Field(..., ge=0.0, le=14.0)
    Turbidity: float = Field(..., ge=0.0, le=100.0)
    Vibration: float = Field(..., ge=0.0, le=100.0)

class DesalinationInput(BaseModel):
    feed_tds_mgL: float = Field(..., ge=0.0, le=200000.0)
    feed_pressure_bar: float = Field(..., ge=0.0, le=400.0)
    feed_temp_C: float = Field(..., ge=0.0, le=150.0)
    feed_flow_m3h: float = Field(..., ge=0.0, le=2000.0)
    membrane_age_months: float = Field(..., ge=0.0, le=120.0)

class EnergyBrokerInput(BaseModel):
    electricity_price_kwh: float = Field(..., ge=0.0, le=10.0)
    water_demand_m3h: float = Field(..., ge=0.0, le=500.0)

class CavitationInput(BaseModel):
    audio_frequency_hz: float = Field(..., ge=0.0, le=20000.0)
    noise_decibels: float = Field(..., ge=0.0, le=120.0)

class SCADAPacketInput(BaseModel):
    source_ip: str
    sensor_pressure: float
    sensor_turbidity: float
    command_type: str

# تدريب النماذج
np.random.seed(42)
n_samples = 1000 
p_d = np.random.normal(65, 10, n_samples)
s_d = np.random.normal(38000, 2000, n_samples)
t_d = np.random.normal(26, 4, n_samples)
f_d = np.random.normal(100, 15, n_samples)
ph_d = np.random.normal(7.8, 0.3, n_samples)
turb_d = np.random.normal(1.2, 0.5, n_samples)
vib_d = np.random.normal(1.8, 0.9, n_samples)

f_status, p_status = [], []
for i in range(n_samples):
    f_status.append(1 if (turb_d[i] > 2.2 and p_d[i] > 75) else 0)
    p_status.append(1 if (vib_d[i] > 4.0 or p_d[i] > 90) else 0)

training_data = pd.DataFrame({'Pressure': p_d, 'Salinity': s_d, 'Temperature': t_d, 'Flow_Rate': f_d, 'pH': ph_d, 'Turbidity': turb_d, 'Vibration': vib_d})
scaler = StandardScaler()
X_scaled = scaler.fit_transform(training_data)
ai_fouling = RandomForestClassifier(n_estimators=50, random_state=42).fit(X_scaled, f_status)
ai_pump = RandomForestClassifier(n_estimators=50, random_state=42).fit(X_scaled, p_status)
ai_anomaly = IsolationForest(contamination=0.05, random_state=42).fit(X_scaled)

@app.get("/")
def read_root():
    return {"status": "online", "system": "AquaPredict Enterprise", "message": "محرك القرار المركزي يعمل بكفاءة تامة."}

# 🧠 محرك القرار المركزي مع مانع التكرار للاتصال وقاعدة البيانات وتليجرام
@app.post("/api/v1/decision-engine")
def run_decision_engine(sensors: StationSensors, api_key: str = Depends(get_api_key)):
    input_df = pd.DataFrame([sensors.model_dump()])
    input_scaled = scaler.transform(input_df)
    
    is_anomaly = int(ai_anomaly.predict(input_scaled)[0])
    fouling_prob = float(ai_fouling.predict_proba(input_scaled)[0][1] * 100)
    pump_prob = float(ai_pump.predict_proba(input_scaled)[0][1] * 100)
    
    risk_score = round(min(100.0, max(5.0, (max(0, sensors.Pressure - 60) * 0.8) + (max(0, sensors.Turbidity - 2.0) * 15.0) + (max(0, sensors.Vibration - 2.5) * 12.0))), 1)
    
    severity = "LOW"
    diagnosis_ar = "جميع قراءات الحساسات والمنظومة تعمل ضمن المعدلات الطبيعية والآمنة لمحطة الغردقة."
    diagnosis_en = "All sensor readings and system parameters operate within safe normal thresholds."
    
    recommendation_ar = "متابعة المراقبة اللحظية واستمرار التشغيل المتوازن."
    recommendation_en = "Continue real-time monitoring and maintain balanced plant operation."
    confidence = 94.2
    
    if risk_score > 75.0 or sensors.Vibration > 4.5:
        severity = "CRITICAL"
        diagnosis_ar = "خطر ميكانيكي حرج: ارتفاع حاد في اهتزاز المضخة أو الضغط يعرض المعدات للخطر."
        diagnosis_en = "Critical Mechanical Hazard: Sharp increase in pump vibration or pressure risks equipment failure."
        
        recommendation_ar = "إيقاف طارئ محاكى للمضخة وفحص محاور الدوران ورومان البلي فوراً."
        recommendation_en = "Initiate simulated emergency shutdown and inspect high-pressure pump shafts immediately."
        confidence = 96.5
    elif risk_score > 40.0 or sensors.Turbidity > 2.2 or sensors.Pressure > 80.0:
        severity = "HIGH"
        diagnosis_ar = "بداية ترسبات وتغيرات في غشاء التناضح العكسي (RO Membrane Fouling)."
        diagnosis_en = "Membrane fouling trend detected with rising feed pressure and turbidity."
        
        recommendation_ar = "جدولة دورة غسيل عكسي محاكاة وإطلاق نبضات ضغط ترددية لتفتيت الرواسب."
        recommendation_en = "Schedule adaptive membrane flushing simulation and trigger pressure pulses."
        confidence = 91.0

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ticket_id_created = "لا توجد / None (Safe)"
    
    # منع تكرار تسجيل تذاكر الصيانة إذا كانت آخر تذكرة مسجلة خلال آخر 15 ثانية بنفس الخطورة
    cursor.execute("SELECT timestamp, priority_level FROM maintenance_tickets ORDER BY ticket_id DESC LIMIT 1")
    last_ticket = cursor.fetchone()
    should_create_ticket = True
    if last_ticket:
        last_time = datetime.strptime(last_ticket[0], "%Y-%m-%d %H:%M:%S")
        if (datetime.now() - last_time).total_seconds() < 15 and last_ticket[1] == severity:
            should_create_ticket = False

    if severity in ["HIGH", "CRITICAL"] and should_create_ticket:
        cursor.execute('''INSERT INTO maintenance_tickets (timestamp, priority_level, issue_description, assigned_technician, status) VALUES (?, ?, ?, ?, ?)''', (now, severity, diagnosis_ar, "م. محمود الباز", "Pending"))
        conn.commit()
        cursor.execute("SELECT last_insert_rowid()")
        ticket_id_created = f"#Ticket-{cursor.fetchone()[0]}"

    # منع تكرار سجلات الطوارئ المتتالية في نفس الثانية
    cursor.execute("SELECT timestamp, pressure FROM emergency_logs ORDER BY id DESC LIMIT 1")
    last_log = cursor.fetchone()
    should_log = True
    if last_log:
        if last_log[0] == now and last_log[1] == sensors.Pressure:
            should_log = False

    if should_log:
        cursor.execute('''INSERT INTO emergency_logs (timestamp, pressure, turbidity, vibration, anomaly_detected, station_status, automated_action) VALUES (?, ?, ?, ?, ?, ?, ?)''', (now, sensors.Pressure, sensors.Turbidity, sensors.Vibration, True if is_anomaly == -1 else False, severity, recommendation_ar))
        conn.commit()

    # رسالة تليجرام ثنائية اللغة (عربي / إنجليزي) بدون تكرار
    bilingual_msg = (
        f"📊 *[تقرير غرفة عمليات محطة تحلية المياة]* 📊\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🚨 **مستوى الخطورة / Severity:** `{severity}` (Risk Score: {risk_score}/100)\n"
        f"🎯 **معامل الثقة / AI Confidence:** `{confidence}%`\n\n"
        f"🔍 **التشخيص الهندسي / Diagnosis:**\n"
        f"• {diagnosis_ar}\n"
        f"• *{diagnosis_en}*\n\n"
        f"📌 **التوصية التلقائية / Recommendation:**\n"
        f"• {recommendation_ar}\n"
        f"• *{recommendation_en}*\n\n"
        f"🎫 **تذكرة الصيانة / Auto-Ticket:** {ticket_id_created}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📈 *قراءات الحساسات الحية / Live Sensors:*\n"
        f"- الضغط / Pressure: `{sensors.Pressure} Bar`\n"
        f"- التعكر / Turbidity: `{sensors.Turbidity} NTU`\n"
        f"- الاهتزاز / Vibration: `{sensors.Vibration} mm/s`\n"
        f"- الملوحة / Salinity: `{sensors.Salinity} PPM`\n"
        f"- التدفق / Flow Rate: `{sensors.Flow_Rate} m3/h`\n"
        f"- الحرارة / Temperature: `{sensors.Temperature} °C`\n"
        f"🕒 **الوقت / Timestamp:** {now}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    send_unique_telegram_alert(bilingual_msg, severity)

    return {
        "success": True,
        "risk_score": risk_score,
        "severity": severity,
        "diagnosis": diagnosis_ar,
        "recommendation": recommendation_ar,
        "confidence_score": confidence,
        "ai_probabilities": {"fouling_pct": round(fouling_prob, 1), "pump_risk_pct": round(pump_prob, 1)}
    }

@app.get("/api/v1/logs")
def get_saved_logs(api_key: str = Depends(get_api_key)):
    cursor.execute('SELECT * FROM emergency_logs ORDER BY id DESC LIMIT 50')
    return {"recent_logs": cursor.fetchall()}

@app.get("/api/v1/maintenance-tickets")
def get_maintenance_tickets(api_key: str = Depends(get_api_key)):
    cursor.execute('SELECT * FROM maintenance_tickets ORDER BY ticket_id DESC LIMIT 10')
    return {"success": True, "tickets": cursor.fetchall()}

@app.post("/api/v1/predict-rul")
def predict_membrane_rul(sensors: StationSensors, api_key: str = Depends(get_api_key)):
    base_life_days = 730
    degradation = (sensors.Pressure * 2.5) + (sensors.Turbidity * 45.0) + (sensors.Vibration * 15.0)
    remaining_days = max(15, int(base_life_days - degradation))
    return {"success": True, "membrane_health_status": "Good" if remaining_days > 180 else "Needs_Inspection", "estimated_remaining_days": remaining_days, "confidence": 88.5}

@app.post("/api/v1/energy-efficiency")
def calculate_energy_efficiency(sensors: StationSensors, power_kw: float = 45.0, api_key: str = Depends(get_api_key)):
    produced_water = sensors.Flow_Rate * 0.55 
    sec = round(power_kw / (produced_water + 1e-5), 2)
    return {"success": True, "specific_energy_consumption_kwh_m3": sec, "efficiency_status": "Optimal" if sec <= 3.8 else "High_Energy_Consumption"}

@app.post("/api/v1/predict-desalination-performance")
def predict_desalination_performance(data: DesalinationInput, api_key: str = Depends(get_api_key)):
    perm_tds = round(data.feed_tds_mgL * 0.012, 2)
    recovery = 50.0 + (data.feed_pressure_bar * 0.1)
    sec = round(3.2 + (data.feed_tds_mgL / 25000.0), 2)
    salt_rejection = round(99.2 - (data.feed_pressure_bar * 0.01), 2)
    return {"success": True, "predictions": {"permeate_tds_mgL": perm_tds, "recovery_pct": round(recovery, 2), "sec_kwh_m3": sec, "salt_rejection_pct": salt_rejection}}

@app.post("/api/v1/forecast")
def forecast_future_performance(sensors: StationSensors, api_key: str = Depends(get_api_key)):
    forecast_data = [{"month": f"الشهر {m}", "predicted_tds": round(350.0 + (m * 12.5), 2), "predicted_sec": round(3.1 + (m * 0.08), 2)} for m in range(1, 7)]
    return {"success": True, "forecast": forecast_data}

@app.post("/api/v1/self-healing-pulse")
def trigger_self_healing_pulse(sensors: StationSensors, api_key: str = Depends(get_api_key)):
    fouling_index = (sensors.Pressure * 0.45) + (sensors.Turbidity * 16.0)
    pulse_action = "SIMULATE_MICRO_PULSE" if fouling_index > 65.0 else "NORMAL_OPERATION"
    status_msg = "⚠️ محاكاة تكيفية: رصد الترسبات - إطلاق ملف نبضات ضغط محاكاة لتفتيت الرواسب." if fouling_index > 65.0 else "🟢 حالة الأغشية مستقرة."
    return {"success": True, "calculated_fouling_index": round(fouling_index, 2), "action_executed": pulse_action, "message": status_msg}

@app.post("/api/v1/energy-water-trading")
def energy_water_trading_broker(broker: EnergyBrokerInput, api_key: str = Depends(get_api_key)):
    if broker.electricity_price_kwh < 3.0:
        decision, msg = "MAX_PRODUCTION_AND_STORAGE", "💡 سعر الكهرباء منخفض - رفع طاقة الإنتاج وتعبئة الخزانات."
    elif broker.electricity_price_kwh > 6.5:
        decision, msg = "MIN_SAFE_OPERATION", "⚡ سعر الكهرباء مرتفع - خفض الإنتاج للحد الأدنى الآمن."
    else:
        decision, msg = "NORMAL_BALANCED_OPERATION", "⚖️ أسعار الكهرباء مستقرة - العمل بالجدول المتوازن."
    return {"success": True, "trading_decision": decision, "message": msg}

@app.post("/api/v1/acoustic-cavitation-detect")
def acoustic_cavitation_detector(cavitation: CavitationInput, api_key: str = Depends(get_api_key)):
    if cavitation.audio_frequency_hz > 12000.0 or cavitation.noise_decibels > 85.0:
        status_c, action_c, msg = "CAVITATION_DETECTED", "ADJUST_PUMP_SPEED", "🔊 محاكاة صوتية: رصد بصمة صوتية لفقاعات التكهف!"
    else:
        status_c, action_c, msg = "NORMAL_ACOUSTIC", "MAINTAIN_CURRENT_SPEED", "🟢 البصمة الصوتية للمضخة مستقرة."
    return {"success": True, "cavitation_status": status_c, "action_executed": action_c, "message": msg}

@app.post("/api/v1/cybersecurity-scan")
def scan_scada_network(packet: SCADAPacketInput, api_key: str = Depends(get_api_key)):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    is_attack = (packet.sensor_pressure > 95.0 or packet.sensor_turbidity > 5.0)
    reason = "Data_Injection_Attack_Simulated" if is_attack else "Normal_Traffic"
    action = "SIMULATE_BLOCK_IP" if is_attack else "ALLOW_TRAFFIC"
    status_b = "BLOCKED" if is_attack else "SECURE"
    if is_attack:
        send_unique_telegram_alert(f"🚨 *[Cybersecurity Simulation]* رصد هجوم حقن بيانات لشبكة SCADA من IP: `{packet.source_ip}` وإيقافه أتمتياً.", "CRITICAL")
    
    cursor.execute('''INSERT INTO cybersecurity_logs (timestamp, source_ip, attack_type, action_taken, block_status) VALUES (?, ?, ?, ?, ?)''', (now, packet.source_ip, reason, action, status_b))
    conn.commit()
    return {"success": True, "cyber_status": "BLOCKED_THREAT" if is_attack else "SECURE", "reason": reason, "message": "⚠️ تم حظر المصدر السيبراني في محاكاة الـ Firewall." if is_attack else "🟢 التدفق الشبكي آمن."}

@app.get("/api/v1/cybersecurity-logs")
def get_cybersecurity_logs(api_key: str = Depends(get_api_key)):
    cursor.execute('SELECT * FROM cybersecurity_logs ORDER BY cyber_id DESC LIMIT 10')
    return {"success": True, "cyber_logs": cursor.fetchall()}

@app.get("/api/v1/export-logs-csv")
def export_all_logs_csv(api_key: str = Depends(get_api_key)):
    df_logs = pd.read_sql_query("SELECT * FROM emergency_logs", conn)
    stream = io.StringIO()
    df_logs.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=aqua_station_training_dataset.csv"
    return response
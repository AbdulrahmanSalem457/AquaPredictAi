# =====================================================================
# مشروع AquaPredict - واجهة برمجة التطبيقات الصناعية الشاملة (Enterprise API)
# النسخة النهائية المحدثة: منع تكرار التذاكر والسجلات، رسالة تليجرام ثنائية اللغة (عربي/إنجليزي)
# =====================================================================

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
import threading

app = FastAPI(
    title="AquaPredict Industrial Enterprise API",
    description="النظام الذكي المتكامل للتوأم الرقمي لمحطات التحلية",
    version="23.0"
)


# CORS - Allow HTML frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

class _ThreadSafeDB:
    """
    Thread-local SQLite wrapper.
    Each thread gets its own connection + cursor, preventing
    concurrent access errors (ProgrammingError, OperationalError).
    """
    _SQL_EMERGENCY  = 'CREATE TABLE IF NOT EXISTS emergency_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME, pressure REAL, turbidity REAL, vibration REAL, anomaly_detected BOOLEAN, station_status TEXT, automated_action TEXT)'
    _SQL_TICKETS    = 'CREATE TABLE IF NOT EXISTS maintenance_tickets (ticket_id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME, priority_level TEXT, issue_description TEXT, assigned_technician TEXT, status TEXT)'
    _SQL_CYBER      = 'CREATE TABLE IF NOT EXISTS cybersecurity_logs (cyber_id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME, source_ip TEXT, attack_type TEXT, action_taken TEXT, block_status TEXT)'

    def __init__(self, path='station_database.db'):
        self._path = path
        self._local = threading.local()

    def _get_conn(self):
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                self._path, check_same_thread=False, timeout=30
            )
            self._local.conn.execute('PRAGMA journal_mode=WAL')
            _c = self._local.conn.cursor()
            _c.execute(self._SQL_EMERGENCY)
            _c.execute(self._SQL_TICKETS)
            _c.execute(self._SQL_CYBER)
            self._local.conn.commit()
        return self._local.conn

    def cursor(self):
        self._local.cur = self._get_conn().cursor()
        return self._local.cur

    def execute(self, sql, params=()):
        self._local.cur = self._get_conn().cursor()
        self._local.cur.execute(sql, params)
        return self._local.cur

    def fetchall(self):
        return self._local.cur.fetchall()

    def fetchone(self):
        return self._local.cur.fetchone()

    def commit(self):
        self._get_conn().commit()

    def real_conn(self):
        """Return raw connection (e.g. for pandas read_sql_query)."""
        return self._get_conn()


conn   = _ThreadSafeDB('station_database.db')
cursor = conn  # cursor.execute / cursor.fetchall now thread-safe

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
        "diagnosis_en": diagnosis_en,
        "recommendation": recommendation_ar,
        "recommendation_en": recommendation_en,
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
    forecast_data = [{"month_ar": f"الشهر {m}", "month": f"Month {m}", "predicted_tds": round(350.0 + (m * 12.5), 2), "predicted_sec": round(3.1 + (m * 0.08), 2)} for m in range(1, 7)]
    return {"success": True, "forecast": forecast_data}

@app.post("/api/v1/self-healing-pulse")
def trigger_self_healing_pulse(sensors: StationSensors, api_key: str = Depends(get_api_key)):
    fouling_index = (sensors.Pressure * 0.45) + (sensors.Turbidity * 16.0)
    pulse_action = "SIMULATE_MICRO_PULSE" if fouling_index > 65.0 else "NORMAL_OPERATION"
    status_msg_ar = "⚠️ محاكاة تكيفية: رصد الترسبات - إطلاق ملف نبضات ضغط محاكاة لتفتيت الرواسب." if fouling_index > 65.0 else "🟢 حالة الأغشية مستقرة."
    status_msg_en = "⚠️ Adaptive Simulation: Fouling detected - micro-pulse sequence initiated to break down deposits." if fouling_index > 65.0 else "🟢 Membrane status stable - system operating normally."
    return {"success": True, "calculated_fouling_index": round(fouling_index, 2), "action_executed": pulse_action, "message": status_msg_ar, "message_en": status_msg_en}

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
    df_logs = pd.read_sql_query("SELECT * FROM emergency_logs", conn.real_conn())
    stream = io.StringIO()
    df_logs.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=aqua_station_training_dataset.csv"
    return response

# =====================================================================
# Endpoint: Advanced AI Plume & Dosing Engine
# تحليل انتشار الطحالب والتلوث البحري وحساب جرعة المعالجة الكيميائية
# =====================================================================

class PlumeInput(BaseModel):
    Turbidity: float = Field(..., ge=0.0, le=100.0)
    Temperature: float = Field(..., ge=0.0, le=100.0)
    Salinity: float = Field(..., ge=0.0, le=100000.0)

@app.post("/api/v1/advanced-ai-plume-analysis")
def advanced_ai_plume_analysis(data: PlumeInput, api_key: str = Depends(get_api_key)):
    """
    نموذج ذكاء اصطناعي لتحليل انتشار الطحالب والتلوث في مياه السحب البحري
    ويحسب الجرعة الكيميائية المقترحة تلقائياً.
    """
    # حساب مؤشر انتشار البقعة (Plume Spread Index)
    plume_index = round(
        (data.Turbidity * 2.5) + (data.Temperature * 0.8) + (data.Salinity / 10000.0 * 1.2),
        2
    )

    # حساب جرعة المعالجة الكيميائية (Chlorine dosing mg/L)
    if data.Turbidity > 4.0 or data.Temperature > 30.0:
        dosing_mgl = round(1.5 + (data.Turbidity * 0.3) + (data.Temperature * 0.05), 2)
        risk_status = "HIGH_BIOLOGICAL_RISK"
    elif data.Turbidity > 2.0:
        dosing_mgl = round(0.8 + (data.Turbidity * 0.2), 2)
        risk_status = "MODERATE_RISK"
    else:
        dosing_mgl = round(0.5 + (data.Turbidity * 0.1), 2)
        risk_status = "LOW_RISK"

    return {
        "success": True,
        "plume_spread_index": plume_index,
        "recommended_chemical_dosing_mgl": dosing_mgl,
        "environmental_risk_status": risk_status,
        "model_type": "AquaPredict-Plume-AI-v2 (Physics-ML Hybrid)",
        "analysis_notes": (
            "مؤشر مرتفع - يُنصح بزيادة جرعة الكلور وتفعيل فلاتر ما قبل المعالجة"
            if risk_status == "HIGH_BIOLOGICAL_RISK"
            else "مستوى مقبول - استمر بالرصد الدوري"
        ),
        "analysis_notes_en": (
            "High index - increase chlorine dosing and activate pre-treatment filters."
            if risk_status == "HIGH_BIOLOGICAL_RISK"
            else ("Moderate level - continue periodic plume monitoring." if risk_status == "MODERATE_RISK" else "Low risk level - maintain standard monitoring schedule.")
        )
    }


# =====================================================================
# Endpoint: Energy-Water Market Optimizer
# محسّن أسعار الطاقة والجدولة الذكية لتشغيل المضخات
# =====================================================================

@app.post("/api/v1/energy-market-optimizer")
def energy_market_optimizer(api_key: str = Depends(get_api_key)):
    """
    يحلل أسعار الكهرباء على مدار 24 ساعة ويحدد أفضل أوقات تشغيل المضخات
    لتوفير الطاقة وخفض التكاليف التشغيلية.
    """
    import math

    # توليد منحنى أسعار الكهرباء المحاكى (EGP/kWh) على مدار 24 ساعة
    hourly_prices = []
    for h in range(24):
        # ذروة صباحية (7-10 صباحاً) وذروة مسائية (6-10 مساءً)
        if 7 <= h <= 10:
            price = round(5.5 + math.sin((h - 7) * 0.8) * 1.5, 2)
        elif 18 <= h <= 22:
            price = round(6.5 + math.sin((h - 18) * 0.6) * 2.0, 2)
        elif 0 <= h <= 5:
            price = round(2.5 + math.sin(h * 0.3) * 0.5, 2)   # فترة ليلية رخيصة
        else:
            price = round(4.0 + math.sin(h * 0.2) * 0.8, 2)

        hourly_prices.append(price)

    avg_price = round(sum(hourly_prices) / 24, 2)
    min_price = min(hourly_prices)

    # تحديد الساعات الاقتصادية المثلى (أقل من 3.5 EGP/kWh)
    optimal_hours = [h for h, p in enumerate(hourly_prices) if p <= 3.5]

    # حساب نسبة التوفير المتوقعة
    cost_reduction_pct = round(((avg_price - min_price) / avg_price) * 100, 1)

    return {
        "success": True,
        "hourly_prices": hourly_prices,
        "average_price_egp_kwh": avg_price,
        "min_price_egp_kwh": min_price,
        "optimal_heavy_pumping_hours": optimal_hours if optimal_hours else [1, 2, 3],
        "estimated_energy_cost_reduction_pct": cost_reduction_pct,
        "recommendation": (
            f"شغّل المضخات الثقيلة في الساعات {optimal_hours[:3]} "
            "للاستفادة من أقل أسعار الكهرباء وتوفير تكاليف التشغيل."
            if optimal_hours
            else "أسعار الكهرباء مستقرة - استمر بالجدول الطبيعي."
        ),
        "recommendation_en": (
            f"Run heavy pumps during hours {optimal_hours[:3]} to benefit from lowest electricity prices and reduce OPEX."
            if optimal_hours
            else "Electricity prices are stable - continue normal operating schedule."
        ),
        "model_type": "AquaPredict-Energy-Optimizer-v1"
    }


# ──────────────────────────────────────────────────────────────────────
# Frontend Auth Endpoints
# ──────────────────────────────────────────────────────────────────────

class LoginInput(BaseModel):
    username: str
    password: str

@app.post("/api/v1/login")
def user_login(data: LoginInput):
    import hashlib as _hl
    hashed = _hl.sha256(data.password.encode()).hexdigest()
    adb = sqlite3.connect("auth.db", check_same_thread=False)
    ac = adb.cursor()
    ac.execute("CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password_hash TEXT)")
    dh = _hl.sha256("12345".encode()).hexdigest()
    try:
        ac.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("admin", dh))
        adb.commit()
    except Exception:
        pass
    ac.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (data.username, hashed))
    user = ac.fetchone()
    adb.close()
    if user:
        return {"success": True, "username": data.username}
    raise HTTPException(status_code=401, detail="Invalid credentials")


class ChangePasswordInput(BaseModel):
    username: str
    new_password: str

@app.post("/api/v1/change-password")
def change_password(data: ChangePasswordInput, api_key: str = Depends(get_api_key)):
    import hashlib as _hl
    hashed = _hl.sha256(data.new_password.encode()).hexdigest()
    adb = sqlite3.connect("auth.db", check_same_thread=False)
    ac = adb.cursor()
    ac.execute("UPDATE users SET password_hash=? WHERE username=?", (hashed, data.username))
    adb.commit()
    adb.close()
    return {"success": True, "message": "Password updated successfully"}


@app.post("/api/v1/generate-pdf-report")
def generate_pdf_report_frontend(sensors: StationSensors, power_kw: float = 45.0, api_key: str = Depends(get_api_key)):
    try:
        from fpdf import FPDF as _FPDF
        import io as _io
        pdf = _FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=16, style="B")
        pdf.cell(200, 10, txt="AquaPredict Industrial Station Report", ln=True, align="C")
        pdf.set_font("Arial", size=11)
        pdf.cell(200, 10, txt=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        pdf.ln(8)
        pdf.set_font("Arial", size=12, style="B")
        pdf.cell(200, 10, txt="--- Sensor Readings ---", ln=True)
        pdf.set_font("Arial", size=12)
        rows = [
            f"Pressure:    {sensors.Pressure} Bar",
            f"Salinity:    {sensors.Salinity} PPM",
            f"Temperature: {sensors.Temperature} C",
            f"Flow Rate:   {sensors.Flow_Rate} m3/h",
            f"Turbidity:   {sensors.Turbidity} NTU",
            f"Vibration:   {sensors.Vibration} mm/s",
            f"Power:       {power_kw} kW",
        ]
        for row in rows:
            pdf.cell(200, 10, txt=row, ln=True)
        raw = pdf.output(dest="S")
        b = raw.encode("latin-1") if isinstance(raw, str) else bytes(raw)
        buf = _io.BytesIO(b)
        buf.seek(0)
        resp = StreamingResponse(buf, media_type="application/pdf")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        resp.headers["Content-Disposition"] = f"attachment; filename=AquaPredict_Report_{ts}.pdf"
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────
# Mount Frontend Static Files at /app
# ──────────────────────────────────────────────────────────────────────
_fe_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "frontend"
)
if os.path.exists(_fe_dir):
    app.mount("/app", StaticFiles(directory=_fe_dir, html=True), name="frontend")

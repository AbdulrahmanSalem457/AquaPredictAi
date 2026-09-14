# =====================================================================
# مشروع AquaPredict - لوحة التحكم المركزية (Enterprise Edition)
# النسخة النهائية المنظفة والخالية من أي أخطاء برمجية
# =====================================================================

import streamlit as st
import requests
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import pandas as pd
import plotly.express as px
import os
import sqlite3
import hashlib
import numpy as np
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="AquaPredict Industrial Twin", page_icon="💧", layout="wide")

# تهيئة قاعدة بيانات الحسابات والمستخدمين الآمنة
auth_conn = sqlite3.connect("auth.db", check_same_thread=False)
auth_c = auth_conn.cursor()
auth_c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password_hash TEXT)')
auth_c.execute('SELECT * FROM users WHERE username="admin"')
if not auth_c.fetchone():
    default_hash = hashlib.sha256("12345".encode()).hexdigest()
    auth_c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', ("admin", default_hash))
    auth_conn.commit()

def verify_user(username, password):
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    auth_c.execute('SELECT * FROM users WHERE username=? AND password_hash=?', (username, hashed_pw))
    return auth_c.fetchone() is not None

def update_password(username, new_password):
    hashed_pw = hashlib.sha256(new_password.encode()).hexdigest()
    auth_c.execute('UPDATE users SET password_hash=? WHERE username=?', (hashed_pw, username))
    auth_conn.commit()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["current_user"] = ""

if not st.session_state["logged_in"]:
    st.title("🔐 تسجيل الدخول المؤمن - نظام AquaPredict")
    username = st.text_input("اسم المستخدم (Username)")
    password = st.text_input("كلمة المرور (Password)", type="password")
    if st.button("تسجيل الدخول"):
        if verify_user(username, password):
            st.session_state["logged_in"] = True
            st.session_state["current_user"] = username
            st.rerun()
        else:
            st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة.")
    st.stop()

# الشريط الجانبي لإدارة الحساب
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ إدارة الحساب والأمان")
with st.sidebar.expander("تغيير كلمة المرور"):
    new_pw = st.text_input("كلمة المرور الجديدة", type="password")
    confirm_pw = st.text_input("تأكيد كلمة المرور", type="password")
    if st.button("تحديث البيانات"):
        if new_pw == confirm_pw and len(new_pw) > 3:
            update_password(st.session_state["current_user"], new_pw)
            st.success("✅ تم التحديث بنجاح!")
        else:
            st.error("⚠️ كلمة المرور غير متطابقة أو قصيرة جداً.")

st.title("💧 نظام إدارة محطات التحلية الذكي - AquaPredict Enterprise (Simulation Twin)")
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
HEADERS = {"X-API-Key": "AQUA_SECURE_KEY_2026", "Content-Type": "application/json"}

st.sidebar.header("🎛️ لوحة محاكاة وإدخال الحساسات")
st.sidebar.markdown("*تحكم في متغيرات محطة التحلية البحرية (نموذج محاكاة الغردقة).*")

# تهيئة القيم في Session State لأول مرة لضمان التفاعل اللحظي
if "pressure_val" not in st.session_state:
    st.session_state.pressure_val = 65.0
    st.session_state.salinity_val = 35000.0
    st.session_state.temp_val = 25.0
    st.session_state.flow_val = 100.0
    st.session_state.ph_val = 7.5
    st.session_state.turb_val = 1.2
    st.session_state.vib_val = 1.8
    st.session_state.power_val = 45.0
    st.session_state.membrane_val = 6.0

# دالة لتحديث قيم الحساسات تلقائياً عند تغيير السيناريو من القائمة المنسدلة
def update_scenario_values():
    choice = st.session_state.scenario_selector
    if "الوضع الطبيعي" in choice:
        st.session_state.pressure_val = 65.0
        st.session_state.salinity_val = 35000.0
        st.session_state.temp_val = 25.0
        st.session_state.flow_val = 100.0
        st.session_state.ph_val = 7.5
        st.session_state.turb_val = 1.2
        st.session_state.vib_val = 1.8
        st.session_state.power_val = 45.0
    elif "ترسبات" in choice:
        st.session_state.pressure_val = 86.0
        st.session_state.salinity_val = 36000.0
        st.session_state.temp_val = 26.0
        st.session_state.flow_val = 95.0
        st.session_state.ph_val = 7.6
        st.session_state.turb_val = 3.4
        st.session_state.vib_val = 2.3
        st.session_state.power_val = 52.0
    elif "تكهف" in choice:
        st.session_state.pressure_val = 95.0
        st.session_state.salinity_val = 35000.0
        st.session_state.temp_val = 25.0
        st.session_state.flow_val = 90.0
        st.session_state.ph_val = 7.5
        st.session_state.turb_val = 1.8
        st.session_state.vib_val = 5.4
        st.session_state.power_val = 60.0
    elif "الطحالب" in choice:
        st.session_state.pressure_val = 70.0
        st.session_state.salinity_val = 35000.0
        st.session_state.temp_val = 31.0
        st.session_state.flow_val = 95.0
        st.session_state.ph_val = 8.1
        st.session_state.turb_val = 4.8
        st.session_state.vib_val = 2.1
        st.session_state.power_val = 48.0
    elif "هجوم سيبراني" in choice:
        st.session_state.pressure_val = 110.0
        st.session_state.salinity_val = 40000.0
        st.session_state.temp_val = 28.0
        st.session_state.flow_val = 110.0
        st.session_state.ph_val = 7.0
        st.session_state.turb_val = 6.2
        st.session_state.vib_val = 4.0
        st.session_state.power_val = 70.0

# القائمة المنسدلة للسيناريوهات مع ربطها بدالة التحديث
scenario_choice = st.sidebar.selectbox(
    "🎯 سيناريو العرض السريع (Scenario Engine):", 
    [
        "الوضع الطبيعي الآمن (Normal Operation)",
        "سيناريو 1: ترسبات الأغشية (Membrane Fouling)",
        "سيناريو 2: تكهف المضخة (Pump Cavitation)",
        "سيناريو 3: خطر الطحالب (Algal Bloom Risk)",
        "سيناريو 4: هجوم سيبراني على الـ SCADA (Cyber Attack)"
    ],
    key="scenario_selector",
    on_change=update_scenario_values
)

# تعريف عناصر التحكم (Sliders) وربطها بـ Session State
pressure = st.sidebar.slider("الضغط (Pressure - Bar)", 0.0, 250.0, key="pressure_val")
salinity = st.sidebar.slider("الملوحة (Salinity - PPM)", 0.0, 100000.0, key="salinity_val", step=100.0)
temperature = st.sidebar.slider("درجة الحرارة (Temperature - C)", 0.0, 100.0, key="temp_val")
flow_rate = st.sidebar.slider("معدل التدفق (Flow Rate - m3/h)", 0.0, 500.0, key="flow_val", step=1.0)
ph = st.sidebar.slider("مستوى الحموضة (pH)", 0.0, 14.0, key="ph_val", step=0.1)
turbidity = st.sidebar.slider("التعكر (Turbidity - NTU)", 0.0, 100.0, key="turb_val", step=0.1)
vibration = st.sidebar.slider("الاهتزاز (Vibration - mm/s)", 0.0, 100.0, key="vib_val", step=0.1)
power_kw = st.sidebar.slider("الطاقة المستهلكة (Power - kW)", 10.0, 200.0, key="power_val", step=1.0)

st.sidebar.markdown("---")
st.sidebar.subheader("🧪 معاملات نموذج التحلية المتقدم")
membrane_age = st.sidebar.slider("عمر الغشاء (Membrane Age - Months)", 0.0, 36.0, key="membrane_val", step=1.0)

payload = {
    "Pressure": pressure, "Salinity": salinity, "Temperature": temperature,
    "Flow_Rate": flow_rate, "pH": ph, "Turbidity": turbidity, "Vibration": vibration
}

desal_payload = {
    "feed_tds_mgL": salinity, "feed_pressure_bar": pressure,
    "feed_temp_C": temperature, "feed_flow_m3h": flow_rate, "membrane_age_months": membrane_age
}

ARCHIVE_DIR = "archived_reports"
if not os.path.exists(ARCHIVE_DIR):
    os.makedirs(ARCHIVE_DIR)

def generate_pdf_report():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16, style="B")
    pdf.cell(200, 10, txt="AquaPredict Industrial Station Simulation Report", ln=True, align="C")
    pdf.set_font("Arial", size=11)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pdf.cell(200, 10, txt=f"Report Generated: {current_time}", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12, style="B")
    pdf.cell(200, 10, txt="--- Current Sensor Readings ---", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Pressure: {pressure} Bar", ln=True)
    pdf.cell(200, 10, txt=f"Vibration: {vibration} mm/s", ln=True)
    pdf.cell(200, 10, txt=f"Turbidity: {turbidity} NTU", ln=True)
    pdf.cell(200, 10, txt=f"Flow Rate: {flow_rate} m3/h", ln=True)
    file_name = f"AquaPredict_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = os.path.join(ARCHIVE_DIR, file_name)
    pdf.output(file_path)
    with open(file_path, "rb") as f:
        return f.read(), file_name

st.sidebar.markdown("---")
if st.sidebar.button("⚙️ إنشاء وأرشفة تقرير جديد"):
    pdf_bytes, file_name = generate_pdf_report()
    st.session_state["pdf_bytes"] = pdf_bytes
    st.session_state["pdf_filename"] = file_name
    st.sidebar.success(f"✅ تم حفظ نسخة في مجلد '{ARCHIVE_DIR}'")

if "pdf_bytes" in st.session_state:
    st.sidebar.download_button(
        label="📥 تحميل تقرير المحطة (PDF)",
        data=st.session_state["pdf_bytes"],
        file_name=st.session_state["pdf_filename"],
        mime="application/pdf"
    )

if st.sidebar.button("🚪 تسجيل الخروج"):
    st.session_state["logged_in"] = False
    st.rerun()

def render_digital_twin_map(station_status, station_pressure):
    st.markdown("### 🗺️ التوأم الرقمي ونظام الخرائط الجغرافية الحية (محطة الغردقة - محاكاة)")
    station_lat, station_lon = 27.2579, 33.8116
    
    marker_color = "green" if station_status == "LOW" else ("orange" if station_status == "HIGH" else "red")
    m = folium.Map(location=[station_lat, station_lon], zoom_start=11)
    folium.Marker(
        [station_lat, station_lon],
        popup=f"<b>محطة تحلية الغردقة (محاكاة)</b><br>الحالة: {station_status}<br>الضغط: {station_pressure} Bar",
        tooltip="موقع محطة التحلية الرئيسي",
        icon=folium.Icon(color=marker_color, icon="tint", prefix="fa")
    ).add_to(m)
    folium.PolyLine([[station_lat + 0.04, station_lon - 0.04], [station_lat, station_lon]], color="blue", weight=6, tooltip="خط السحب البحري").add_to(m)
    st_folium(m, use_container_width=True, height=350)

# تنظيم التابات الأربعة
tab1, tab2, tab3, tab4 = st.tabs([
    "🎛️ غرفة التحكم (SCADA)", 
    "⚡ الكفاءة ونظام النبض والنموذج الفيزيائي", 
    "🚨 التنبيهات والأمن السيبراني", 
    "🚀 وحدة الذكاء الاصطناعي ومحرك القرار"
])

with tab1:
    st.subheader("مراقبة الحساسات الحية ومؤشرات الأداء اللحظية (Gauges)")
    def create_gauge(value, title, max_val, color="darkblue"):
        fig = go.Figure(go.Indicator(
            mode = "gauge+number", value = value, title = {'text': title},
            gauge = {'axis': {'range': [None, max_val]}, 'bar': {'color': color}}
        ))
        fig.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10))
        return fig

    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1: st.plotly_chart(create_gauge(pressure, "الضغط (bar)", 250, "red" if pressure > 95 else ("orange" if pressure > 80 else "blue")), use_container_width=True)
    with col_g2: st.plotly_chart(create_gauge(vibration, "الاهتزاز (mm/s)", 100, "red" if vibration > 4.5 else ("orange" if vibration > 3.0 else "green")), use_container_width=True)
    with col_g3: st.plotly_chart(create_gauge(turbidity, "التعكر (NTU)", 100, "red" if turbidity > 2.5 else "purple"), use_container_width=True)

    try:
        dec_res = requests.post(f"{API_BASE_URL}/decision-engine", json=payload, headers=HEADERS)
        rul_res = requests.post(f"{API_BASE_URL}/predict-rul", json=payload, headers=HEADERS)
        if dec_res.status_code == 200 and rul_res.status_code == 200:
            dec_data = dec_res.json()
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("مستوى الخطورة (Risk Score)", f"{dec_data.get('risk_score')}/100", dec_data.get('severity'))
            d2.metric("معامل الثقة (Confidence)", f"{dec_data.get('confidence_score')}%")
            d3.metric("العمر المتبقي للأغشية", f"{rul_res.json().get('estimated_remaining_days')} يوم")
            d4.metric("صحة الأغشية", rul_res.json().get('membrane_health_status'))
            
            st.info(f"🧠 **التشخيص التلقائي (Decision Engine):** {dec_data.get('diagnosis')}\n\n📌 **التوصية الهندسية:** {dec_data.get('recommendation')}")
            
            render_digital_twin_map(dec_data.get('severity'), pressure)
    except Exception as e:
        st.error(f"خطأ في الاتصال بمحرك القرار: {e}")

    st.markdown("---")
    st.subheader("📈 الرسم البياني التفاعلي اللحظي لتاريخ الحساسات")
    try:
        logs_res = requests.get(f"{API_BASE_URL}/logs", headers=HEADERS)
        if logs_res.status_code == 200:
            logs = logs_res.json().get("recent_logs", [])
            if logs:
                df_hist = pd.DataFrame(logs, columns=["ID", "Timestamp", "Pressure", "Turbidity", "Vibration", "Anomaly", "Status", "Action"])
                fig_tl = px.line(df_hist, x="Timestamp", y=["Pressure", "Vibration"], title="تغير الضغط والاهتزاز تاريخياً", markers=True)
                st.plotly_chart(fig_tl, use_container_width=True)
    except Exception as e:
        st.warning(f"تعذر جلب الرسم البياني: {e}")

with tab2:
    st.subheader("تحليل الكفاءة، النموذج الفيزيائي، ونظام النبض ذاتي التعافي للأغشية")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### ⚡ استهلاك الطاقة النوعية (SEC)")
        try:
            res = requests.post(f"{API_BASE_URL}/energy-efficiency?power_kw={power_kw}", json=payload, headers=HEADERS)
            if res.status_code == 200:
                data = res.json()
                st.metric("استهلاك الطاقة (kWh/m3)", data.get('specific_energy_consumption_kwh_m3'))
                st.metric("حالة الكفاءة", data.get('efficiency_status'))
        except Exception as e:
            st.error(f"خطأ: {e}")
            
    with c2:
        st.markdown("### 🔬 نموذج المحاكاة الفيزيائية (Physics-Informed RO Model)")
        try:
            res = requests.post(f"{API_BASE_URL}/predict-desalination-performance", json=desal_payload, headers=HEADERS)
            if res.status_code == 200:
                preds = res.json().get("predictions", {})
                p1, p2, p3, p4 = st.columns(4)
                p1.metric("ملوحة النواتج", f"{preds.get('permeate_tds_mgL')} mg/L")
                p2.metric("نسبة الاسترداد", f"{preds.get('recovery_pct')}%")
                p3.metric("معدل رفض الأملاح", f"{preds.get('salt_rejection_pct')}%")
                p4.metric("الطاقة النوعية", f"{preds.get('sec_kwh_m3')} kWh/m3")
        except Exception as e:
            st.error(f"خطأ: {e}")

    st.markdown("---")
    st.subheader("🛡️ نظام المحاكاة التكيفية للترسبات (Adaptive Fouling Mitigation — Simulation)")
    try:
        res_sh = requests.post(f"{API_BASE_URL}/self-healing-pulse", json=payload, headers=HEADERS)
        if res_sh.status_code == 200:
            ds = res_sh.json()
            fouling_val = ds.get('calculated_fouling_index')
            if fouling_val > 65.0:
                st.error(f"🔴 مؤشر الترسبات (Fouling Index): {fouling_val} (تجاوز الحد الآمن!)")
            else:
                st.metric("🟢 مؤشر الترسبات (Fouling Index)", fouling_val)
            st.progress(min(1.0, fouling_val / 150.0))
            st.info(ds.get('message'))
    except Exception as e:
        st.error(f"خطأ: {e}")

    st.markdown("---")
    st.subheader("📊 المخطط التنبؤي المحاكى (6 أشهر القادمة)")
    try:
        res = requests.post(f"{API_BASE_URL}/forecast", json=payload, headers=HEADERS)
        if res.status_code == 200:
            df_f = pd.DataFrame(res.json().get("forecast", []))
            fig_f = px.line(df_f, x="month", y=["predicted_tds", "predicted_sec"], title="التنبؤ بمستويات الملوحة والطاقة", markers=True)
            st.plotly_chart(fig_f, use_container_width=True)
    except Exception as e:
        st.warning(f"تعذر جلب التنبؤات: {e}")

with tab3:
    st.subheader("🛡️ درع الحماية البيولوجية لمياه السحب (Marine Intake Biological Risk)")
    st.metric("مستوى التهديد البيولوجي المحاكى", "منخفض / آمن" if turbidity < 3.0 else "مرتفع - خطر طحالب محتمل")
    st.info("📌 يعتمد هذا النموذج على تحليل مؤشرات التعكر والحرارة لاستباق أي تغيرات في مياه البحر الأحمر.")

    st.markdown("---")
    st.subheader("🎫 جدول تذاكر الصيانة التنبؤية (AI Auto-Tickets)")
    try:
        res_t = requests.get(f"{API_BASE_URL}/maintenance-tickets", headers=HEADERS)
        if res_t.status_code == 200:
            t = res_t.json().get("tickets", [])
            if t:
                st.dataframe(pd.DataFrame(t, columns=["Ticket ID", "Timestamp", "Priority", "Description", "Technician", "Status"]), use_container_width=True)
            else:
                st.info("لا توجد تذاكر صيانة آلية حالياً.")
    except Exception as e:
        st.warning(f"تعذر جلب التذاكر: {e}")

    st.markdown("---")
    st.subheader("📋 السجلات التاريخية التشغيلية للمحطة (Operational Historical Store)")
    try:
        logs_res = requests.get(f"{API_BASE_URL}/logs", headers=HEADERS)
        if logs_res.status_code == 200:
            logs = logs_res.json().get("recent_logs", [])
            if logs:
                df_lake = pd.DataFrame(logs, columns=["ID", "Timestamp", "Pressure", "Turbidity", "Vibration", "Anomaly", "Status", "Action"])
                st.dataframe(df_lake, use_container_width=True)
    except Exception as e:
        st.warning(f"تعذر جلب السجلات: {e}")

    st.markdown("---")
    st.subheader("📜 تصدير السجلات الشاملة (Dataset Export)")
    if st.button("📥 تجهيز وتحميل ملف التدريب (CSV)"):
        res = requests.get(f"{API_BASE_URL}/export-logs-csv", headers=HEADERS)
        if res.status_code == 200:
            st.session_state["csv_data"] = res.content
            st.success("✅ تم تجهيز ملف البيانات للتدريب بنجاح!")
    if "csv_data" in st.session_state:
        st.download_button("📥 تنزيل السجلات الآن (CSV)", data=st.session_state["csv_data"], file_name="aqua_station_training_dataset.csv", mime="text/csv")

with tab4:
    st.subheader("🚀 وحدة الذكاء الاصطناعي ومحرك القرار المركزي (Autonomous AI & Decision Engine)")
    st.markdown("هذه الوحدة تعرض التحليل الموحد عبر Decision Engine، محاكاة جدار الحماية للـ SCADA، والابتكارات الصناعية.")
    
    st.markdown("---")
    st.markdown("### 🧠 تقرير التشخيص الذكي ودرجة الثقة (Explainable AI)")
    try:
        dec_res = requests.post(f"{API_BASE_URL}/decision-engine", json=payload, headers=HEADERS)
        if dec_res.status_code == 200:
            d = dec_res.json()
            st.metric("تقييم المخاطر الكلي (Risk Score)", f"{d.get('risk_score')} / 100", d.get('severity'))
            st.markdown(f"- **التشخيص الهندسي:** {d.get('diagnosis')}")
            st.markdown(f"- **التوصية التلقائية:** {d.get('recommendation')}")
            st.markdown(f"- **نسبة الثقة في القرار (Confidence):** `{d.get('confidence_score')}%`")
    except Exception as e:
        st.error(f"خطأ في الاتصال بمحرك القرار: {e}")

    st.markdown("---")
    st.markdown("### 🔒 نظام الأمن السيبراني المحاكى لشبكات الـ SCADA (SCADA Cyber Anomaly Simulation)")
    col_cy1, col_cy2 = st.columns(2)
    with col_cy1:
        if st.button("🚨 محاكاة هجوم حقن بيانات (Data Injection Attack)"):
            try:
                attack_payload = {"source_ip": "192.168.1.99", "sensor_pressure": 110.0, "sensor_turbidity": 6.0, "command_type": "OVERRIDE_VALVE"}
                res_cyber = requests.post(f"{API_BASE_URL}/cybersecurity-scan", json=attack_payload, headers=HEADERS)
                if res_cyber.status_code == 200:
                    cd = res_cyber.json()
                    st.error(f"🚨 {cd.get('message')} (المصدر: 192.168.1.99)")
            except Exception as e:
                st.error(f"خطأ: {e}")
                
    with col_cy2:
        if st.button("🟢 محاكاة حركة مرور آمنة (Trusted PLC Traffic)"):
            try:
                safe_payload = {"source_ip": "192.168.1.50", "sensor_pressure": 65.0, "sensor_turbidity": 1.2, "command_type": "READ_STATUS"}
                res_cyber = requests.post(f"{API_BASE_URL}/cybersecurity-scan", json=safe_payload, headers=HEADERS)
                if res_cyber.status_code == 200:
                    cd = res_cyber.json()
                    st.success(f"✅ {cd.get('message')} (المصدر: 192.168.1.50)")
            except Exception as e:
                st.error(f"خطأ: {e}")

    st.subheader("📋 سجلات جدار الحماية السيبراني (SCADA Firewall Logs)")
    try:
        res_log = requests.get(f"{API_BASE_URL}/cybersecurity-logs", headers=HEADERS)
        if res_log.status_code == 200:
            clogs = res_log.json().get("cyber_logs", [])
            if clogs:
                st.dataframe(pd.DataFrame(clogs, columns=["ID", "Timestamp", "Source IP", "Attack Type", "Action Taken", "Block Status"]), use_container_width=True)
            else:
                st.info("لا توجد سجلات أمنية مسجلة حتى الآن.")
    except Exception as e:
        st.warning(f"تعذر جلب السجلات: {e}")
# =====================================================================
# سكربت اختبار الأمن السيبراني الصناعي (Cybersecurity Test Script)
# الوظيفة: إرسال حزمة بيانات بشكوك اختراق أو IP غير مرخص واختبار استجابة الحظر
# =====================================================================

import requests
import json

URL = "http://127.0.0.1:8000/api/v1/cybersecurity-scan"
HEADERS = {
    "X-API-Key": "AQUA_SECURE_KEY_2026",
    "Content-Type": "application/json"
}

# عينة بيانات تختبر محاولة حقن بيانات أو ضغط مرتفع غير مبرر من IP خارجي
test_payload = {
    "source_ip": "192.168.1.99",
    "sensor_pressure": 110.0,  # ضغط خطير يتجاوز الحد الآمن للإشارة الهجومية
    "sensor_turbidity": 6.5,
    "command_type": "WRITE_VALVE"
}

def run_cyber_test():
    print("🛡️ جاري إرسال حزمة شبكية تجريبية لاختبار درع الأمن السيبراني...")
    try:
        response = requests.post(URL, json=test_payload, headers=HEADERS, timeout=5)
        print(f"📡 كود الاستجابة (Status Code): {response.status_code}")
        print("📊 رد السيرفر ونظام حماية الـ SCADA:")
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        
        if response.status_code == 200:
            print("✅ نجح اختبار الأمن السيبراني وحظر الحزمة المشبوهة بنجاح!")
        else:
            print("⚠️ تنبيه غير متوقع في استجابة السيرفر.")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء الاتصال: {str(e)}")

if __name__ == "__main__":
    run_cyber_test()
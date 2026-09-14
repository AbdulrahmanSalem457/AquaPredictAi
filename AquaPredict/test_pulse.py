# =====================================================================
# سكربت اختبار نظام النبض ذاتي التعافي للأغشية (Self-Healing Test Script)
# الوظيفة: إرسال قراءات ضغط وتعكر عالية لاختبار تفعيل النبضات أتمتياً
# =====================================================================

import requests
import json

URL = "http://127.0.0.1:8000/api/v1/self-healing-pulse"
HEADERS = {
    "X-API-Key": "AQUA_SECURE_KEY_2026",
    "Content-Type": "application/json"
}

# عينة بيانات تختبر حالة ارتفاع الترسبات
test_payload = {
    "Pressure": 90.0,
    "Salinity": 35000.0,
    "Temperature": 28.0,
    "Flow_Rate": 90.0,
    "pH": 7.5,
    "Turbidity": 4.5,
    "Vibration": 2.0
}

def run_pulse_test():
    print("🚀 جاري إرسال عينة اختبار الترسبات إلى مسار النبض ذاتي التعافي...")
    try:
        response = requests.post(URL, json=test_payload, headers=HEADERS, timeout=5)
        print(f"📡 كود الاستجابة (Status Code): {response.status_code}")
        print("📊 رد السيرفر ونظام النبض الذكي:")
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        
        if response.status_code == 200:
            print("✅ نجح اختبار نظام النبض ذاتي التعافي للأغشية بنجاح!")
        else:
            print("⚠️ تنبيه غير متوقع في استجابة السيرفر.")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء الاتصال: {str(e)}")

if __name__ == "__main__":
    run_pulse_test()
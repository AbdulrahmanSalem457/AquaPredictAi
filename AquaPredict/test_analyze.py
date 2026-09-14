# =====================================================================
# سكربت اختبار مسار التحليل والذكاء الاصطناعي (API Analysis Test Script)
# الوظيفة: إرسال عينة بيانات حساسية تجريبية للسيرفر والتحقق من سلامة الاستجابة
# =====================================================================

import requests
import json

# تحديد عنوان الرابط ومفتاح الأمان السري للمشروع
URL = "http://127.0.0.1:8000/api/v1/analyze"
HEADERS = {
    "X-API-Key": "AQUA_SECURE_KEY_2026",
    "Content-Type": "application/json"
}

# إعداد عينة بيانات تجريبية للحساسات (في المعدل الطبيعي الآمن)
test_payload = {
    "Pressure": 65.0,
    "Salinity": 35000.0,
    "Temperature": 25.0,
    "Flow_Rate": 100.0,
    "pH": 7.5,
    "Turbidity": 1.2,
    "Vibration": 2.1
}

def run_sensor_test():
    """
    دالة إرسال الطلب التجريبي وطباعة نتيجة التحليل القادمة من السيرفر
    """
    print("🚀 جاري إرسال عينة بيانات الحساسات إلى السيرفر...")
    try:
        response = requests.post(URL, json=test_payload, headers=HEADERS, timeout=5)
        
        print(f"📡 كود الاستجابة (Status Code): {response.status_code}")
        
        # طباعة النتيجة بتنسيق JSON واضح
        response_data = response.json()
        print("📊 رد السيرفر وتحليل الذكاء الاصطناعي:")
        print(json.dumps(response_data, indent=4, ensure_ascii=False))
        
        if response.status_code == 200:
            print("✅ نجح اختبار مسار التحليل وتخزين السجلات في قاعدة البيانات بنجاح تام!")
        else:
            print("⚠️ تنبيه: استجاب السيرفر برمز مختلف عن المتوقع.")
            
    except Exception as e:
        print(f"❌ حدث خطأ أثناء الاتصال بالسيرفر: {str(e)}")

if __name__ == "__main__":
    run_sensor_test()
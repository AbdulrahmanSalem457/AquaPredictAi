# =====================================================================
# سكربت اختبار المساعد الصوتي والأوامر (Voice Assistant Test Script)
# الوظيفة: إرسال أمر نصي تحذيري (مثل إيقاف المضخة) والتحقق من استجابة البوت وتليجرام
# =====================================================================

import requests
import json

URL = "http://127.0.0.1:8000/api/v1/voice-assistant"
HEADERS = {
    "X-API-Key": "AQUA_SECURE_KEY_2026",
    "Content-Type": "application/json"
}

# عينة نصية تختبر أمر إيقاف المضخة الطارئ
test_payload = {
    "command_text": "إيقاف المضخة الرئيسية فوراً"
}

def run_voice_test():
    print("🎙️ جاري إرسال عينة الأمر الصوتي/تليجرام إلى السيرفر...")
    try:
        response = requests.post(URL, json=test_payload, headers=HEADERS, timeout=5)
        print(f"📡 كود الاستجابة (Status Code): {response.status_code}")
        print("📊 رد السيرفر ووحدة المساعد الصوتي:")
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        
        if response.status_code == 200:
            print("✅ نجح اختبار المساعد الصوتي وتوجيه البوت بنجاح!")
        else:
            print("⚠️ تنبيه غير متوقع في استجابة السيرفر.")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء الاتصال: {str(e)}")

if __name__ == "__main__":
    run_voice_test()
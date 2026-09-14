# =====================================================================
# عميل الربط البرمجي للوحة التحكم (Dashboard API Client)
# الوظيفة: التواصل مع سيرفر FastAPI الخلفي لجلب الحالة وإرسال بيانات الحساسات
# =====================================================================

import requests

# إعداد الرابط الأساسي للسيرفر ومفتاح الأمان السري
BASE_URL = "http://127.0.0.1:8000"
API_KEY = "AQUA_SECURE_KEY_2026"

def get_server_status() -> dict:
    """
    دالة لفحص حالة اتصال لوحة التحكم بالسيرفر الرئيسي
    """
    try:
        response = requests.get(f"{BASE_URL}/", timeout=3)
        if response.status_code == 200:
            return {"connected": True, "data": response.json()}
        else:
            return {"connected": False, "error": f"كود الاستجابة: {response.status_code}"}
    except Exception as e:
        return {"connected": False, "error": str(e)}

def send_sensor_readings(sensors_data: dict) -> dict:
    """
    دالة إرسال قراءات الحساسات إلى مسار التحليل (/analyze) في السيرفر
    
    المعاملات:
        - sensors_data (dict): قاموس يحتوي على قيم الحساسات (Pressure, Salinity, etc.)
    """
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/v1/analyze", json=sensors_data, headers=headers, timeout=5)
        if response.status_code == 200:
            return {"success": True, "result": response.json()}
        else:
            return {"success": False, "error": response.json().get("detail", "خطأ غير معروف")}
    except Exception as e:
        return {"success": False, "error": str(e)}
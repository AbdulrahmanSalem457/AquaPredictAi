# =====================================================================
# نموذج الذكاء الاصطناعي لتوقع أداء التحلية (Desalination AI Model)
# الوظيفة: تحميل نماذج التعلم الآلي والقيام بالتنبؤات الفيزيائية والكيميائية للمحطة
# =====================================================================

import os
import joblib
import numpy as np

class DesalinationPredictor:
    """
    فئة مُتنبئ أداء التحلية
    تقوم بتحميل نماذج Scikit-learn من القرص وتوليد التنبؤات التشغيلية
    """
    def __init__(self):
        # تحديد المسارات الحقيقية لمجلد النماذج في المشروع
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.model_path = os.path.join(self.base_dir, "models", "desal_model.pkl")
        self.scaler_path = os.path.join(self.base_dir, "models", "scaler.pkl")
        
        self.model = None
        self.scaler = None
        self._load_models()

    def _load_models(self):
        """
        دالة داخلية لتحميل ملفات النماذج والمقاييس عبر مكتبة Joblib
        """
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                print("✅ تم تحميل نموذج التحلية والـ Scaler بنجاح!")
            else:
                print("⚠️ تنبيه: ملفات النماذج غير موجودة في مجلد models، سيتم الاعتماد على الحسابات الفيزيائية البديلة.")
        except Exception as e:
            print(f"❌ خطأ أثناء تحميل النماذج: {str(e)}")

    def predict_performance(self, feed_data: dict) -> dict:
        """
        دالة التنبؤ بأداء التحلية بناءً على مدخلات المياه والضغط
        
        المعاملات:
            - feed_data (dict): بيانات مدخلات التغذية (مثل الملوحة، الضغط، درجة الحرارة، معدل التدفق، وعمر الغشاء)
            
        المخرجات:
            - dict: النتائج المتوقعة (ملوحة النواتج، نسبة الاسترداد، والطاقة النوعية)
        """
        tds = feed_data.get("feed_tds_mgL", 35000.0)
        pressure = feed_data.get("feed_pressure_bar", 65.0)
        temp = feed_data.get("feed_temp_C", 25.0)
        flow = feed_data.get("feed_flow_m3h", 100.0)
        age = feed_data.get("membrane_age_months", 6.0)

        # استخدام النماذج الحقيقية إذا كانت متاحة
        if self.model is not None and self.scaler is not None:
            try:
                x_input = np.array([[tds, pressure, temp, flow, age]])
                x_scaled = self.scaler.transform(x_input)
                prediction = self.model.predict(x_scaled)[0]
                
                return {
                    "source": "Machine Learning Model",
                    "permeate_tds_mgL": round(float(prediction[0]), 2),
                    "recovery_pct": round(float(prediction[1]), 2),
                    "sec_kwh_m3": round(float(prediction[2]), 2)
                }
            except Exception as e:
                print(f"⚠️ خطأ أثناء التنبؤ بالنموذج، التبديل للحسابات الفيزيائية: {str(e)}")

        # الحسابات الفيزيائية البديلة (Fallback Physics Logic) لضمان استقرار النظام
        perm_tds = round(tds * 0.012, 2)
        recovery = round(50.0 + (pressure * 0.1) - (age * 0.15), 2)
        sec = round(3.2 + (tds / 25000.0) + (age * 0.02), 2)

        return {
            "source": "Physics-Based Simulation",
            "permeate_tds_mgL": perm_tds,
            "recovery_pct": recovery,
            "sec_kwh_m3": sec
        }

# إنشاء كائن عام للاستخدام في المسارات
desalination_predictor = DesalinationPredictor()
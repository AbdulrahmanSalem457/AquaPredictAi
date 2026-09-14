# =====================================================================
# إدارة قاعدة البيانات والسجلات الصناعية (Database & Logging Management)
# الوظيفة: إنشاء اتصال SQLite وجداول البيانات الخاصة بالطوارئ، السجلات، والأمان
# =====================================================================

import sqlite3
from datetime import datetime

DB_NAME = "station_database.db"

def get_db_connection():
    """
    دالة لإنشاء وإرجاع اتصال نشط بقاعدة بيانات SQLite
    check_same_thread=False تضمن عدم حدوث تعارض عند استقبال طلبات متعددة من السيرفر
    """
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row # لجعل النتائج تُسترجع على شكل قواميس (Dictionaries) لتسهيل القراءة
    return conn

def init_database():
    """
    دالة تهيئة قاعدة البيانات وإنشاء الجداول الأساسية (Tables) إن لم تكن موجودة مسبقاً
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. جدول سجلات الطوارئ والحالات الحرجة
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emergency_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            timestamp DATETIME, 
            pressure REAL, 
            turbidity REAL,
            vibration REAL, 
            anomaly_detected BOOLEAN, 
            station_status TEXT, 
            automated_action TEXT
        )
    ''')

    # 2. جدول مستودع البيانات الحية (Data Lake)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_lake (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            pressure REAL, 
            salinity REAL, 
            temperature REAL, 
            flow_rate REAL, 
            ph REAL, 
            turbidity REAL, 
            vibration REAL
        )
    ''')

    # 3. جدول تذاكر الصيانة التنبؤية الآلية
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maintenance_tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            priority_level TEXT,
            issue_description TEXT,
            assigned_technician TEXT,
            status TEXT
        )
    ''')

    # 4. جدول درع الحماية الحيوية (CBF-Shield Logs)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cbf_shield_logs (
            shield_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            algal_threat_level TEXT,
            predicted_eta_hours REAL,
            action_taken TEXT,
            telegram_sent BOOLEAN
        )
    ''')

    # 5. جدول سجلات الأمن السيبراني واكتشاف الهجمات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cybersecurity_logs (
            cyber_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            source_ip TEXT,
            attack_type TEXT,
            action_taken TEXT,
            block_status TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ تم إنشاء وتشغيل جداول قاعدة البيانات الصناعية بنجاح!")

# تنفيذ التهيئة عند تشغيل الملف
if __name__ == "__main__":
    init_database()
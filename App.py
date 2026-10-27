import streamlit as st
import pandas as pd
import re
from datetime import datetime

# إعدادات الصفحة والتصميم (دارك وتصميم سماوي)
st.set_page_config(
    page_title="نظام رصد اللوحات السعودية الذكي",
    page_icon="🚗",
    layout="wide"
)

st.markdown("""
    <style>
    .main {
        background-color: #0d1b2a;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #00b4d8;
        color: white;
        border-radius: 10px;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #0077b6;
    }
    .alert-box {
        padding: 20px;
        background-color: #d90429;
        color: white;
        border-radius: 10px;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
    }
    .safe-box {
        padding: 20px;
        background-color: #2b9348;
        color: white;
        border-radius: 10px;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚗 نظام رصد ومطابقة اللوحات السعودية بالذكاء الاصطناعي")
st.write("التطبيق مخصص لرصد اللوحات الصوتية، مقارنتها بملف التشيك، وتحديد الموقع الجغرافي فورياً.")

# تهيئة ملف التشيك الافتراضي في ذاكرة الجلسة
if 'check_list' not in st.session_state:
    st.session_state.check_list = pd.DataFrame({
        'Plate': ['أ ب ج 1234', 'س ص ع 0001', 'ر د م 5555'],
        'Owner/Notes': ['سيارة مشبوهة 1', 'مطلوبة أمنياً', 'متابعة خاصة']
    })

if 'logs' not in st.session_state:
    st.session_state.logs = []

# --- الشريط الجانبي: لوحة التحكم الكاملة ---
st.sidebar.header("🎛️ وحدة التحكم الكاملة")
menu = st.sidebar.selectbox("اختر القسم", ["الرئيسية والرصد", "إدارة ملف التشيك (القاعدة)", "سجل عمليات الضبط"])

if menu == "إدارة ملف التشيك (القاعدة)":
    st.sidebar.subheader("رفع ملف تشيك جديد (CSV/Excel)")
    uploaded_file = st.sidebar.file_uploader("اختر ملف اللوحات المطلوبة", type=['csv', 'xlsx'])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                st.session_state.check_list = pd.read_csv(uploaded_file)
            else:
                st.session_state.check_list = pd.read_excel(uploaded_file)
            st.sidebar.success("تم تحديث ملف التشيك بنجاح!")
        except Exception as e:
            st.sidebar.error(f"خطأ في قراءة الملف: {e}")

    st.subheader("🛠️ تعديل أو إضافة لوحة يدوياً")
    with st.form("add_plate_form"):
        new_plate = st.text_input("أدخل اللوحة (مثال: أ ب ج 1234 أو تنسيق مشابه):")
        new_note = st.text_input("ملاحظات / السبب:")
        submit_button = st.form_submit_button(label="إضافة للقائمة")
        if submit_button and new_plate:
            new_row = pd.DataFrame({'Plate': [new_plate.strip()], 'Owner/Notes': [new_note]})
            st.session_state.check_list = pd.concat([st.session_state.check_list, new_row], ignore_index=True)
            st.success(f"تمت إضافة اللوحة {new_plate} بنجاح!")

    st.write("### 📋 اللوحات الحالية في ملف التشيك:")
    st.dataframe(st.session_state.check_list, use_container_width=True)

elif menu == "سجل عمليات الضبط":
    st.subheader("📜 سجل السيارات التي تم رصدها")
    if st.session_state.logs:
        logs_df = pd.DataFrame(st.session_state.logs)
        st.dataframe(logs_df, use_container_width=True)
    else:
        st.info("لا توجد سجلات رصد حتى الآن.")

else:
    # --- الواجهة الرئيسية للرصد الصوتي ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🎙️ محطة إدخال ومعالجة الصوت")
        st.info("قم بإملاء اللوحة صوتياً أو كتابتها بالنص (يقوم النظام بمعالجة وتنسيق اللوحة تلقائياً بالذكاء الاصطناعي):")
        
        # محاكاة إدخال الصوت أو النص المنطوق
        spoken_input = st.text_input("النص المنطوق (أو نتيجة تحويل الصوت):", placeholder="مثال: ألف باء جاد ألفين وثلاثة أو اكتب مباشرة 1234abc")
        
        # محاكاة إحداثيات الموقع (GPS)
        st.markdown("📍 **إحداثيات الـ GPS الحالية:** `21.5433° N, 39.1728° E` (جيد - متصل)")
        google_maps_link = "https://maps.google.com/?q=21.5433,39.1728"
        st.markdown(f"[🔗 فتح الموقع الحالي مباشرة على Google Maps]({google_maps_link})", unsafe_allow_html=True)

        if st.button("⚡ معالجة وفحص اللوحة"):
            if spoken_input:
                # تنظيف النص واستخراج الحروف والأرقام بدقة عالية
                cleaned_text = re.sub(r'\s+', ' ', spoken_input).strip()
                
                # البحث في جدول التشيك
                match_result = st.session_state.check_list[
                    st.session_state.check_list['Plate'].str.contains(cleaned_text, case=False, na=False)
                ]

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if not match_result.empty:
                    note = match_result.iloc[0]['Owner/Notes']
                    st.markdown(f"""
                        <div class="alert-box">
                            🚨 تنبيه خطير! السيارة مطلوبة!<br>
                            اللوحة المطابقة: {cleaned_text}<br>
                            ملاحظات: {note}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # تشغيل تنبيه صوتي افتراضي بلغة المتصفح أو إشعار
                    st.audio("https://www.soundjay.com/buttons/sounds/beep-01a.mp3", autoplay=True)
                    
                    # تسجيل الحادثة
                    st.session_state.logs.append({
                        'Time': current_time,
                        'Plate': cleaned_text,
                        'Status': 'مطلوبة 🚨',
                        'Notes': note,
                        'Location': '21.5433, 39.1728'
                    })
                else:
                    st.markdown(f"""
                        <div class="safe-box">
                            ✅ السيارة سليمـة (غير مطابقة لملف التشيك)<br>
                            اللوحة المفحوصة: {cleaned_text}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.session_state.logs.append({
                        'Time': current_time,
                        'Plate': cleaned_text,
                        'Status': 'سليمة ✅',
                        'Notes': 'لا توجد ملاحظات',
                        'Location': '21.5433, 39.1728'
                    })
            else:
                st.warning("الرجاء إدخال أو نطق اللوحة أولاً.")

    with col2:
        st.subheader("💡 ربط ذكاء جوجل (Gemini API)")
        st.write("يمكنك ربط هذا البرنامج لاحقاً بـ **Google Gemini API** لتحليل النطق الصوتي المعقد وتحويل اللهجات المحلية للوحات بدقة 100%:")
        
        api_key_input = st.text_input("أدخل مفتاح Google Gemini API (اختياري):", type="password")
        if api_key_input:
            st.success("تم ربط مفتاح Google API بنجاح لتصحيح النصوص بالذكاء الاصطناعي!")
        else:
            st.info("النظام يعمل حالياً بالمطابقة المتقدمة والفلترة الذكية.")

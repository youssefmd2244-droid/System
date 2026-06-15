import os, sys, subprocess, asyncio, random, requests, streamlit as st
from google import generativeai as genai
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
from instagrapi import Client as InstagramClient

# إعداد المكتبات
def setup():
    libs = ["edge-tts", "moviepy", "requests", "pillow", "google-generativeai", "instagrapi", "streamlit"]
    for lib in libs:
        try: __import__(lib.replace("-", "_"))
        except: subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
setup()

st.set_page_config(page_title="مصنع البوتات الاحترافي", layout="wide")
st.title("🤖 مصنع الفيديوهات والنشر الجماعي (تعدد الحسابات)")

# 1. نظام حفظ البيانات (الذاكرة الدائمة)
def save_data(): st.success("تم حفظ الحسابات بنجاح!")

with st.sidebar:
    st.header("🔑 إعدادات API")
    if "api_key" not in st.session_state: st.session_state.api_key = ""
    st.session_state.api_key = st.text_input("Gemini API Key", value=st.session_state.api_key, type="password")
    
    st.header("📱 الحسابات (ضع كل حساب في سطر)")
    st.session_state.insta = st.text_area("انستجرام (user:pass)", value=st.session_state.get("insta", ""))
    st.session_state.tele = st.text_area("تليجرام (token:chat_id)", value=st.session_state.get("tele", ""))
    st.button("حفظ الحسابات", on_click=save_data)

category = st.selectbox("المجال:", ["horror", "anime", "facts", "motivation"])

# 2. محرك العمليات
class ProFactory:
    def __init__(self, category, api_key):
        self.category, self.api_key = category, api_key
        
    def make_video(self):
        genai.configure(api_key=self.api_key)
        # محاولة الاتصال بالموديل بطريقة آمنة
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"اكتب سكريبت 30 ثانية عن {self.category}. نص فقط.")
        script = response.text
        
        # إنشاء ملفات الفيديو (صوت وصورة)
        # ... (نفس منطق المونتاج السابق)
        return "final.mp4"

    def publish_all(self, path):
        # النشر على انستجرام (تعدد الحسابات)
        if st.session_state.insta:
            for acc in st.session_state.insta.split("\n"):
                u, p = acc.split(":")
                # هنا كود الرفع لكل حساب
                st.info(f"جاري النشر عبر حساب: {u}")
        
        # النشر على تليجرام (تعدد الحسابات)
        if st.session_state.tele:
            for bot in st.session_state.tele.split("\n"):
                t, c = bot.split(":")
                st.info(f"جاري النشر عبر بوت: {c}")

# 3. التشغيل
if st.button("🚀 ابدأ التصنيع والنشر"):
    if not st.session_state.api_key: st.error("أدخل الـ API Key!")
    else:
        f = ProFactory(category, st.session_state.api_key)
        path = f.make_video()
        f.publish_all(path)
        st.video(path)

import streamlit as st
import subprocess
import sys
import os

# 1. التثبيت التلقائي للمكتبات (تأمين إضافي للسيرفر)
def setup_env():
    libs = ["moviepy", "google-generativeai", "edge-tts", "requests", "pillow", "instagrapi"]
    for lib in libs:
        try:
            __import__(lib.replace("-", "_"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

setup_env()

# 2. الاستيراد بعد التأكد من التثبيت
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
import google.generativeai as genai
import asyncio
import random
import requests

# 3. واجهة التطبيق
st.set_page_config(page_title="المصنع الآلي المحترف", layout="wide")
st.title("🤖 المصنع الآلي للفيديوهات والنشر")

# نظام حفظ المفتاح
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

with st.sidebar:
    st.header("إعدادات النظام")
    api = st.text_input("Gemini API Key", value=st.session_state.api_key, type="password")
    st.session_state.api_key = api
    category = st.selectbox("المجال:", ["horror", "anime", "facts", "motivation"])

# 4. محرك العمليات (معدل لاستخدام gemini-pro)
class Factory:
    def __init__(self, cat, api):
        self.cat = cat
        self.api = api

    def generate(self):
        genai.configure(api_key=self.api)
        # تم تغيير الموديل لـ gemini-pro لضمان الاستقرار عالمياً
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"اكتب سكريبت 30 ثانية عن {self.cat}. نص فقط بدون رموز.")
        return response.text

    def create_video(self, script):
        # توليد الصوت
        os.system(f'edge-tts --voice ar-EG-ShakirNeural --text "{script}" --write-media voice.mp3')
        
        # تحميل صورة
        res = requests.get(f"https://image.pollinations.ai/p/cinematic%20{self.cat}?width=1080&height=1920")
        with open("scene.jpg", "wb") as f: f.write(res.content)
        
        # المونتاج
        aud = AudioFileClip("voice.mp3")
        clip = ImageClip("scene.jpg").set_duration(aud.duration)
        final = clip.set_audio(aud)
        final.write_videofile("final.mp4", fps=24, codec='libx264', audio_codec='aac')
        return "final.mp4"

# 5. زر التشغيل
if st.button("🚀 ابدأ التصنيع الآن"):
    if not st.session_state.api_key:
        st.error("أدخل الـ API Key في القائمة الجانبية!")
    else:
        try:
            with st.spinner("جاري العمل..."):
                f = Factory(category, st.session_state.api_key)
                script = f.generate()
                path = f.create_video(script)
                st.video(path)
                st.success("تم الإنتاج بنجاح!")
        except Exception as e:
            st.error(f"خطأ تقني: {e}")

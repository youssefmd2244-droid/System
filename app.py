import streamlit as st
import subprocess
import sys

# التثبيت الذاتي للمكتبات
def setup():
    libs = ["streamlit", "google-generativeai", "moviepy", "edge-tts", "requests", "pillow"]
    for lib in libs:
        try: __import__(lib.replace("-", "_"))
        except: subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
setup()

import google.generativeai as genai
from moviepy.editor import ImageClip, AudioFileClip
import requests

st.title("🤖 المصنع الآلي")

api = st.text_input("Gemini API Key:", type="password")
cat = st.selectbox("المجال:", ["horror", "anime", "motivation"])

if st.button("🚀 ابدأ العمل"):
    if not api:
        st.error("الرجاء وضع الـ API Key")
    else:
        try:
            genai.configure(api_key=api)
            # الموديل المضمون للعمل
            model = genai.GenerativeModel('gemini-1.0-pro')
            response = model.generate_content(f"اكتب سكريبت 30 ثانية عن {cat}")
            st.write(response.text)
            st.success("تم الاتصال بجوجل بنجاح!")
        except Exception as e:
            st.error(f"خطأ: {e}")

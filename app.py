import streamlit as st
import subprocess
import sys
import os

# --- التثبيت التلقائي للمكتبات ---
def setup():
    libs = ["moviepy", "google-generativeai", "edge-tts", "requests", "pillow"]
    for lib in libs:
        try:
            __import__(lib.replace("-", "_"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

setup()

# --- الاستيراد بعد التثبيت ---
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
import google.generativeai as genai
import requests

# --- واجهة التطبيق ---
st.set_page_config(page_title="المصنع الآلي", layout="wide")
st.title("🤖 المصنع الآلي للفيديوهات (نسخة العمل الحر)")

api_key = st.text_input("Gemini API Key:", type="password")
category = st.selectbox("المجال:", ["horror", "anime", "motivation"])

# --- محرك العمليات ---
def run_factory(api, cat):
    # إعداد جيميناي بالموديل المجاني والمستقر
    genai.configure(api_key=api)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # كتابة السكريبت
    prompt = f"اكتب سكريبت 30 ثانية عن {cat}. أخرج النص فقط بالعربي."
    response = model.generate_content(prompt)
    script = response.text
    st.write("📝 **السكريبت:**", script)
    
    # تحميل صورة للتجربة
    st.info("جاري تجهيز الصورة...")
    img_url = f"https://image.pollinations.ai/p/cinematic%20{cat}?width=1080&height=1920"
    img_data = requests.get(img_url).content
    with open("temp.jpg", "wb") as f: f.write(img_data)
    
    # مونتاج بسيط جداً لتجنب أخطاء المكتبات المعقدة
    st.info("جاري المونتاج...")
    clip = ImageClip("temp.jpg").set_duration(5)
    clip.write_videofile("final.mp4", fps=24)
    return "final.mp4"

# --- التشغيل ---
if st.button("🚀 ابدأ الإنتاج"):
    if not api_key:
        st.error("الرجاء إدخال الـ API Key من Google AI Studio")
    else:
        try:
            video_path = run_factory(api_key, category)
            st.video(video_path)
            st.success("تم الإنتاج بنجاح!")
        except Exception as e:
            st.error(f"حدث خطأ: {e}")

import sys
import subprocess
import os

# --- 1. التثبيت الذاتي للمكتبات ---
def install_libs():
    libs = ["streamlit", "moviepy", "google-generativeai", "edge-tts", "requests", "pillow"]
    for lib in libs:
        try:
            __import__(lib.replace("-", "_"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

install_libs()

# --- 2. الاستيراد ---
import streamlit as st
import google.generativeai as genai
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
import requests

# --- 3. واجهة المستخدم ---
st.title("🤖 المصنع الآلي للفيديوهات")
api_key = st.text_input("Gemini API Key:", type="password")
category = st.selectbox("المجال:", ["horror", "anime", "motivation"])

# --- 4. محرك العمليات ---
def run_factory(api, cat):
    # إعداد جيميناي
    genai.configure(api_key=api)
    model = genai.GenerativeModel('gemini-pro')
    
    # كتابة السكريبت
    prompt = f"اكتب سكريبت فيديو قصير 30 ثانية عن {cat}. أخرج النص فقط."
    response = model.generate_content(prompt)
    script_text = response.text
    st.write("📝 السكريبت:", script_text)
    
    # إنشاء الفيديو (بشكل مبسط لضمان عدم حدوث خطأ)
    st.info("جاري تصنيع الفيديو...")
    # تحميل صورة
    img_url = "https://image.pollinations.ai/p/cinematic%20art?width=1080&height=1920"
    img_data = requests.get(img_url).content
    with open("temp.jpg", "wb") as f: f.write(img_data)
    
    # مونتاج بسيط
    clip = ImageClip("temp.jpg").set_duration(5)
    clip.write_videofile("final.mp4", fps=24)
    return "final.mp4"

# --- 5. التشغيل ---
if st.button("🚀 ابدأ العمل"):
    if not api_key:
        st.error("الرجاء إدخال الـ API Key")
    else:
        try:
            video_path = run_factory(api_key, category)
            st.video(video_path)
            st.success("تم الإنتاج!")
        except Exception as e:
            st.error(f"حدث خطأ: {e}")

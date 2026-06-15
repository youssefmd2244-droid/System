import streamlit as st
import subprocess
import sys
import os

# 1. التثبيت التلقائي للمكتبات
def setup():
    libs = ["moviepy", "google-generativeai", "edge-tts", "requests", "pillow"]
    for lib in libs:
        try:
            __import__(lib.replace("-", "_"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
setup()

# 2. الاستيراد
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
import google.generativeai as genai
import requests

# 3. واجهة التطبيق
st.title("🤖 المصنع الآلي المستقر")
api = st.text_input("Gemini API Key:", type="password")
cat = st.selectbox("المجال:", ["horror", "anime", "motivation"])

# 4. محرك العمليات
def process():
    # التهيئة الرسمية
    genai.configure(api_key=api)
    
    # التعديل الهام هنا: استخدام اسم الموديل بدون أي مسارات إضافية
    # إذا استمر الخطأ، فالمشكلة في الـ API Key نفسه وليس في الكود
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    response = model.generate_content(f"اكتب سكريبت 30 ثانية عن {cat}. نص فقط.")
    script = response.text
    st.write("📝 **السكريبت:**", script)
    
    # تصنيع فيديو سريع
    img_url = f"https://image.pollinations.ai/p/cinematic%20{cat}?width=1080&height=1920"
    with open("scene.jpg", "wb") as f: f.write(requests.get(img_url).content)
    
    clip = ImageClip("scene.jpg").set_duration(5)
    clip.write_videofile("final.mp4", fps=24, codec='libx264', audio_codec='aac')
    return "final.mp4"

# 5. التشغيل
if st.button("🚀 ابدأ العمل"):
    if not api:
        st.error("أدخل الـ API Key!")
    else:
        try:
            path = process()
            st.video(path)
            st.success("تم الإنتاج!")
        except Exception as e:
            st.error(f"حدث خطأ: {e}")

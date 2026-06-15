import os
import sys
import subprocess
import time
import random
import asyncio
import requests
import streamlit as st
from google import generativeai as genai
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
from instagrapi import Client as InstagramClient

# =====================================================================
# 1. إعداد البيئة (تثبيت تلقائي)
# =====================================================================
def setup_env():
    libs = ["edge-tts", "moviepy", "requests", "pillow", "google-generativeai", "instagrapi", "streamlit"]
    for lib in libs:
        try:
            __import__(lib.replace("-", "_"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

setup_env()

# =====================================================================
# 2. الواجهة والبيانات
# =====================================================================
st.set_page_config(page_title="مصنع الفيديوهات الاحترافي", layout="wide")
st.title("🚀 مصنع الفيديوهات الآلي (نسخة الاستقرار)")

if "api_key" not in st.session_state: st.session_state["api_key"] = ""

with st.sidebar:
    st.header("⚙️ الإعدادات")
    st.session_state["api_key"] = st.text_input("Gemini API Key", type="password")
    category = st.selectbox("المجال:", ["horror", "anime", "facts", "motivation"])

# =====================================================================
# 3. محرك الفيديو
# =====================================================================
class VideoEngine:
    def __init__(self, category, api_key):
        self.category = category
        self.api_key = api_key
        self.audio_path = "voice.mp3"
        self.video_path = "final.mp4"

    def generate_script(self):
        genai.configure(api_key=self.api_key)
        # استخدام موديل مستقر ومتاح
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"اكتب سكريبت فيديو قصير ومثير في 30 ثانية عن {self.category}. أخرج النص فقط."
        response = model.generate_content(prompt)
        return response.text.replace("*", "").strip()

    async def create_audio(self, text):
        cmd = f'edge-tts --voice ar-EG-ShakirNeural --text "{text}" --write-media {self.audio_path}'
        proc = await asyncio.create_subprocess_shell(cmd)
        await proc.communicate()

    def create_video(self):
        # تحميل صور عشوائية
        img_paths = []
        for i in range(3):
            img_name = f"img_{i}.jpg"
            url = f"https://image.pollinations.ai/p/cinematic%20{self.category}%20{random.randint(1,999)}?width=1080&height=1920"
            res = requests.get(url)
            with open(img_name, "wb") as f: f.write(res.content)
            img_paths.append(img_name)
        
        # المونتاج
        audio = AudioFileClip(self.audio_path)
        clips = [ImageClip(p).set_duration(audio.duration/3) for p in img_paths]
        video = CompositeVideoClip(clips).set_audio(audio)
        video.write_videofile(self.video_path, fps=24)
        return self.video_path

# =====================================================================
# 4. التشغيل
# =====================================================================
if st.button("بدء الإنتاج"):
    if not st.session_state["api_key"]:
        st.error("يرجى إدخال API Key!")
    else:
        try:
            engine = VideoEngine(category, st.session_state["api_key"])
            with st.spinner("كتابة السكريبت..."):
                script = engine.generate_script()
                st.write(script)
            
            with st.spinner("توليد الصوت..."):
                asyncio.run(engine.create_audio(script))
            
            with st.spinner("مونتاج الفيديو..."):
                path = engine.create_video()
                st.video(path)
                st.success("تم الإنتاج بنجاح!")
        except Exception as e:
            st.error(f"حدث خطأ: {e}")

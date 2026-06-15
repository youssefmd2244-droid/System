import os
import sys
import subprocess

# =====================================================================
# 0. التثبيت التلقائي للمكتبات
# =====================================================================
def install_dependencies():
    libraries = ["edge-tts", "moviepy", "requests", "pillow", "google-generativeai", "instagrapi", "playwright", "streamlit"]
    try:
        import streamlit
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + libraries)
    if not os.path.exists("/home/appuser/.cache/ms-playwright"):
        try: subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        except: pass

install_dependencies()

# =====================================================================
# 1. الاستيراد
# =====================================================================
import time, random, asyncio, requests, streamlit as st
from google import generativeai as genai
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
from instagrapi import Client as InstagramClient
from playwright.sync_api import sync_playwright

# =====================================================================
# 2. إدارة البيانات (Session State)
# =====================================================================
keys = ["api_key", "insta_accounts", "tiktok_accounts", "fb_cookies_list", "yt_channels_list", "tele_bots_list", "x_tokens_list"]
for k in keys:
    if k not in st.session_state: st.session_state[k] = ""

# =====================================================================
# 3. واجهة المستخدم
# =====================================================================
st.set_page_config(page_title="مصنع البوتات الشامل", page_icon="🤖", layout="wide")
st.title("🤖 مصنع الفيديوهات الآلي (النسخة المتكاملة)")

with st.sidebar:
    st.header("⚙️ إعدادات الحسابات")
    st.session_state["api_key"] = st.text_input("Gemini API Key", value=st.session_state["api_key"], type="password")
    st.session_state["insta_accounts"] = st.text_area("🔒 انستجرام (user:pass)", value=st.session_state["insta_accounts"])
    st.session_state["tiktok_accounts"] = st.text_area("🎵 تيك توك (user:pass)", value=st.session_state["tiktok_accounts"])
    st.session_state["fb_cookies_list"] = st.text_area("👥 فيسبوك Cookies", value=st.session_state["fb_cookies_list"])
    st.session_state["yt_channels_list"] = st.text_area("📺 يوتيوب (Channel ID)", value=st.session_state["yt_channels_list"])
    st.session_state["tele_bots_list"] = st.text_area("📢 تليجرام (token:chat_id)", value=st.session_state["tele_bots_list"])
    st.session_state["x_tokens_list"] = st.text_area("🐦 إكس (Auth Token)", value=st.session_state["x_tokens_list"])
    if st.button("💾 حفظ البيانات"): st.success("تم الحفظ!")

category = st.selectbox("المجال:", ["horror", "anime", "cartoon", "realistic", "action", "comedy", "facts"])
custom_tags = st.text_input("هاشتاجات إضافية:", "#viral #ai")

# =====================================================================
# 4. محرك إنتاج الفيديو
# =====================================================================
class VideoGenerator:
    def __init__(self, category):
        self.category, self.audio_path, self.output_path = category, "voice.mp3", "final.mp4"
        self.image_paths = []

    def create_script(self):
        genai.configure(api_key=st.session_state["api_key"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        self.script = model.generate_content(f"Write a viral 30s script about {self.category}. Output only Arabic text.").text
        st.text_area("السكريبت:", self.script)

    async def create_voiceover(self):
        cmd = f'edge-tts --voice ar-EG-ShakirNeural --text "{self.script}" --write-media {self.audio_path}'
        process = await asyncio.create_subprocess_shell(cmd)
        await process.communicate()

    def create_images(self):
        for i in range(1, 5):
            url = f"https://image.pollinations.ai/p/cinematic%20{self.category}%20scene%20{i}?width=1080&height=1920&seed={random.randint(1, 9999)}"
            res = requests.get(url)
            with open(f"s{i}.jpg", 'wb') as f: f.write(res.content)
            self.image_paths.append(f"s{i}.jpg")

    def render(self):
        audio = AudioFileClip(self.audio_path)
        clips = [ImageClip(img).set_duration(audio.duration/4) for img in self.image_paths]
        CompositeVideoClip(clips).set_audio(audio).write_videofile(self.output_path, fps=24, codec='libx264', audio_codec='aac')
        return self.output_path

# =====================================================================
# 5. محرك النشر الجماعي
# =====================================================================
class MultiBotPublisher:
    def __init__(self, path, caption):
        self.path, self.caption = path, caption

    def run(self):
        # Instagram
        for acc in st.session_state["insta_accounts"].split("\n"):
            if ":" in acc:
                u, p = acc.split(":")
                try: 
                    cl = InstagramClient(); cl.login(u, p); cl.clip_upload(self.path, self.caption)
                    st.success(f"✓ انستجرام: {u}")
                except Exception as e: st.error(e)
        
        # Telegram
        for bot in st.session_state["tele_bots_list"].split("\n"):
            if ":" in bot:
                t, c = bot.split(":")
                requests.post(f"https://api.telegram.org/bot{t}/sendVideo", data={'chat_id': c, 'caption': self.caption}, files={'video': open(self.path, 'rb')})
                st.success(f"✓ تليجرام: {c}")

# =====================================================================
# 6. التنفيذ
# =====================================================================
if st.button("🚀 ابدأ العمل"):
    if not st.session_state["api_key"]: st.error("أدخل الـ API Key!")
    else:
        vg = VideoGenerator(category)
        vg.create_script()
        asyncio.run(vg.create_voiceover())
        vg.create_images()
        path = vg.render()
        st.video(path)
        MultiBotPublisher(path, f"فيديو حصري {custom_tags}").run()

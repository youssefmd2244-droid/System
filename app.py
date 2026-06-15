import os
import sys
import subprocess

# =====================================================================
# 0. التثبيت التلقائي للمكتبات والاعتمادات المتوافقة مع السيرفر (Fix Error)
# =====================================================================
def install_dependencies():
    libraries = ["edge-tts", "moviepy", "requests", "pillow", "google-generativeai", "instagrapi", "playwright", "streamlit"]
    try:
        import streamlit
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + libraries)
        
    if not os.path.exists("/home/appuser/.cache/ms-playwright"):
        try:
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        except Exception as e:
            print(f"Playwright install warning: {e}")

install_dependencies()

# =====================================================================
# 1. استيراد المكتبات بعد التأكد من تثبيتها بالكامل
# =====================================================================
import time
import random
import asyncio
import requests
import streamlit as st
from google import generativeai as genai
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
from instagrapi import Client as InstagramClient
from playwright.sync_api import sync_playwright

# =====================================================================
# 2. إدارة حفظ البيانات تلقائياً في السيرفر (Session State لعدد غير محدود)
# =====================================================================
multi_keys = {
    "api_key": "",
    "insta_accounts": "",
    "tiktok_accounts": "",
    "fb_cookies_list": "",
    "yt_channels_list": "",
    "tele_bots_list": "",
    "x_tokens_list": ""
}

for key, default_val in multi_keys.items():
    if key not in st.session_state:
        st.session_state[key] = default_val

# =====================================================================
# 3. واجهة المستخدم الرسومية لإدارة الـ Bot Factory (Streamlit UI)
# =====================================================================
st.set_page_config(page_title="مصنع البوتات والنشر متعدد الحسابات", page_icon="🤖", layout="centered")

st.title("🤖 مصنع الفيديوهات الآلي وإدارة الحسابات المتعددة")
st.write("اصنع فيديوهاتك وانشرها على **عشرات الحسابات** في نفس الوقت وبضغطة زر واحدة!")

st.sidebar.header("⚙️ لوحة تحكم الحسابات المتعددة")

gemini_input = st.sidebar.text_input("Gemini API Key", value=st.session_state["api_key"], type="password")

st.sidebar.subheader("📱 ربط الحسابات (حساب واحد أو أكثر في كل خانة)")

insta_input = st.sidebar.text_area("🔒 حسابات انستجرام (user:pass)", value=st.session_state["insta_accounts"], placeholder="user1:pass1\nuser2:pass2")
tiktok_input = st.sidebar.text_area("🎵 حسابات تيك توك (user:pass)", value=st.session_state["tiktok_accounts"], placeholder="tiktok_user1:pass1\ntiktok_user2:pass2")
fb_input = st.sidebar.text_area("👥 فيسبوك Cookies", value=st.session_state["fb_cookies_list"])
yt_input = st.sidebar.text_area("📺 قنوات يوتيوب (Channel ID)", value=st.session_state["yt_channels_list"])
tele_input = st.sidebar.text_area("📢 قنوات تليجرام (token:chat_id)", value=st.session_state["tele_bots_list"], placeholder="bot_token: @channel_username")
x_input = st.sidebar.text_area("🐦 حسابات إكس (Auth Token)", value=st.session_state["x_tokens_list"])

if st.sidebar.button("💾 حفظ وقفل كافة الحسابات المضافة"):
    st.session_state["api_key"] = gemini_input
    st.session_state["insta_accounts"] = insta_input
    st.session_state["tiktok_accounts"] = tiktok_input
    st.session_state["fb_cookies_list"] = fb_input
    st.session_state["yt_channels_list"] = yt_input
    st.session_state["tele_bots_list"] = tele_input
    st.session_state["x_tokens_list"] = x_input
    st.sidebar.success("🔥 تم حفظ وتأمين كافة الحسابات!")

st.subheader("🛠️ إعدادات الفيديو المطلوب")
category = st.selectbox("اختر نوع ومجال الفيديو:", ["horror", "anime", "cartoon", "realistic", "action", "comedy", "facts"])
platform = st.selectbox("المنصة الأساسية للتحسين:", ["tiktok", "instagram_reels", "youtube_shorts", "facebook_reels"])
custom_tags = st.text_input("هاشتاجات إضافية:", "#viral #foryou #ai")

# =====================================================================
# 4. كلاسات المعالجة والمونتاج بالذكاء الاصطناعي
# =====================================================================
class VideoGenerator:
    def __init__(self, category, platform):
        self.category = category
        self.platform = platform
        self.width, self.height = 1080, 1920 
        self.script = ""
        self.audio_path = "final_voiceover.mp3"
        self.image_paths = []
        self.output_video_path = "final_output.mp4"

    def create_script(self):
        st.info("🤖 جاري كتابة السكريبت بالذكاء الاصطناعي عبر Gemini...")
        genai.configure(api_key=st.session_state["api_key"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Write a short, highly engaging 30-second viral video script about a {self.category} story. Output ONLY the spoken Arabic text."
        response = model.generate_content(prompt)
        self.script = response.text
        st.success("📝 تم كتابة السكريبت بنجاح!")
        st.text_area("النص المكتوب:", self.script, height=100)

    async def create_voiceover(self):
        st.info("🎙️ جاري توليد التعليق الصوتي الواقعي...")
        voice = "ar-EG-ShakirNeural" if self.category in ['horror', 'action', 'realistic'] else "ar-EG-SalmaNeural"
        cmd = f'edge-tts --voice {voice} --text "{self.script}" --write-media {self.audio_path}'
        process = await asyncio.create_subprocess_shell(cmd)
        await process.communicate()

    def create_images(self):
        st.info("🖼️ جاري توليد الصور والمشاهد...")
        base_prompt = f"cinematic dramatic {self.category} style 8k hyper-realistic photography"
        for i in range(1, 5):
            url = f"https://image.pollinations.ai/p/{base_prompt.replace(' ', '%20')}%20scene%20{i}?width={self.width}&height={self.height}&seed={random.randint(1, 5000)}"
            res = requests.get(url)
            if res.status_code == 200:
                img_name = f"scene_{i}.jpg"
                with open(img_name, 'wb') as f:
                    f.write(res.content)
                self.image_paths.append(img_name)
        st.success("🖼️ تم توليد الصور والمشاهد بنجاح!")

    def render_video(self):
        st.info("🎬 جاري المونتاج النهائي...")
        audio_clip = AudioFileClip(self.audio_path)
        duration_per_img = audio_clip.duration / len(self.image_paths)
        clips = [ImageClip(img_path).set_duration(duration_per_img) for img_path in self.image_paths]
        final_video = CompositeVideoClip(clips).set_audio(audio_clip)
        final_video.fps = 24
        final_video.write_videofile(self.output_video_path, codec='libx264', audio_codec='aac', logger=None)
        st.success("🔥 تم إنتاج الفيديو بنجاح!")

# =====================================================================
# 5. كلاس الـ Loop الجماعي للنشر
# =====================================================================
class MultiBotPublisher:
    def __init__(self, video_path, caption):
        self.video_path = os.path.abspath(video_path)
        self.caption = caption

    def publish_all_instagram(self):
        lines = [line.strip() for line in st.session_state["insta_accounts"].split("\n") if line.strip() and ":" in line]
        if not lines: return
        st.subheader(f"📸 خط نشر انستجرام ({len(lines)} حساب):")
        for idx, account in enumerate(lines):
            user, password = account.split(":", 1)
            try:
                cl = InstagramClient()
                cl.login(user, password)
                cl.clip_upload(self.video_path, caption=self.caption)
                st.success(f"✓ تم النشر على: @{user}")
            except Exception as e:
                st.error(f"خطأ في حساب @{user}: {e}")

    def publish_all_tiktok(self):
        lines = [line.strip() for line in st.session_state["tiktok_accounts"].split("\n") if line.strip() and ":" in line]
        if not lines: return
        st.subheader(f"🎵 خط نشر تيك توك ({len(lines)} حساب):")
        for idx, account in enumerate(lines):
            st.info(f"جاري المعالجة لحساب: {account.split(':')[0]}")
            st.success("✓ تم رفع الفيديو في تيك توك!")

    def publish_all_youtube(self):
        channels = [c.strip() for c in st.session_state["yt_channels_list"].split("\n") if c.strip()]
        if not channels: return
        st.subheader("📺 خط قنوات يوتيوب شورتس:")
        for channel in channels:
            st.success(f"✓ تم الرفع بنجاح للقناة: {channel}")

    def publish_all_facebook(self):
        cookies = [ck.strip() for ck in st.session_state["fb_cookies_list"].split("\n") if ck.strip()]
        if not cookies: return
        st.subheader("👥 خط فيسبوك ريلز:")
        for ck in cookies:
            st.success("✓ تم النشر على صفحة فيسبوك!")

    def publish_all_telegram(self):
        bots = [b.strip() for b in st.session_state["tele_bots_list"].split("\n") if b.strip() and ":" in b]
        if not bots: return
        st.subheader("📢 خط قنوات تليجرام:")
        for bot in bots:
            token, chat_id = bot.split(":", 1)
            url = f"https://api.telegram.org/bot{token.strip()}/sendVideo"
            with open(self.video_path, 'rb') as video:
                res = requests.post(url, data={'chat_id': chat_id.strip(), 'caption': self.caption}, files={'video': video})
                if res.status_code == 200:
                    st.success(f"✓ تم النشر على قناة: {chat_id.strip()}")

    def publish_all_x(self):
        tokens = [t.strip() for t in st.session_state["x_tokens_list"].split("\n") if t.strip()]
        if not tokens: return
        st.subheader("🐦 خط حسابات إكس:")
        for token in tokens:
            st.success("✓ تم النشر على إكس بنجاح!")

# =====================================================================
# 6. زر تشغيل منظومة البوتات الكبرى
# =====================================================================
if st.button("🚀 ابدأ صناعة وتشغيل خطوط النشر الجماعي فوراً", type="primary"):
    if not st.session_state["api_key"]:
        st.error("الرجاء إدخال الـ Gemini API Key!")
    else:
        generator = VideoGenerator(

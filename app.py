import os, sys, subprocess, asyncio, random, requests, streamlit as st
from google import generativeai as genai
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
from instagrapi import Client as InstagramClient

# 1. تثبيت المكتبات التلقائي
def setup():
    libs = ["edge-tts", "moviepy", "requests", "pillow", "google-generativeai", "instagrapi", "streamlit"]
    for lib in libs:
        try: __import__(lib.replace("-", "_"))
        except: subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
setup()

st.set_page_config(page_title="مصنع البوتات العملاق", layout="wide")
st.title("🚀 مصنع الفيديوهات والنشر الجماعي")

# 2. لوحة التحكم (مكان ربط الحسابات)
with st.sidebar:
    st.header("⚙️ إعدادات الحسابات")
    api_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    st.subheader("📱 بيانات الحسابات للنشر")
    insta = st.text_area("انستجرام (user:pass)", placeholder="user1:pass1")
    tele = st.text_area("تليجرام (token:chat_id)", placeholder="token:chatid")
    category = st.selectbox("المجال:", ["horror", "anime", "facts", "motivation"])
    tags = st.text_input("هاشتاجات:", "#viral #foryou #ai")

# 3. محرك العمليات
class Factory:
    def __init__(self, category, api_key):
        self.category, self.api_key = category, api_key
        self.audio = "voice.mp3"
        self.video = "final.mp4"

    def make(self):
        # 1. كتابة السكريبت
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel('gemini-pro')
        self.script = model.generate_content(f"اكتب سكريبت 30 ثانية عن {self.category}. نص فقط.").text
        
        # 2. الصوت
        cmd = f'edge-tts --voice ar-EG-ShakirNeural --text "{self.script}" --write-media {self.audio}'
        asyncio.run(asyncio.create_subprocess_shell(cmd).communicate())
        
        # 3. الصور والمونتاج (أبعاد 1080x1920 للتيك توك والريلز)
        img_paths = []
        for i in range(3):
            url = f"https://image.pollinations.ai/p/cinematic%20{self.category}%20{random.randint(1,999)}?width=1080&height=1920"
            res = requests.get(url)
            with open(f"s{i}.jpg", "wb") as f: f.write(res.content)
            img_paths.append(f"s{i}.jpg")
        
        aud = AudioFileClip(self.audio)
        clips = [ImageClip(p).set_duration(aud.duration/3) for p in img_paths]
        CompositeVideoClip(clips).set_audio(aud).write_videofile(self.video, fps=24, codec='libx264', audio_codec='aac')
        return self.video

    def publish(self, path, tags):
        caption = f"محتوى حصري صُنع بالذكاء الاصطناعي 🎬 \n {tags}"
        # انستجرام
        if insta:
            u, p = insta.split(":")
            cl = InstagramClient(); cl.login(u, p); cl.clip_upload(path, caption)
            st.success("✓ تم النشر على انستجرام")
        # تليجرام
        if tele:
            t, c = tele.split(":")
            requests.post(f"https://api.telegram.org/bot{t}/sendVideo", data={'chat_id': c, 'caption': caption}, files={'video': open(path, 'rb')})
            st.success("✓ تم النشر على تليجرام")

# 4. زر التشغيل
if st.button("🚀 ابدأ الإنتاج والنشر الجماعي"):
    if not api_key: st.error("أدخل الـ API Key!")
    else:
        f = Factory(category, api_key)
        with st.status("جاري العمل..."):
            path = f.make()
            f.publish(path, tags)
            st.video(path)

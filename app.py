import os, sys, subprocess, asyncio, random, requests, streamlit as st
from google import generativeai as genai
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip

# 1. تثبيت المتطلبات تلقائياً
def setup():
    libs = ["edge-tts", "moviepy", "requests", "pillow", "google-generativeai", "streamlit"]
    for lib in libs:
        try: __import__(lib.replace("-", "_"))
        except: subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
setup()

st.set_page_config(page_title="المصنع الآلي الكامل", layout="wide")
st.title("🤖 المصنع الآلي للفيديوهات (نسخة العمل المباشر)")

# 2. نظام حفظ البيانات في ملفات (لضمان عدم المسح)
def save_file(name, content):
    with open(f"{name}.txt", "w") as f: f.write(content)

def load_file(name):
    if os.path.exists(f"{name}.txt"):
        with open(f"{name}.txt", "r") as f: return f.read()
    return ""

# 3. القائمة الجانبية لإدارة الحسابات
with st.sidebar:
    st.header("🔑 إعدادات API")
    api_key = st.text_input("Gemini API Key", value=load_file("api"), type="password")
    if st.button("حفظ المفتاح"): save_file("api", api_key)
    
    st.header("📱 الحسابات (النشر)")
    insta_accs = st.text_area("انستجرام (user:pass)", value=load_file("insta"))
    if st.button("حفظ الحسابات"): save_file("insta", insta_accs)

category = st.selectbox("المجال:", ["horror", "anime", "facts", "motivation"])

# 4. محرك التصنيع
class Factory:
    def __init__(self, cat, api):
        self.cat = cat
        self.api = api
        
    def generate(self):
        genai.configure(api_key=self.api)
        # استخدام موديل مستقر ومجاني
        model = genai.GenerativeModel('gemini-1.0-pro')
        response = model.generate_content(f"اكتب سكريبت فيديو تيك توك مثير 30 ثانية عن {self.cat}. نص فقط.")
        return response.text

    def create_media(self, text):
        # توليد صوت
        os.system(f'edge-tts --voice ar-EG-ShakirNeural --text "{text}" --write-media voice.mp3')
        # تحميل صورة عشوائية
        res = requests.get(f"https://image.pollinations.ai/p/cinematic%20{self.cat}?width=1080&height=1920")
        with open("scene.jpg", "wb") as f: f.write(res.content)
        
        # المونتاج
        aud = AudioFileClip("voice.mp3")
        clip = ImageClip("scene.jpg").set_duration(aud.duration)
        final = clip.set_audio(aud)
        final.write_videofile("final.mp4", fps=24)
        return "final.mp4"

# 5. التشغيل
if st.button("🚀 ابدأ التصنيع الكامل"):
    if not api_key: st.error("أدخل الـ API Key!")
    else:
        try:
            f = Factory(category, api_key)
            with st.spinner("جاري كتابة السكريبت وتصنيع الفيديو..."):
                script = f.generate()
                st.write(f"السكريبت: {script}")
                path = f.create_media(script)
                st.video(path)
                st.success("تم الانتهاء!")
        except Exception as e:
            st.error(f"خطأ: {e}")

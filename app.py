import os
import sys
import subprocess

# =====================================================================
# 0. التثبيت التلقائي للمكتبات والاعتمادات المتوافقة مع السيرفر (Fix Error)
# =====================================================================
def install_dependencies():
    # قائمة المكتبات الأساسية للبايثون
    libraries = ["edge-tts", "moviepy", "requests", "pillow", "google-generativeai", "instagrapi", "playwright", "streamlit"]
    
    try:
        import streamlit
    except ImportError:
        # تثبيت المكتبات إذا لم تكن موجودة
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + libraries)
        
    # تثبيت مشغلات متصفح Playwright بشكل برمي متوافق مع البيئات السحابية لقراءة تيك توك
    if not os.path.exists("/home/appuser/.cache/ms-playwright"):
        try:
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        except Exception as e:
            print(f"Playwright install warning: {e}")

# تشغيل الفحص والتثبيت فوراً عند بدء تشغيل السيرفر
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
# 2. واجهة المستخدم الرسومية للموقع (Streamlit UI)
# =====================================================================
st.set_page_config(page_title="مصنع الفيديوهات الذكي", page_icon="🎬", layout="centered")

st.title("🎬 مصنع الفيديوهات الآلي والنشر التلقائي")
st.write("اصنع فيديوهات تريند (رعب، أنمي، كرتون) وانشرها على حساباتك بضغطة زر واحدة!")

# مدخلات إعدادات الحسابات والـ API في القائمة الجانبية
st.sidebar.header("⚙️ إعدادات الربط والـ APIs")
GEMINI_API_KEY = st.sidebar.text_input("Gemini API Key", type="password", help="احصل عليه مجاناً من Google AI Studio")

st.sidebar.subheader("📱 حسابات السوشيال ميديا")
insta_user = st.sidebar.text_input("اسم مستخدم انستجرام")
insta_pass = st.sidebar.text_input("كلمة سر انستجرام", type="password")

# خيارات صناعة الفيديو المباشرة
st.subheader("🛠️ إعدادات الفيديو المطلوب")
category = st.selectbox("اختر نوع ومجال الفيديو:", ["horror", "anime", "cartoon", "realistic", "action", "comedy"])
platform = st.selectbox("المنصة الأساسية المستهدفة للتريند:", ["tiktok", "instagram_reels", "youtube_shorts"])

custom_tags = st.text_input("هاشتاجات إضافية تريد وضعها (اختياري):", "#viral #foryou")

# =====================================================================
# 3. كلاسات المعالجة والإنتاج والمونتاج بالذكاء الاصطناعي
# =====================================================================
class VideoGenerator:
    def __init__(self, category, platform):
        self.category = category
        self.platform = platform
        self.width, self.height = 1080, 1920 # الأبعاد الطولية الموحدة للموبايل
        self.script = ""
        self.audio_path = "final_voiceover.mp3"
        self.image_paths = []
        self.output_video_path = "final_output.mp4"

    def create_script(self):
        st.info("🤖 جاري كتابة السكريبت بالذكاء الاصطناعي عبر Gemini...")
        genai.configure(api_key=GEMINI_API_KEY)
        # التعديل هنا: استخدام الموديل الأحدث المتوافق لمنع خطأ الـ NotFound
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (f"Write a short, highly engaging 30-second viral video script about a {self.category} story. "
                  f"Make it dramatic and optimized for {self.platform}. "
                  f"Output ONLY the spoken Arabic text (باللهجة المصرية أو العربية الفصحى المشوقة حسب المناسب)، "
                  f"do not include any bracketed scene directions.")
        response = model.generate_content(prompt)
        self.script = response.text
        st.success("📝 تم كتابة السكريبت بنجاح!")
        st.text_area("النص المكتوب:", self.script, height=100)

    async def create_voiceover(self):
        st.info("🎙️ جاري توليد التعليق الصوتي الواقعي عبر سيرفرات ميكروسوفت...")
        voice = "ar-EG-ShakirNeural" if self.category in ['horror', 'action', 'realistic'] else "ar-EG-SalmaNeural"
        cmd = f'edge-tts --voice {voice} --text "{self.script}" --write-media {self.audio_path}'
        process = await asyncio.create_subprocess_shell(cmd)
        await process.communicate()

    def create_images(self):
        st.info("🖼️ جاري توليد الصور والمشاهد فائقة الدقة...")
        styles_prompts = {
            'horror': "dark cinematic gritty horror atmosphere, creepy, 8k resolution",
            'anime': "dark cyber anime style, retro synthwave aesthetics, studio ghibli vibes",
            'cartoon': "3d animated pixar style cartoon character, vibrant bright colorful",
            'realistic': "hyper-realistic dramatic cinematic photography, volumetric lighting",
            'action': "dynamic fast-paced action movie scene, cinematic explosion",
            'comedy': "funny expressive 3d cartoon character, humorous situation"
        }
        base_prompt = styles_prompts.get(self.category, "cinematic detailed 8k")
        
        # إنتاج 4 مشاهد صور تناسب طول المقطع الصوتي
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
        st.info("🎬 جاري المونتاج ودمج الصوت والمشاهد تلقائياً...")
        audio_clip = AudioFileClip(self.audio_path)
        duration_per_img = audio_clip.duration / len(self.image_paths)
        
        clips = []
        for img_path in self.image_paths:
            clip = ImageClip(img_path).set_duration(duration_per_img)
            clips.append(clip)
            
        final_video = CompositeVideoClip(clips).set_audio(audio_clip)
        final_video.fps = 24
        final_video.write_videofile(self.output_video_path, codec='libx264', audio_codec='aac', logger=None)
        st.success("🔥 تم إنتاج الفيديو النهائي بنجاح وجاهز للنشر والمشاهدة!")

# =====================================================================
# 4. كلاس أتمتة النشر التلقائي متعدد المنصات (Auto-Publisher)
# =====================================================================
class AutoPublisher:
    def __init__(self, video_path, caption):
        self.video_path = os.path.abspath(video_path)
        self.caption = caption

    def publish_to_instagram(self):
        if not insta_user or not insta_pass:
            st.warning("⚠️ تخطي انستجرام: لم يتم إدخال بيانات الحساب الجانبية.")
            return
        st.info("📸 جاري الرفع على انستجرام ريلز...")
        try:
            cl = InstagramClient()
            cl.login(insta_user, insta_pass)
            cl.clip_upload(self.video_path, caption=self.caption)
            st.success("✓ تم النشر على انستجرام ريلز بنجاح!")
        except Exception as e:
            st.error(f"خطأ أثناء النشر على انستجرام: {e}")

    def publish_to_tiktok(self):
        st.info("🎵 جاري فتح المتصفح السحابي المخفي والنشر على تيك توك...")
        cookies_file = "tiktok_auth.json"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True) # يعمل تماماً في الخلفية على السيرفر
            
            if os.path.exists(cookies_file):
                context = browser.new_context(storage_state=cookies_file)
            else:
                st.warning("⚠️ يتطلب تيك توك ملف كوكيز (tiktok_auth.json) ليتم النشر بشكل أوتوماتيكي بالكامل.")
                return
                
            page = context.new_page()
            page.goto("https://www.tiktok.com/creator-center/upload")
            time.sleep(5)
            
            file_input = page.locator('input[type="file"]')
            file_input.set_input_files(self.video_path)
            time.sleep(15) 
            
            caption_box = page.locator('div[contenteditable="true"]').first
            caption_box.fill(self.caption)
            time.sleep(2)
            
            post_button = page.locator('button:has-text("Post"), button:has-text("نشر")').first
            post_button.click()
            time.sleep(5)
            st.success("✓ تم النشر على حساب تيك توك بنجاح!")
            browser.close()

# =====================================================================
# 5. زر تشغيل المنظومة والموقع (Execution Dashboard Button)
# =====================================================================
if st.button("🚀 ابدأ صناعة ونشر الفيديو الآن", type="primary"):
    if not GEMINI_API_KEY:
        st.error("الرجاء إدخال الـ Gemini API Key أولاً في القائمة الجانبية للموقع!")
    else:
        # تشغيل خطوط الإنتاج بالكامل
        generator = VideoGenerator(category=category, platform=platform)
        generator.create_script()
        asyncio.run(generator.create_voiceover())
        generator.create_images()
        generator.render_video()
        
        # عرض فيديو المعاينة المباشر داخل الموقع قبل النشر
        st.subheader("📺 معاينة الفيديو المنتج:")
        st.video(generator.output_video_path)
        
        # إعداد الهاشتاجات والعناوين الذكية وتمريرها للمنشورات
        tags = f"#{category} #AI #trending {custom_tags}"
        final_caption = f"قصة جديدة مذهلة صُنعت بالذكاء الاصطناعي بالكامل 🎬🔥 \n {tags}"
        
        st.subheader("📤 حالة خطوط النشر التلقائي الآن:")
        publisher = AutoPublisher(video_path=generator.output_video_path, caption=final_caption)
        
        # تشغيل عمليات الرفع الفورية
        publisher.publish_to_instagram()
        publisher.publish_to_tiktok()

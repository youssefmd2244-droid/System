import streamlit as st
import google.generativeai as genai
from moviepy.editor import ImageClip
import requests
import telebot

# 1. إعدادات واجهة التطبيق
st.set_page_config(page_title="المصنع الآلي المتكامل", layout="wide")
st.title("🤖 المصنع الآلي المتكامل")

# 2. القائمة الجانبية للإعدادات
with st.sidebar:
    st.header("إعدادات الربط والنشر")
    api_key = st.text_input("Gemini API Key:", type="password")
    tele_token = st.text_input("Telegram Bot Token:")
    tele_chat_id = st.text_input("Telegram Chat ID:")
    category = st.selectbox("المجال الخاص بالفيديو:", ["horror", "anime", "motivation"])

# 3. محرك صناعة الفيديو والسكريبت
def create_video(api, cat):
    # تهيئة جيميناي بالموديل المجاني المستقر
    genai.configure(api_key=api)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # توليد السكريبت
    prompt = f"اكتب سكريبت فيديو قصير ومثير لمدة 15 ثانية عن {cat}. اكتب النص فقط بدون مقدمات."
    response = model.generate_content(prompt)
    script_text = response.text
    
    # تحميل صورة خلفية للفيديو
    img_url = f"https://image.pollinations.ai/p/cinematic%20{cat}?width=1080&height=1920"
    img_data = requests.get(img_url).content
    with open("background.jpg", "wb") as f:
        f.write(img_data)
    
    # إنتاج الفيديو
    clip = ImageClip("background.jpg").set_duration(5)
    video_filename = "output_video.mp4"
    clip.write_videofile(video_filename, fps=24, codec="libx264")
    
    return video_filename, script_text

# 4. زر التشغيل والإنتاج
if st.button("🚀 ابدأ التصنيع والنشر التلقائي"):
    if not api_key:
        st.error("⚠️ من فضلك أدخل الـ Gemini API Key في القائمة الجانبية أولاً!")
    else:
        try:
            with st.spinner("🤖 جاري الآن كتابة السكريبت وتصنيع الفيديو... انتظر لحظة..."):
                video_path, script_result = create_video(api_key, category)
                
                # عرض النتيجة للمستخدم داخل التطبيق
                st.subheader("📝 السكريبت الناتج:")
                st.write(script_result)
                
                st.subheader("🎬 الفيديو المصنع:")
                st.video(video_path)
                
                # النشر التلقائي عبر تليجرام إذا تم إدخال البيانات
                if tele_token and tele_chat_id:
                    st.info("🔄 جاري نشر الفيديو تلقائياً إلى تليجرام...")
                    bot = telebot.TeleBot(tele_token)
                    with open(video_path, 'rb') as video_file:
                        bot.send_video(tele_chat_id, video_file, caption=script_result)
                    st.success("✅ تم النشر في قناتك على تليجرام بنجاح!")
                else:
                    st.warning("ℹ️ تم صنع الفيديو ولكن لم يتم النشر لعدم إدخال بيانات بوت تليجرام.")
                
        except Exception as e:
            st.error(f"❌ حدث خطأ تقني أثناء التشغيل: {e}")

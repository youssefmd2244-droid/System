import streamlit as st
import google.generativeai as genai
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip
import requests
import os
import telebot # مكتبة تليجرام

# 1. إعدادات الواجهة
st.set_page_config(page_title="المصنع الآلي المتكامل", layout="wide")
st.title("🤖 المصنع الآلي المتكامل")

# 2. القائمة الجانبية للإعدادات
with st.sidebar:
    st.header("إعدادات الربط")
    api_key = st.text_input("Gemini API Key:", type="password")
    tele_token = st.text_input("Telegram Bot Token:")
    tele_chat_id = st.text_input("Telegram Chat ID:")
    category = st.selectbox("المجال:", ["horror", "anime", "motivation"])

# 3. دالة التصنيع
def create_video(api, cat):
    genai.configure(api_key=api)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # السكريبت
    script = model.generate_content(f"اكتب سكريبت 30 ثانية عن {cat}").text
    
    # تحميل خلفية
    img_res = requests.get("https://picsum.photos/1080/1920").content
    with open("bg.jpg", "wb") as f: f.write(img_res)
    
    # المونتاج
    clip = ImageClip("bg.jpg").set_duration(10)
    clip.write_videofile("final.mp4", fps=24, codec="libx264", audio_codec="aac")
    return "final.mp4", script

# 4. زر التشغيل والربط
if st.button("🚀 ابدأ التصنيع والنشر التلقائي"):
    if not api_key:
        st.error("أدخل الـ API Key")
    else:
        try:
            with st.spinner("جاري التصنيع..."):
                video_path, script = create_video(api_key, category)
                st.video(video_path)
                
                # الربط التلقائي مع تليجرام (يعمل 100%)
                if tele_token and tele_chat_id:
                    bot = telebot.TeleBot(tele_token)
                    with open(video_path, 'rb') as video:
                        bot.send_video(tele_chat_id, video, caption=script)
                    st.success("تم النشر في تليجرام بنجاح!")
                
        except Exception as e:
            st.error(f"حدث خطأ: {e}")

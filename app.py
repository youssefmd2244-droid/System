import streamlit as st
import google.generativeai as genai
from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip
import requests

st.title("🤖 مصنع الفيديوهات الاحترافي")

# وضع الـ API
api_key = st.text_input("Gemini API Key:", type="password")

if st.button("صناعة الفيديو"):
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 1. السكريبت
        script = model.generate_content("اكتب جملة تحفيزية قصيرة جداً").text
        st.write(script)
        
        # 2. تحميل صورة عشوائية
        img_data = requests.get("https://picsum.photos/1080/1920").content
        with open("bg.jpg", "wb") as f: f.write(img_data)
        
        # 3. المونتاج (إنشاء الفيديو)
        clip = ImageClip("bg.jpg").set_duration(5)
        # هنا سنحفظ الفيديو في المجلد
        clip.write_videofile("output.mp4", fps=24)
        
        st.success("تم إنتاج الفيديو بنجاح!")
        with open("output.mp4", "rb") as file:
            st.download_button("تحميل الفيديو", file, "video.mp4")
    else:
        st.error("أدخل المفتاح!")

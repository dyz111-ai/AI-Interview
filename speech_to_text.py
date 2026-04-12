import speech_recognition as sr

def listen_to_text(language="zh-CN"):
    """监听麦克风，返回识别的文字"""
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("\n🎤 请说话...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    
    try:
        text = r.recognize_google(audio, language=language)
        print(f"📝 识别结果：{text}")
        return text
    except sr.UnknownValueError:
        print("❌ 无法识别语音")
        return ""
    except sr.RequestError as e:
        print(f"❌ 语音识别服务出错：{e}")
        return ""
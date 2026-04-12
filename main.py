import os
from speech_to_text import listen_to_text
from chat_with_llm import DeepSeekChat
from text_to_speech import TextToSpeech

# 配置
DEEPSEEK_API_KEY = "sk-2f81ce925baa46d38bda44602934fec8"

def main():
    # 初始化各模块
    tts = TextToSpeech()
    llm = DeepSeekChat(api_key=DEEPSEEK_API_KEY)
    
    # 启动提示
    tts.speak("你好，语音助手已启动")
    print("=" * 50)
    print("说'退出'、'再见'或'结束'来退出程序")
    
    while True:
        # 1. 语音转文字
        user_input = listen_to_text()
        
        if not user_input:
            continue
        
        # 检查退出命令
        if user_input in ["退出", "再见", "结束"]:
            tts.speak("再见")
            break
        
        # 2. 调用LLM获取回复
        reply = llm.ask(user_input)
        
        # 3. 文字转语音输出
        if reply:
            print("正在用语音来回复")
            tts.speak(reply)

if __name__ == "__main__":
    main()
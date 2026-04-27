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
    tts.speak("你好，我是你的面试官，我们将进行Java后端开发工程师的模拟面试。请准备好，我们马上开始。")
    print("=" * 50)
    print("说'退出'、'再见'或'结束'来退出程序")
    

    count = 0
    while True:
        # 1. 语音转文字
        user_input = listen_to_text()
        # if count == 0:
        #     user_input = "你好，面试官。我准备好了。请问第一个问题是什么？"  # 测试用固定输入
        # elif count == 1:
        #     user_input = "我是王云杰，我印象最深的是图书馆管理系统"  # 测试用固定输入
        # else:
        #     user_input = listen_to_text()
        # count += 1
        
        
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
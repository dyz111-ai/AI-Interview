from openai import OpenAI

class DeepSeekChat:
    def __init__(self, api_key, base_url="https://api.deepseek.com/v1"):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    def ask(self, prompt, temperature=0.7, max_tokens=1000):
        """发送问题给LLM，返回回复"""
        try:
            print(f"正在获取LLM回复")

            system_prompt = "你是一个语音助手，你的回复将直接通过语音朗读给用户。请使用纯文本格式回复，不要使用任何Markdown语法（如*、#、-、`等符号），不要使用代码块、列表标记。请用自然流畅的语言回答。"
        
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            reply = response.choices[0].message.content
            print(f"获取LLM回复成功")
            return reply
        except Exception as e:
            print(f"❌ API错误：{e}")
            return ""
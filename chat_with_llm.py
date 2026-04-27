from openai import OpenAI

class DeepSeekChat:
    def __init__(self, api_key, base_url="https://api.deepseek.com/v1", max_history=10):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.max_history = max_history  # 最大历史记录数
        self.history = []  # 对话历史记录
    
    def _get_system_prompt(self):
        """获取系统提示词"""
        prompt = "你是一名资深的后端开发工程师面试官，负责对计算机相关专业的学生进行模拟技术面试你的任务是：" \
        "1. 根据岗位“Java后端开发工程师”的要求，从题库中选择或动态生成面试题，包含技术知识、项目经历深挖、场景题、行为题。" \
        "2. 采用多轮对话形式，先提问，等学生回答后，根据回答中的关键词或漏洞进行合理追问。" \
        "3. 控制面试节奏，总时长约15–20分钟，包括3–5个核心问题及可能的追问。" \
        "4. 在每次学生回答后，不直接给出答案，而是简短过渡（如“明白了，我们再看下一个问题”或“你提到了XX，能具体说一下吗？”）。" \
        "5. 面试结束时，输出一个简要的结构化总结，供后续评估模块使用。" \
        "当前面试岗位：Java后端开发工程师" \
        "目标学生水平：本科或硕士，有基础项目经验" \
        "请开始第一轮提问，首先要询问自我介绍，后续再追问。请使用纯文本格式回复，不要使用任何Markdown语法（如*、#、-、`等符号），不要使用代码块、列表标记。请用自然流畅的语言回答。"
        ""
        return prompt 
    
    def _add_to_history(self, role, content):
        """添加消息到历史记录"""
        self.history.append({"role": role, "content": content})
        # 保持历史记录在限制范围内
        if len(self.history) > self.max_history * 2:  # *2 因为每轮对话有用户和助手两条消息
            self.history = self.history[-self.max_history * 2:]
    
    def clear_history(self):
        """清空对话历史"""
        self.history = []
    
    def ask(self, prompt, temperature=0.7, max_tokens=1000):
        """发送问题给LLM，返回完整回复（带历史记录）"""
        try:
            print(f"正在获取LLM回复")

            system_prompt = self._get_system_prompt()
            
            # 构建消息列表：系统提示 + 历史记录 + 当前问题
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(self.history)
            messages.append({"role": "user", "content": prompt})
        
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            reply = response.choices[0].message.content
            
            # 添加到历史记录
            self._add_to_history("user", prompt)
            self._add_to_history("assistant", reply)
            
            print(f"获取LLM回复成功")
            return reply
        except Exception as e:
            print(f"❌ API错误：{e}")
            return ""
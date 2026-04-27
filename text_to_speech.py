import edge_tts
import asyncio
import pygame
import tempfile
import os
import time

class TextToSpeech:
    def __init__(self, voice="zh-CN-YunyangNeural"):
        """
        初始化TTS
        :param voice: 语音类型，中文可选: zh-CN-XiaoxiaoNeural(女), zh-CN-YunxiNeural(男)
                      英文可选: en-US-JennyNeural(女), en-US-GuyNeural(男)
        """
        self.voice = voice
        # 初始化pygame的混音器
        pygame.mixer.init()
    
    def speak(self, text):
        """同步版本的speak方法"""
        if not text or not text.strip():
            return
            
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            temp_filename = tmp_file.name
        
        try:
            # 异步生成音频文件
            asyncio.run(self._generate_audio(text, temp_filename))
            
            # 播放音频
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            
            # 等待播放完成
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            # 关键修复：停止音乐并卸载文件
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()  # 卸载文件，释放句柄
            time.sleep(0.1)  # 给系统一点时间释放文件
                
        except Exception as e:
            print(f"语音播放出错: {e}")
        finally:
            # 清理临时文件
            try:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
            except PermissionError:
                # 如果还是无法删除，稍等重试
                time.sleep(0.2)
                try:
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                except:
                    pass
    
    async def _generate_audio(self, text, filename):
        """生成音频文件的异步方法"""
        tts = edge_tts.Communicate(text, self.voice)
        await tts.save(filename)

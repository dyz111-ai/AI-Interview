// 语音播放模块（使用Web Speech API的TTS）
class AudioPlayer {
    constructor() {
        this.synthesis = window.speechSynthesis;
        this.isPlaying = false;
        this.onStart = null;
        this.onEnd = null;
        this.onError = null;
        this.voicesLoaded = false;
        
        this.init();
    }
    
    init() {
        if (typeof this.synthesis.onvoiceschanged !== 'undefined') {
            this.synthesis.onvoiceschanged = () => {
                this.voicesLoaded = true;
            };
        }
        
        const voices = this.synthesis.getVoices();
        if (voices.length > 0) {
            this.voicesLoaded = true;
        }
    }
    
    getChineseVoice() {
        const voices = this.synthesis.getVoices();
        return voices.find(voice => 
            voice.lang.includes('zh-CN') || voice.lang.includes('zh')
        );
    }

    speak(text, onEndCallback = null) {
        if (!text || text.trim() === '') {
            console.warn('文本为空，不进行语音播放');
            return;
        }
        
        // 停止当前播放
        if (this.isPlaying) {
            this.synthesis.cancel();
        }
        
        // 创建语音对象
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'zh-CN';  // 中文
        utterance.rate = 1.5;      // 语速稍慢
        utterance.pitch = 1.0;     // 音调正常
        utterance.volume = 1.0;    // 音量最大
        
        // 选择中文语音（如果有）
        const chineseVoice = this.getChineseVoice();
        if (chineseVoice) {
            utterance.voice = chineseVoice;
        }
        
        // 绑定事件
        utterance.onstart = () => {
            this.isPlaying = true;
            if (this.onStart) this.onStart();
        };
        
        utterance.onend = () => {
            this.isPlaying = false;
            if (this.onEnd) this.onEnd();
            if (onEndCallback) onEndCallback();
        };
        
        utterance.onerror = (event) => {
            console.error('语音播放错误:', event);
            this.isPlaying = false;
            if (this.onError) this.onError(event);
        };
        
        // 播放
        this.synthesis.speak(utterance);
    }
    
    stop() {
        if (this.isPlaying) {
            this.synthesis.cancel();
            this.isPlaying = false;
        }
    }
}

// 创建全局实例
const audioPlayer = new AudioPlayer();
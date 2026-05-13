// API客户端封装
class APIClient {
    constructor(baseURL = 'http://127.0.0.1:8000') {
        this.baseURL = baseURL;
        this.sessionId = null;
    }

    async request(endpoint, method, data) {
        const url = `${this.baseURL}${endpoint}`;
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        console.log(`[API] 请求: ${method} ${url}`);
        console.log(`[API] 数据:`, data);

        try {
            const response = await fetch(url, options);
            console.log(`[API] 响应状态: ${response.status}`);

            if (!response.ok) {
                const errorText = await response.text();
                const errorMsg = `HTTP ${response.status}: ${response.statusText} - ${errorText}`;
                console.error('[API] 请求失败:', errorMsg);
                throw new Error(errorMsg);
            }

            const result = await response.json();
            console.log(`[API] 响应数据:`, result);
            return result;

        } catch (error) {
            console.error('[API] 请求异常:', error);

            if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
                console.error('[API] 网络错误 - 可能后端服务未启动或端口不可达');
                throw new Error('网络连接失败，请检查后端服务是否启动');
            }

            throw error;
        }
    }

    async parseResume(file) {
        const url = `${this.baseURL}/api/interview/parse-resume`;
        const form = new FormData();
        form.append('file', file);
        const response = await fetch(url, { method: 'POST', body: form });
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || `HTTP ${response.status}`);
        }
        return response.json();
    }

    async startInterview(resumeText) {
        // 空串会触发后端 min_length=1，返回 422
        const text = typeof resumeText === 'string' ? resumeText.trim() : String(resumeText ?? '').trim();
        if (!text) {
            throw new Error('简历内容为空。请重新上传能复制出文字的 PDF 或 docx（图片型 PDF 无法识别）。');
        }
        const data = { resume_text: text };
        if (this.sessionId != null && this.sessionId !== '') {
            data.session_id = String(this.sessionId);
        }
        const result = await this.request('/api/interview/start', 'POST', data);
        this.sessionId = result.session_id;
        return result;
    }

    async sendMessage(message) {
        if (!this.sessionId) {
            throw new Error('请先开始面试');
        }
        const result = await this.request('/api/interview/chat', 'POST', {
            session_id: this.sessionId,
            user_message: message
        });
        return result.reply;
    }

    async endInterview() {
        if (!this.sessionId) {
            throw new Error('没有进行中的面试');
        }
        const result = await this.request('/api/interview/end', 'POST', {
            session_id: this.sessionId
        });
        this.sessionId = null;
        return result.summary;
    }

    async getInterviewHistory() {
        const result = await this.request('/api/interview/history', 'GET');
        return result.interviews;
    }

    async getInterviewDetail(sessionId) {
        const result = await this.request(`/api/interview/history/${sessionId}`, 'GET');
        return result;
    }

    async deleteInterview(sessionId) {
        const result = await this.request(`/api/interview/history/${sessionId}`, 'DELETE');
        return result;
    }
}

// 创建全局实例
const apiClient = new APIClient();

// 主逻辑：欢迎页 → 设置页 → 面试对话页
class InterviewApp {
    constructor() {
        this.isInterviewActive = false;
        this.currentSessionId = null;
        this.isRecording = false;
        this.currentDetailSessionId = null;
        this.currentView = 'welcome';

        this.viewWelcome = document.getElementById('viewWelcome');
        this.viewSetup = document.getElementById('viewSetup');
        this.viewPredict = document.getElementById('viewPredict');
        this.viewInterview = document.getElementById('viewInterview');
        this.viewGrowth = document.getElementById('viewGrowth');
        this.viewBank = document.getElementById('viewBank');

        this.bankSearchInput = document.getElementById('bankSearchInput');
        this.bankSourceFilter = document.getElementById('bankSourceFilter');
        this.bankCategoryFilter = document.getElementById('bankCategoryFilter');
        this.bankStatusEl = document.getElementById('bankStatus');
        this.bankStatsEl = document.getElementById('bankStats');
        this.bankListEl = document.getElementById('bankList');
        this.bankItems = [];
        this.bankLoaded = false;

        this.predictResumeFileInput = document.getElementById('predictResumeFileInput');
        this.predictResumeHint = document.getElementById('predictResumeHint');
        this.predictResumeText = '';
        this.predictResumeReady = false;
        this.predictGenerateBtn = document.getElementById('predictGenerateBtn');
        this.predictCopyBtn = document.getElementById('predictCopyBtn');
        this.predictResultEl = document.getElementById('predictResult');
        this.predictStatusEl = document.getElementById('predictStatus');
        this.lastPredictMarkdown = '';

        this.chatArea = document.getElementById('chatArea');
        this.resumeFileInput = document.getElementById('resumeFileInput');
        this.resumeHint = document.getElementById('resumeHint');
        this.resumePreviewWrap = document.getElementById('resumePreviewWrap');
        this.resumePreview = document.getElementById('resumePreview');
        this.resumeParsedText = '';
        this.resumeReady = false;

        this.setupStartBtn = document.getElementById('setupStartBtn');

        this.recordBtn = document.getElementById('recordBtn');
        this.endBtn = document.getElementById('endBtn');
        this.historyBtn = document.getElementById('historyBtn');
        this.statusDiv = document.getElementById('status');
        this.manualInput = document.getElementById('manualInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.historyModal = document.getElementById('historyModal');
        this.historyDetailModal = document.getElementById('historyDetailModal');
        this.historyList = document.getElementById('historyList');
        this.historyDetail = document.getElementById('historyDetail');
        this.detailTitle = document.getElementById('detailTitle');
        this.deleteHistoryBtn = document.getElementById('deleteHistoryBtn');

        this.lastSummaryText = '';
        this.viewReportBtn = document.getElementById('viewReportBtn');
        this.summaryReportModal = document.getElementById('summaryReportModal');
        this.summaryReportBody = document.getElementById('summaryReportBody');
        this.summaryDownloadPdfBtn = document.getElementById('summaryDownloadPdfBtn');
        this.summaryModalCloseBtn = document.getElementById('summaryModalCloseBtn');
        this.closeSummarySpan = document.querySelector('.close-summary');

        this.init();
    }

    init() {
        document.getElementById('welcomeMockBtn')?.addEventListener('click', () => this.showView('setup'));
        document.getElementById('welcomePredictBtn')?.addEventListener('click', () => this.showView('predict'));
        document.getElementById('welcomeBankBtn')?.addEventListener('click', () => this.showBank());
        document.getElementById('welcomeHistoryBtn')?.addEventListener('click', () => this.showHistory());
        document.getElementById('welcomeGrowthBtn')?.addEventListener('click', () => this.showGrowth());
        document.getElementById('growthBackBtn')?.addEventListener('click', () => this.showView('welcome'));
        document.getElementById('bankBackBtn')?.addEventListener('click', () => this.showView('welcome'));
        document.getElementById('predictBackBtn')?.addEventListener('click', () => this.showView('welcome'));
        if (this.bankSearchInput) {
            this.bankSearchInput.addEventListener('input', () => this.renderBankList());
        }
        if (this.bankSourceFilter) {
            this.bankSourceFilter.addEventListener('change', () => this.renderBankList());
        }
        if (this.bankCategoryFilter) {
            this.bankCategoryFilter.addEventListener('change', () => this.renderBankList());
        }
        if (this.predictResumeFileInput) {
            this.predictResumeFileInput.addEventListener('change', (e) => this.onPredictResumeFileSelected(e));
        }
        if (this.predictGenerateBtn) {
            this.predictGenerateBtn.addEventListener('click', () => this.generatePredict());
        }
        if (this.predictCopyBtn) {
            this.predictCopyBtn.addEventListener('click', () => this.copyPredictResult());
        }
        document.getElementById('setupBackBtn')?.addEventListener('click', () => this.onSetupBack());
        document.getElementById('interviewSettingsBtn')?.addEventListener('click', () => this.onInterviewSettings());

        if (this.resumeFileInput) {
            this.resumeFileInput.addEventListener('change', (e) => this.onResumeFileSelected(e));
        }
        if (this.setupStartBtn) {
            this.setupStartBtn.addEventListener('click', () => this.startInterview());
        }

        const setupInputs = this.viewSetup?.querySelectorAll(
            'input, select, .chip input'
        );
        setupInputs?.forEach((el) => {
            el.addEventListener('change', () => this.updateSetupSummary());
            if (el.type === 'number') {
                el.addEventListener('input', () => this.updateSetupSummary());
            }
        });

        this.recordBtn.addEventListener('click', () => this.toggleRecording());
        this.endBtn.addEventListener('click', () => this.endInterview());
        this.historyBtn.addEventListener('click', () => this.showHistory());
        this.sendBtn.addEventListener('click', () => this.sendManualMessage());
        this.manualInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendManualMessage();
        });

        document.querySelector('.close')?.addEventListener('click', () => {
            this.historyModal.style.display = 'none';
        });
        document.querySelector('.close-detail')?.addEventListener('click', () => {
            this.historyDetailModal.style.display = 'none';
        });
        document.getElementById('closeDetailBtn')?.addEventListener('click', () => {
            this.historyDetailModal.style.display = 'none';
        });
        this.deleteHistoryBtn.addEventListener('click', () => this.deleteCurrentHistory());

        if (this.viewReportBtn) {
            this.viewReportBtn.addEventListener('click', () => this.openSummaryReportModal());
        }
        if (this.summaryDownloadPdfBtn) {
            this.summaryDownloadPdfBtn.addEventListener('click', () => this.downloadSummaryPdf());
        }
        if (this.summaryModalCloseBtn) {
            this.summaryModalCloseBtn.addEventListener('click', () => this.closeSummaryReportModal());
        }
        if (this.closeSummarySpan) {
            this.closeSummarySpan.addEventListener('click', () => this.closeSummaryReportModal());
        }

        window.addEventListener('click', (e) => {
            if (e.target === this.historyModal) {
                this.historyModal.style.display = 'none';
            }
            if (e.target === this.historyDetailModal) {
                this.historyDetailModal.style.display = 'none';
            }
            if (this.summaryReportModal && e.target === this.summaryReportModal) {
                this.closeSummaryReportModal();
            }
        });

        audioRecorder.onResult = (text) => this.handleUserInput(text);
        audioRecorder.onError = (error) => {
            this.updateStatus(`语音识别错误: ${error}`, 'error');
            this.isRecording = false;
            this.recordBtn.textContent = '🎙️ 按住说话';
            this.recordBtn.classList.remove('recording');
        };
        audioRecorder.onEnd = () => {
            this.isRecording = false;
            this.recordBtn.textContent = '🎙️ 按住说话';
            this.recordBtn.classList.remove('recording');
        };

        audioPlayer.onStart = () => {
            this.updateStatus('面试官正在说话...', 'info');
        };
        audioPlayer.onEnd = () => {
            this.updateStatus('等待您的回答...', 'info');
            if (this.isInterviewActive) {
                this.enableRecording(true);
            }
        };

        this.loadSettingsFromStorage();
        this.updateSetupSummary();
        this.showView('welcome');
    }

    showView(name) {
        this.currentView = name;
        const views = [
            ['welcome', this.viewWelcome],
            ['setup', this.viewSetup],
            ['predict', this.viewPredict],
            ['bank', this.viewBank],
            ['interview', this.viewInterview],
            ['growth', this.viewGrowth],
        ];
        views.forEach(([key, el]) => {
            if (!el) return;
            const active = key === name;
            el.classList.toggle('app-view--active', active);
            el.hidden = !active;
        });
    }

    onSetupBack() {
        if (this.isInterviewActive) {
            if (!confirm('面试进行中，返回将不会自动保存进度。确定返回设置页？')) {
                return;
            }
        }
        this.showView('welcome');
    }

    onInterviewSettings() {
        if (this.isInterviewActive) {
            this.updateStatus('面试进行中无法修改设置，请先结束面试', 'error');
            return;
        }
        this.showView('setup');
    }

    setPredictStatus(message, type = 'info') {
        if (!this.predictStatusEl) return;
        this.predictStatusEl.textContent = message || '';
        this.predictStatusEl.dataset.status = type === 'error' ? 'error' : type === 'loading' ? 'loading' : 'info';
    }

    updatePredictReady() {
        if (this.predictGenerateBtn) {
            this.predictGenerateBtn.disabled = !this.predictResumeReady;
        }
    }

    collectPredictOptions() {
        const count = parseInt(document.getElementById('predictCountSelect')?.value || '12', 10);
        const focusAreas = Array.from(
            document.querySelectorAll('input[name="predictFocusArea"]:checked')
        ).map((el) => el.value);
        return { question_count: count, focus_areas: focusAreas };
    }

    async onPredictResumeFileSelected(event) {
        const file = event.target?.files?.[0];
        if (!file) return;

        this.predictResumeReady = false;
        this.predictResumeText = '';
        this.updatePredictReady();
        if (this.predictResumeHint) {
            this.predictResumeHint.textContent = '解析中…';
        }
        this.setPredictStatus('正在解析简历…', 'loading');
        if (this.predictResultEl) {
            this.predictResultEl.hidden = true;
            this.predictResultEl.innerHTML = '';
        }
        if (this.predictCopyBtn) {
            this.predictCopyBtn.classList.add('btn-hidden');
        }

        try {
            const result = await apiClient.parseResume(file);
            const raw = result.text != null ? String(result.text) : '';
            this.predictResumeText = raw.trim();

            if (!this.predictResumeText.length) {
                if (this.predictResumeHint) {
                    this.predictResumeHint.textContent = '未提取到文字';
                }
                this.setPredictStatus('未识别到文字，请换用可复制文本的 PDF 或 docx', 'error');
                return;
            }

            this.predictResumeReady = true;
            const name = result.filename || file.name;
            if (this.predictResumeHint) {
                this.predictResumeHint.textContent = `已解析：${name}，约 ${this.predictResumeText.length} 字`;
            }
            this.setPredictStatus('简历已就绪，可点击「开始押题」');
            this.updatePredictReady();
        } catch (error) {
            console.error('押题页简历解析失败:', error);
            if (this.predictResumeHint) {
                this.predictResumeHint.textContent = '解析失败';
            }
            this.setPredictStatus('简历解析失败：' + (error.message || ''), 'error');
        }
    }

    renderPredictResult(data) {
        if (!this.predictResultEl) return;

        const sections = data.sections || [];
        if (!sections.length) {
            this.predictResultEl.innerHTML = '<p class="predict-empty">未生成题目，请重试</p>';
            this.predictResultEl.hidden = false;
            return;
        }

        let html = '';
        let qIndex = 0;
        sections.forEach((sec) => {
            html += `<div class="predict-section"><h3 class="predict-section-title">${this.escapeHtml(sec.category || '其他')}</h3>`;
            (sec.items || []).forEach((item) => {
                qIndex += 1;
                const points = (item.answer_points || [])
                    .map((p) => `<li>${this.escapeHtml(p)}</li>`)
                    .join('');
                const sample = (item.sample_answer || '').trim();
                html += `<article class="predict-item">
                    <div class="predict-q">${qIndex}. ${this.escapeHtml(item.question || '')}</div>
                    ${item.why_ask ? `<div class="predict-why">可能原因：${this.escapeHtml(item.why_ask)}</div>` : ''}
                    ${points ? `<ul class="predict-points">${points}</ul>` : ''}
                    ${sample ? `<details class="predict-sample"><summary>参考回答（展开）</summary><p>${this.escapeHtml(sample)}</p></details>` : ''}
                </article>`;
            });
            html += '</div>';
        });

        this.predictResultEl.innerHTML = html;
        this.predictResultEl.hidden = false;
        this.lastPredictMarkdown = this.buildPredictMarkdown(sections);
    }

    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str == null ? '' : String(str);
        return div.innerHTML;
    }

    setBankStatus(message, type = 'info') {
        if (!this.bankStatusEl) return;
        this.bankStatusEl.textContent = message || '';
        this.bankStatusEl.dataset.status = type === 'error' ? 'error' : type === 'loading' ? 'loading' : 'info';
    }

    async showBank() {
        this.showView('bank');
        if (this.bankLoaded && this.bankItems.length) {
            this.renderBankList();
            return;
        }
        this.setBankStatus('正在加载题库…', 'loading');
        if (this.bankListEl) this.bankListEl.innerHTML = '';
        if (this.bankStatsEl) this.bankStatsEl.textContent = '';
        try {
            const data = await apiClient.getQuestionBank('java_backend');
            this.bankItems = data.items || [];
            this.bankLoaded = true;
            this.populateBankFilters(data.sources || [], data.categories || []);
            if (!this.bankItems.length) {
                this.setBankStatus(data.message || '题库为空，请检查 data/java_backend/interview_questions 目录', 'error');
                return;
            }
            this.setBankStatus('');
            this.renderBankList();
        } catch (e) {
            console.error('题库加载失败:', e);
            this.setBankStatus(e.message || '题库加载失败', 'error');
        }
    }

    populateBankFilters(sources, categories) {
        if (this.bankSourceFilter) {
            const cur = this.bankSourceFilter.value;
            this.bankSourceFilter.innerHTML = '<option value="">全部来源</option>' +
                sources.map((s) => `<option value="${this.escapeHtml(s)}">${this.escapeHtml(s)}</option>`).join('');
            this.bankSourceFilter.value = sources.includes(cur) ? cur : '';
        }
        if (this.bankCategoryFilter) {
            const cur = this.bankCategoryFilter.value;
            this.bankCategoryFilter.innerHTML = '<option value="">全部分类</option>' +
                categories.map((c) => `<option value="${this.escapeHtml(c)}">${this.escapeHtml(c)}</option>`).join('');
            this.bankCategoryFilter.value = categories.includes(cur) ? cur : '';
        }
    }

    getFilteredBankItems() {
        const q = (this.bankSearchInput?.value || '').trim().toLowerCase();
        const source = this.bankSourceFilter?.value || '';
        const category = this.bankCategoryFilter?.value || '';
        return this.bankItems.filter((item) => {
            if (source && item.source !== source) return false;
            if (category && item.category !== category) return false;
            if (!q) return true;
            const hay = [
                item.question,
                item.category,
                item.topic,
                item.source,
                item.answer,
            ].join(' ').toLowerCase();
            return hay.includes(q);
        });
    }

    renderBankList() {
        if (!this.bankListEl) return;
        const filtered = this.getFilteredBankItems();
        if (this.bankStatsEl) {
            this.bankStatsEl.textContent = `共 ${this.bankItems.length} 题 · 当前显示 ${filtered.length} 题`;
        }
        if (!filtered.length) {
            this.bankListEl.innerHTML = '<p class="bank-empty">没有匹配的题目，试试调整筛选条件</p>';
            return;
        }
        this.bankListEl.innerHTML = filtered.map((item, idx) => {
            const meta = [
                item.category,
                item.difficulty ? `难度：${item.difficulty}` : '',
                item.source,
            ].filter(Boolean).map((t) => `<span class="bank-tag">${this.escapeHtml(t)}</span>`).join('');
            const answer = (item.answer || '').trim();
            const followUps = (item.follow_ups || '').trim();
            return `<article class="bank-item" data-id="${this.escapeHtml(item.id)}">
                <div class="bank-item-head">
                    <span class="bank-item-num">${idx + 1}</span>
                    <h3 class="bank-item-q">${this.escapeHtml(item.question)}</h3>
                </div>
                <div class="bank-item-meta">${meta}</div>
                ${answer ? `<details class="bank-item-answer"><summary>参考答案</summary><pre class="bank-answer-text">${this.escapeHtml(answer)}</pre></details>` : ''}
                ${followUps ? `<details class="bank-item-follow"><summary>追问点</summary><pre class="bank-answer-text">${this.escapeHtml(followUps)}</pre></details>` : ''}
            </article>`;
        }).join('');
    }

    buildPredictMarkdown(sections) {
        let md = '# 简历押题结果\n\n';
        let qIndex = 0;
        sections.forEach((sec) => {
            md += `## ${sec.category || '其他'}\n\n`;
            (sec.items || []).forEach((item) => {
                qIndex += 1;
                md += `### ${qIndex}. ${item.question || ''}\n\n`;
                if (item.why_ask) {
                    md += `**可能原因：** ${item.why_ask}\n\n`;
                }
                if (item.answer_points?.length) {
                    md += '**回答要点：**\n';
                    item.answer_points.forEach((p) => {
                        md += `- ${p}\n`;
                    });
                    md += '\n';
                }
                if (item.sample_answer) {
                    md += `**参考回答：** ${item.sample_answer}\n\n`;
                }
            });
        });
        return md;
    }

    async generatePredict() {
        if (!this.predictResumeReady || !this.predictResumeText) {
            this.setPredictStatus('请先上传并成功解析简历', 'error');
            return;
        }

        const opts = this.collectPredictOptions();
        if (this.predictGenerateBtn) {
            this.predictGenerateBtn.disabled = true;
            this.predictGenerateBtn.textContent = '生成中…';
        }
        if (this.predictCopyBtn) {
            this.predictCopyBtn.classList.add('btn-hidden');
        }
        this.setPredictStatus('正在根据简历分析可能问题，约需 30～90 秒…', 'loading');

        try {
            const data = await apiClient.generateResumePredict(
                this.predictResumeText,
                opts.question_count,
                opts.focus_areas
            );
            this.renderPredictResult(data);
            const total = (data.sections || []).reduce(
                (n, s) => n + (s.items?.length || 0),
                0
            );
            this.setPredictStatus(`押题完成，共 ${total} 道题`);
            if (this.predictCopyBtn) {
                this.predictCopyBtn.classList.remove('btn-hidden');
            }
            this.predictResultEl?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } catch (error) {
            console.error('押题失败:', error);
            this.setPredictStatus('押题失败：' + (error.message || '请稍后重试'), 'error');
        } finally {
            if (this.predictGenerateBtn) {
                this.predictGenerateBtn.textContent = '开始押题';
                this.updatePredictReady();
            }
        }
    }

    async copyPredictResult() {
        const text = this.lastPredictMarkdown || '';
        if (!text.trim()) {
            this.setPredictStatus('没有可复制的内容', 'error');
            return;
        }
        try {
            await navigator.clipboard.writeText(text);
            this.setPredictStatus('已复制到剪贴板');
        } catch (_) {
            this.setPredictStatus('复制失败，请手动选择内容复制', 'error');
        }
    }

    collectSettings() {
        const styleEl = document.querySelector('input[name="interviewStyle"]:checked');
        const focusAreas = Array.from(
            document.querySelectorAll('input[name="focusArea"]:checked')
        ).map((el) => el.value);

        return {
            job_role: document.getElementById('jobRoleSelect')?.value || 'java_backend',
            interview_style: styleEl?.value || 'standard',
            depth: document.getElementById('depthSelect')?.value || 'standard',
            duration_minutes: parseInt(document.getElementById('durationSelect')?.value || '20', 10),
            focus_areas: focusAreas,
        };
    }

    saveSettingsToStorage() {
        try {
            localStorage.setItem('interview_setup', JSON.stringify(this.collectSettings()));
        } catch (_) {
            /* ignore */
        }
    }

    loadSettingsFromStorage() {
        try {
            const raw = localStorage.getItem('interview_setup');
            if (!raw) return;
            const s = JSON.parse(raw);
            if (s.interview_style) {
                const el = document.querySelector(
                    `input[name="interviewStyle"][value="${s.interview_style}"]`
                );
                if (el) el.checked = true;
            }
            if (s.depth && document.getElementById('depthSelect')) {
                document.getElementById('depthSelect').value = s.depth;
            }
            if (s.duration_minutes && document.getElementById('durationSelect')) {
                document.getElementById('durationSelect').value = String(s.duration_minutes);
            }
            if (Array.isArray(s.focus_areas)) {
                document.querySelectorAll('input[name="focusArea"]').forEach((cb) => {
                    cb.checked = s.focus_areas.includes(cb.value);
                });
            }
        } catch (_) {
            /* ignore */
        }
    }

    updateSetupSummary() {
        this.saveSettingsToStorage();
        if (this.setupStartBtn) {
            this.setupStartBtn.disabled = !this.resumeReady;
        }
    }

    async onResumeFileSelected(event) {
        const file = event.target?.files?.[0];
        if (!file) {
            return;
        }

        this.resumeReady = false;
        this.resumeParsedText = '';
        if (this.setupStartBtn) {
            this.setupStartBtn.disabled = true;
        }
        if (this.resumeHint) {
            this.resumeHint.textContent = '解析中…';
        }
        if (this.resumePreviewWrap) {
            this.resumePreviewWrap.hidden = true;
        }

        try {
            const result = await apiClient.parseResume(file);
            const raw = result.text != null ? String(result.text) : '';
            this.resumeParsedText = raw.trim();

            if (!this.resumeParsedText.length) {
                this.resumeReady = false;
                if (this.resumeHint) {
                    this.resumeHint.textContent = '未提取到文字（常见于扫描版 PDF）';
                }
                this.updateSetupSummary();
                return;
            }

            this.resumeReady = true;
            const name = result.filename || file.name;
            const extra = result.truncated ? '（服务端已截断过长文本）' : '';
            if (this.resumeHint) {
                this.resumeHint.textContent = `已解析：${name}，约 ${this.resumeParsedText.length} 字${extra}`;
            }
            if (this.resumePreview && this.resumePreviewWrap) {
                this.resumePreview.textContent = this.resumeParsedText.slice(0, 300);
                this.resumePreviewWrap.hidden = false;
            }
            this.updateSetupSummary();
        } catch (error) {
            console.error('简历解析失败:', error);
            if (this.resumeHint) {
                this.resumeHint.textContent = '解析失败，请使用 PDF 或 docx';
            }
            this.updateSetupSummary();
        }
    }

    updateStatus(message, type = 'info') {
        if (!this.statusDiv) return;
        this.statusDiv.textContent = message;
        this.statusDiv.dataset.status = type === 'error' ? 'error' : 'info';
    }

    hideReportButton() {
        this.lastSummaryText = '';
        if (this.summaryReportBody) {
            this.summaryReportBody.innerHTML = '';
        }
        if (this.viewReportBtn) {
            this.viewReportBtn.classList.add('btn-hidden');
            this.viewReportBtn.disabled = true;
        }
        this.closeSummaryReportModal();
    }

    showReportButton(summary) {
        this.lastSummaryText = summary != null ? String(summary) : '';
        if (this.summaryReportBody) {
            if (typeof renderInterviewSummaryHtml === 'function') {
                this.summaryReportBody.innerHTML = renderInterviewSummaryHtml(this.lastSummaryText);
            } else {
                this.summaryReportBody.textContent = this.lastSummaryText;
            }
        }
        if (this.viewReportBtn) {
            this.viewReportBtn.classList.remove('btn-hidden');
            this.viewReportBtn.disabled = false;
        }
    }

    openSummaryReportModal() {
        if (!this.summaryReportModal || !this.summaryReportBody) {
            return;
        }
        const raw = this.lastSummaryText || '';
        if (typeof renderInterviewSummaryHtml === 'function') {
            this.summaryReportBody.innerHTML = raw
                ? renderInterviewSummaryHtml(raw)
                : '<p class="report-empty">（暂无报告内容）</p>';
        } else {
            this.summaryReportBody.textContent = raw || '（暂无报告内容）';
        }
        this.summaryReportModal.style.display = 'block';
    }

    closeSummaryReportModal() {
        if (this.summaryReportModal) {
            this.summaryReportModal.style.display = 'none';
        }
    }

    downloadSummaryPdf() {
        if (typeof html2pdf === 'undefined') {
            this.updateStatus('PDF 组件未加载，请检查网络后刷新页面重试', 'error');
            return;
        }
        const el = this.summaryReportBody;
        if (!el || !String(el.textContent || '').trim()) {
            this.updateStatus('没有可下载的报告内容', 'error');
            return;
        }

        const filename = `面试总结报告_${new Date().toISOString().slice(0, 10)}.pdf`;
        const opt = {
            margin: 12,
            filename,
            image: { type: 'jpeg', quality: 0.92 },
            html2canvas: { scale: 2, useCORS: true, logging: false },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
            pagebreak: { mode: ['avoid-all', 'css', 'legacy'] },
        };

        const prevMax = el.style.maxHeight;
        const prevOv = el.style.overflow;
        el.style.maxHeight = 'none';
        el.style.overflow = 'visible';

        const restore = () => {
            el.style.maxHeight = prevMax;
            el.style.overflow = prevOv;
        };

        const p = html2pdf().set(opt).from(el).save();
        if (p && typeof p.finally === 'function') {
            p.finally(restore);
        } else if (p && typeof p.then === 'function') {
            p.then(restore).catch(restore);
        } else {
            setTimeout(restore, 1500);
        }
    }

    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const roleSpan = document.createElement('span');
        roleSpan.className = 'role';

        if (role === 'user') {
            roleSpan.textContent = '👤 您';
        } else if (role === 'assistant') {
            roleSpan.textContent = '🎯 面试官';
        } else {
            roleSpan.textContent = '🤖 系统';
        }

        const contentP = document.createElement('p');
        contentP.textContent = content;

        messageDiv.appendChild(roleSpan);
        messageDiv.appendChild(contentP);

        this.chatArea.appendChild(messageDiv);
        this.chatArea.scrollTop = this.chatArea.scrollHeight;
    }

    enableRecording(enabled) {
        this.recordBtn.disabled = !enabled;
        this.manualInput.disabled = !enabled;
        this.sendBtn.disabled = !enabled;

        if (enabled) {
            this.updateStatus('可以说话或输入文字回答');
        } else {
            this.updateStatus('面试官正在说话，请稍等...');
        }
    }

    async startInterview() {
        if (!this.resumeReady || !this.resumeParsedText?.trim()) {
            this.updateSetupSummary();
            return;
        }

        const settings = this.collectSettings();

        if (this.setupStartBtn) {
            this.setupStartBtn.disabled = true;
            this.setupStartBtn.textContent = '正在开始…';
        }

        try {
            const result = await apiClient.startInterview(
                this.resumeParsedText.trim(),
                settings,
                settings.job_role
            );
            this.currentSessionId = result.session_id;
            this.isInterviewActive = true;

            this.showView('interview');
            this.endBtn.disabled = false;
            if (this.resumeFileInput) {
                this.resumeFileInput.disabled = true;
            }
            this.enableRecording(true);

            this.hideReportButton();
            this.chatArea.innerHTML = '';
            this.populateInterviewSidebar(settings);
            this.refreshInterviewSidebarHistory();

            this.addMessage('assistant', result.first_question);
            audioPlayer.speak(result.first_question);

            this.updateStatus('面试进行中…');
        } catch (error) {
            console.error('开始面试失败:', error);
            if (this.currentView === 'interview') {
                this.updateStatus('开始面试失败，请检查后端服务是否启动', 'error');
            }
            if (this.setupStartBtn) {
                this.setupStartBtn.disabled = false;
                this.setupStartBtn.textContent = '开始面试';
            }
        } finally {
            if (this.setupStartBtn && this.setupStartBtn.textContent === '正在开始…') {
                this.setupStartBtn.textContent = '开始面试';
                this.setupStartBtn.disabled = !this.resumeReady;
            }
        }
    }

    async toggleRecording() {
        if (!this.isInterviewActive) {
            this.updateStatus('请先开始面试', 'error');
            return;
        }

        if (this.isRecording) {
            audioRecorder.stopListening();
        } else {
            this.updateStatus('请开始说话...', 'info');
            const started = audioRecorder.startListening();
            if (started) {
                this.isRecording = true;
                this.recordBtn.textContent = '🔴 录音中... 点击停止';
                this.recordBtn.classList.add('recording');
            } else {
                this.updateStatus('无法启动麦克风，请检查权限', 'error');
            }
        }
    }

    async handleUserInput(text) {
        if (!this.isInterviewActive) {
            this.updateStatus('面试未开始', 'error');
            return;
        }

        if (!text || text.trim() === '') {
            this.updateStatus('未识别到有效内容，请重新说话', 'error');
            this.enableRecording(true);
            return;
        }

        this.addMessage('user', text);

        this.enableRecording(false);
        this.updateStatus('正在处理您的回答...');

        try {
            const reply = await apiClient.sendMessage(text);

            this.addMessage('assistant', reply);

            audioPlayer.speak(reply);
        } catch (error) {
            console.error('发送消息失败:', error);
            this.updateStatus('发送失败，请重试', 'error');
            this.enableRecording(true);
        }
    }

    async sendManualMessage() {
        const text = this.manualInput.value.trim();
        if (!text) return;

        this.manualInput.value = '';
        await this.handleUserInput(text);
    }

    async endInterview() {
        if (!this.isInterviewActive) {
            return;
        }

        this.updateStatus('正在结束面试，生成总结...');
        this.enableRecording(false);
        this.endBtn.disabled = true;

        try {
            const summary = await apiClient.endInterview();

            this.addMessage(
                'system',
                '面试已结束。完整总结已生成，请点击「查看面试报告」阅读，并可下载 PDF。'
            );
            this.showReportButton(summary);

            this.isInterviewActive = false;
            this.currentSessionId = null;
            this.resumeParsedText = '';
            this.resumeReady = false;
            if (this.resumeFileInput) {
                this.resumeFileInput.value = '';
                this.resumeFileInput.disabled = false;
            }
            if (this.resumeHint) {
                this.resumeHint.textContent = '当前状态：未上传';
            }
            if (this.resumePreviewWrap) {
                this.resumePreviewWrap.hidden = true;
            }
            this.updateSetupSummary();
            this.refreshInterviewSidebarHistory();
            this.updateStatus('面试已结束。可查看报告，或返回设置页重新开始');

        } catch (error) {
            console.error('结束面试失败:', error);
            this.updateStatus('结束面试失败', 'error');
            this.endBtn.disabled = false;
        }
    }

    async showHistory() {
        try {
            const interviews = await apiClient.getInterviewHistory();

            if (interviews.length === 0) {
                this.historyList.innerHTML = '<p class="empty-history">暂无面试记录</p>';
            } else {
                this.historyList.innerHTML = interviews
                    .map(
                        (interview) => `
                    <div class="history-item" data-session-id="${interview.session_id}">
                        <div class="history-info">
                            <span class="history-date">${this.formatDate(interview.created_at)}</span>
                            <span class="history-session-id">会话ID: ${interview.session_id}</span>
                        </div>
                        <div class="history-preview">
                            ${interview.summary ? interview.summary.substring(0, 100) + '...' : '暂无总结'}
                        </div>
                        <button class="btn btn-small btn-primary view-detail-btn">查看详情</button>
                    </div>
                `
                    )
                    .join('');

                this.historyList.querySelectorAll('.view-detail-btn').forEach((btn) => {
                    btn.addEventListener('click', (e) => {
                        const sessionId = e.target.closest('.history-item').dataset.sessionId;
                        this.showHistoryDetail(sessionId);
                    });
                });
            }

            this.historyModal.style.display = 'block';
        } catch (error) {
            console.error('获取历史记录失败:', error);
            this.updateStatus('获取历史记录失败', 'error');
        }
    }

    async showHistoryDetail(sessionId) {
        try {
            const interview = await apiClient.getInterviewDetail(sessionId);
            this.currentDetailSessionId = sessionId;

            this.detailTitle.textContent = `面试详情 - ${this.formatDate(interview.created_at)}`;

            let detailHTML = '<div class="detail-messages">';
            interview.messages.forEach((msg) => {
                const roleClass = msg.role === 'user' ? 'user' : 'assistant';
                const roleText = msg.role === 'user' ? '👤 您' : '🎯 面试官';
                detailHTML += `
                    <div class="message ${roleClass}">
                        <span class="role">${roleText}</span>
                        <p>${msg.content}</p>
                    </div>
                `;
            });
            detailHTML += '</div>';

            if (interview.summary) {
                detailHTML += `
                    <div class="detail-summary">
                        <h3>📊 面试总结</h3>
                        <p>${interview.summary}</p>
                    </div>
                `;
            }

            this.historyDetail.innerHTML = detailHTML;
            this.historyDetailModal.style.display = 'block';
        } catch (error) {
            console.error('获取详情失败:', error);
            this.updateStatus('获取面试详情失败', 'error');
        }
    }

    async deleteCurrentHistory() {
        if (!this.currentDetailSessionId) return;

        if (!confirm('确定要删除这条面试记录吗？')) return;

        try {
            const result = await apiClient.deleteInterview(this.currentDetailSessionId);

            if (result.success) {
                this.historyDetailModal.style.display = 'none';
                this.showHistory();
                this.updateStatus('面试记录已删除', 'info');
            } else {
                this.updateStatus(result.message, 'error');
            }
        } catch (error) {
            console.error('删除失败:', error);
            this.updateStatus('删除失败', 'error');
        }
    }

    populateInterviewSidebar(settings) {
        const el = document.getElementById('isSettings');
        if (!el) return;
        const styleMap = { gentle: '温和鼓励型', standard: '标准专业型', pressure: '压力面型' };
        const depthMap = { basic: '基础', standard: '标准', deep: '深入' };
        const focusNames = {
            java_basic: 'Java基础', java_collection: 'Java集合', concurrent: '并发编程',
            jvm: 'JVM/GC', thread_pool: '线程池', spring: 'Spring Boot', spring_cloud: '微服务',
            database: 'MySQL', sql_optimize: 'SQL优化', redis: 'Redis', mq: '消息队列',
            distributed: '分布式', system_design: '系统设计', performance: '性能优化',
            network: '网络/HTTP', io_nio: 'IO/NIO', design_pattern: '设计模式',
            algorithm: '算法', security: '安全鉴权', docker_k8s: 'Docker/K8s',
            engineering: '工程实践', project: '项目深挖', behavioral: '行为面试',
        };
        const focuses = (settings.focus_areas || []).map(f => focusNames[f] || f).join('、') || '未指定';
        const parts = [
            ['风格', styleMap[settings.interview_style] || settings.interview_style],
            ['深度', depthMap[settings.depth] || settings.depth],
            ['时长', `约 ${settings.duration_minutes} 分钟`],
            ['侧重', focuses],
        ];
        el.innerHTML = parts.map(([label, val]) =>
            `<div class="is-info-item"><span class="is-label">${label}</span><br>${val}</div>`
        ).join('');
    }

    async refreshInterviewSidebarHistory() {
        const list = document.getElementById('isHistoryList');
        if (!list) return;
        try {
            const interviews = await apiClient.getInterviewHistory();
            if (!interviews || interviews.length === 0) {
                list.innerHTML = '<p class="is-empty">暂无记录</p>';
                return;
            }
            list.innerHTML = interviews.slice(0, 10).map(iv => {
                const preview = (iv.summary || '暂无总结').substring(0, 24);
                const date = this.formatDate(iv.created_at);
                return `<div class="is-history-item" data-sid="${iv.session_id}">
                    <div class="is-history-item-date">${date}</div>
                    <div class="is-history-item-preview">${preview}…</div>
                </div>`;
            }).join('');
            list.querySelectorAll('.is-history-item').forEach(el => {
                el.addEventListener('click', () => this.showHistoryDetail(el.dataset.sid));
            });
        } catch (_) { /* ignore */ }
    }

    formatDate(dateStr) {
        const date = new Date(dateStr);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${year}-${month}-${day} ${hours}:${minutes}`;
    }

    // ── Growth view ──
    async showGrowth() {
        this.showView('growth');
        try {
            const interviews = await apiClient.getInterviewHistory();
            const parsed = interviews.map(iv => ({
                ...iv,
                scores: this._parseScores(iv.summary || ''),
                conclusion: this._parseConclusion(iv.summary || ''),
                weakPoints: this._parseWeakPoints(iv.summary || ''),
            })).filter(p => p.scores);

            const emptyEl = document.getElementById('growthEmpty');
            const contentEl = document.getElementById('growthContent');
            if (!parsed.length) {
                if (emptyEl) emptyEl.hidden = false;
                if (contentEl) contentEl.hidden = true;
                return;
            }
            if (emptyEl) emptyEl.hidden = true;
            if (contentEl) contentEl.hidden = false;

            // Overview cards
            const total = parsed.length;
            const latest = parsed[0];
            const latestAvg = latest.scores ? Math.round(Object.values(latest.scores).reduce((a,b)=>a+b,0)/5) : 0;
            const passCount = parsed.filter(p => p.conclusion === '推荐通过').length;
            const passRate = Math.round(passCount / total * 100);
            const prevAvg = parsed.length >= 2 && parsed[1].scores
                ? Math.round(Object.values(parsed[1].scores).reduce((a,b)=>a+b,0)/5) : null;
            const trend = prevAvg !== null ? (latestAvg >= prevAvg ? '↑ 上升' : '↓ 下降') : '—';
            const trendCls = prevAvg !== null ? (latestAvg >= prevAvg ? 'trend-up' : 'trend-down') : '';

            const cards = [
                { icon: '📋', value: `${total} 次`, label: '面试总场次', sub: `含 ${parsed.filter(p=>p.conclusion==='推荐通过').length} 次通过` },
                { icon: '✅', value: `${passRate}%`, label: '推荐通过率', sub: `${passCount}/${total} 场推荐` },
                { icon: '⭐', value: `${latestAvg} 分`, label: '最近均分', sub: this.formatDate(parsed[0].created_at) },
                { icon: prevAvg !== null ? (latestAvg >= prevAvg ? '📈' : '📉') : '📊', value: trend, label: '趋势（较上场）', sub: prevAvg !== null ? `上次均分 ${prevAvg} 分` : '暂无对比', cls: trendCls },
            ];
            document.getElementById('growthCards').innerHTML = cards.map(c =>
                `<div class="growth-card">
                    <span class="growth-card-icon">${c.icon}</span>
                    <div class="growth-card-value ${c.cls||''}">${c.value}</div>
                    <div class="growth-card-label">${c.label}</div>
                    <div class="growth-card-sub">${c.sub}</div>
                </div>`
            ).join('');

            // Table
            const jobMap = { java_backend: 'Java', web_frontend: '前端' };
            document.getElementById('growthTableBody').innerHTML = parsed.map(p => {
                const s = p.scores || {};
                const avg = Math.round(Object.values(s).reduce((a,b)=>a+b,0)/5);
                const weak = (p.weakPoints || []).slice(0, 3).join('、') || '—';
                const concMap = { '推荐通过': 'gt-pass', '基本通过': 'gt-basic', '暂不通过': 'gt-fail', '建议继续准备': 'gt-prepare' };
                return `<tr data-sid="${p.session_id}">
                    <td>${this.formatDate(p.created_at)}</td>
                    <td><b>${avg}</b></td>
                    <td>${s['专业基础能力']||'—'}</td>
                    <td>${s['项目表达能力']||'—'}</td>
                    <td>${s['问题分析能力']||'—'}</td>
                    <td>${s['沟通表达能力']||'—'}</td>
                    <td>${s['岗位匹配程度']||'—'}</td>
                    <td class="gt-conclusion ${concMap[p.conclusion]||''}">${p.conclusion||'—'}</td>
                    <td>${weak}</td>
                </tr>`;
            }).join('');
            document.querySelectorAll('#growthTableBody tr').forEach(tr => {
                tr.addEventListener('click', () => this.showHistoryDetail(tr.dataset.sid));
            });

            // Charts — delay to let DOM layout complete
            await new Promise(r => setTimeout(r, 100));
            this._renderTrendChart(parsed);
            this._renderRadarChart(latest);
            this._renderWeakChart(parsed);
            this._renderConclusionChart(parsed);
        } catch (e) {
            console.error('Growth view error:', e);
        }
    }

    _parseScores(summary) {
        const dims = ['专业基础能力', '项目表达能力', '问题分析能力', '沟通表达能力', '岗位匹配程度'];
        const out = {};
        dims.forEach(d => {
            const re = new RegExp(d.replace(/[+-]/g,'\\$&') + '[^0-9]*?(\\d{1,3})\\s*分');
            const m = summary.match(re);
            if (m) out[d] = parseInt(m[1]);
        });
        return Object.keys(out).length >= 3 ? out : null;
    }

    _parseConclusion(summary) {
        const m = summary.match(/(推荐通过|基本通过|暂不通过|建议继续准备)/);
        return m ? m[1] : '';
    }

    _parseWeakPoints(summary) {
        const keywords = [
            'JVM', 'GC', '并发', '锁', '线程池', '集合', 'IO', 'NIO', 'Netty',
            'Spring', 'Spring Boot', 'MyBatis', '微服务', '分布式', 'CAP',
            'MySQL', 'SQL', '索引', '事务', 'Redis', '缓存', '消息队列', 'MQ',
            '设计模式', '算法', '数据结构', 'HTTP', 'TCP', 'REST',
            '系统设计', '性能优化', '安全', 'Docker', 'K8s', '容器化',
            '项目表达', '沟通', '结构化', '量化',
        ];
        // find the "薄弱知识点" section
        const sec = summary.match(/五[、,]\s*薄弱知识点([\s\S]*?)(?=六[、,]|七[、,]|$)/);
        const text = sec ? sec[1] : '';
        const found = keywords.filter(k => text.includes(k));
        return found.slice(0, 6);
    }

    _renderTrendChart(parsed) {
        const ctx = document.getElementById('chartTrend')?.getContext('2d');
        if (!ctx) return;
        if (this._trendChart) this._trendChart.destroy();
        const dims = ['专业基础能力', '项目表达能力', '问题分析能力', '沟通表达能力', '岗位匹配程度'];
        const colors = ['#22d3ee', '#fbbf24', '#a78bfa', '#34d399', '#fb7185'];
        const labels = parsed.map(p => this.formatDate(p.created_at).slice(5)).reverse();
        const datasets = dims.map((d, i) => ({
            label: d,
            data: parsed.map(p => (p.scores||{})[d]||null).reverse(),
            borderColor: colors[i],
            backgroundColor: 'transparent',
            tension: 0.3,
            pointRadius: 3,
        }));
        this._trendChart = new Chart(ctx, {
            type: 'line',
            data: { labels, datasets },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#94a3b8', font: { size: 11 }, usePointStyle: true, padding: 16 } } },
                scales: {
                    x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,0.06)' } },
                    y: { min: 0, max: 100, ticks: { color: '#64748b', stepSize: 20 }, grid: { color: 'rgba(148,163,184,0.06)' } },
                },
            },
        });
    }

    _renderRadarChart(latest) {
        const ctx = document.getElementById('chartRadar')?.getContext('2d');
        if (!ctx || !latest.scores) return;
        if (this._radarChart) this._radarChart.destroy();
        const dims = ['专业基础能力', '项目表达能力', '问题分析能力', '沟通表达能力', '岗位匹配程度'];
        this._radarChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: dims.map(d => d.replace('能力','').replace('程度','')),
                datasets: [{
                    label: '当前',
                    data: dims.map(d => (latest.scores||{})[d]||0),
                    backgroundColor: 'rgba(34,211,238,0.15)',
                    borderColor: '#22d3ee',
                    borderWidth: 2,
                    pointBackgroundColor: '#22d3ee',
                }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    r: {
                        min: 0, max: 100,
                        ticks: { display: false, stepSize: 20 },
                        pointLabels: { color: '#94a3b8', font: { size: 11 } },
                        grid: { color: 'rgba(148,163,184,0.12)' },
                    },
                },
            },
        });
    }

    _renderWeakChart(parsed) {
        const ctx = document.getElementById('chartWeak')?.getContext('2d');
        if (!ctx) return;
        if (this._weakChart) this._weakChart.destroy();
        const counts = {};
        parsed.forEach(p => (p.weakPoints||[]).forEach(w => { counts[w] = (counts[w]||0)+1; }));
        const entries = Object.entries(counts).sort((a,b) => b[1]-a[1]).slice(0, 10);
        this._weakChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: entries.map(e => e[0]),
                datasets: [{ data: entries.map(e => e[1]), backgroundColor: '#fbbf24', borderRadius: 4 }],
            },
            options: {
                responsive: true, maintainAspectRatio: false, indexAxis: 'y',
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: '#64748b', stepSize: 1 }, grid: { color: 'rgba(148,163,184,0.06)' } },
                    y: { ticks: { color: '#94a3b8', font: { size: 11 } }, grid: { display: false } },
                },
            },
        });
    }

    _renderConclusionChart(parsed) {
        const ctx = document.getElementById('chartConclusion')?.getContext('2d');
        if (!ctx) return;
        if (this._conclusionChart) this._conclusionChart.destroy();
        const counts = {};
        parsed.forEach(p => { const c = p.conclusion||'未知'; counts[c] = (counts[c]||0)+1; });
        const order = ['推荐通过', '基本通过', '暂不通过', '建议继续准备'];
        const colors = ['#34d399', '#fbbf24', '#fb7185', '#64748b'];
        this._conclusionChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: order.filter(k => counts[k]),
                datasets: [{ data: order.filter(k => counts[k]).map(k => counts[k]), backgroundColor: order.filter(k => counts[k]).map((_,i) => colors[i]), borderWidth: 0 }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 11 }, padding: 14, usePointStyle: true } } },
            },
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new InterviewApp();
});

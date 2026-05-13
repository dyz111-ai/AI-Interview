/**
 * 将纯文本面试总结渲染为带图表与排版的 HTML（供弹窗与 PDF 导出）
 */
(function (global) {
    const DIMENSION_ORDER = [
        '专业基础能力',
        '项目表达能力',
        '问题分析能力',
        '沟通表达能力',
        '岗位匹配程度',
    ];

    function escapeHtml(text) {
        if (text == null) return '';
        const d = document.createElement('div');
        d.textContent = String(text);
        return d.innerHTML;
    }

    function nl2brEscaped(text) {
        return escapeHtml(text).replace(/\n/g, '<br>');
    }

    function parseDimensionScores(sectionBody) {
        const out = {};
        for (const name of DIMENSION_ORDER) {
            const esc = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            const re = new RegExp(esc + '[：:]\\s*(\\d+)\\s*分');
            const m = sectionBody.match(re);
            out[name] = m ? Math.min(100, Math.max(0, parseInt(m[1], 10))) : null;
        }
        return out;
    }

    function hasAnyScore(scores) {
        return DIMENSION_ORDER.some((k) => scores[k] != null);
    }

    function stripDimensionLines(body) {
        let s = body || '';
        for (const name of DIMENSION_ORDER) {
            const esc = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            s = s.replace(new RegExp('^\\s*' + esc + '[：:][^\\n]*$', 'gm'), '');
        }
        return s.replace(/\n{3,}/g, '\n\n').trim();
    }

    /**
     * 五维雷达图（SVG）：数据描边填充 + 三层参考网格
     */
    function buildRadarSvg(scores) {
        const n = 5;
        const cx = 150;
        const cy = 150;
        const rMax = 105;
        const angles = DIMENSION_ORDER.map((_, i) => -Math.PI / 2 + (2 * Math.PI * i) / n);

        const polyPoints = angles
            .map((ang, i) => {
                const v = scores[DIMENSION_ORDER[i]];
                const t = v != null ? v / 100 : 0;
                const rr = rMax * t;
                return `${cx + rr * Math.cos(ang)},${cy + rr * Math.sin(ang)}`;
            })
            .join(' ');

        let rings = '';
        for (const ratio of [0.4, 0.7, 1.0]) {
            const pts = angles
                .map((ang) => `${cx + rMax * ratio * Math.cos(ang)},${cy + rMax * ratio * Math.sin(ang)}`)
                .join(' ');
            rings += `<polygon class="radar-ring" points="${pts}" />`;
        }

        let axes = '';
        angles.forEach((ang) => {
            axes += `<line class="radar-axis" x1="${cx}" y1="${cy}" x2="${cx + rMax * Math.cos(ang)}" y2="${cy + rMax * Math.sin(ang)}" />`;
        });

        let labels = '';
        DIMENSION_ORDER.forEach((label, i) => {
            const ang = angles[i];
            const lx = cx + (rMax + 32) * Math.cos(ang);
            const ly = cy + (rMax + 32) * Math.sin(ang);
            labels +=
                `<text class="radar-label" text-anchor="middle" dominant-baseline="central" x="${lx}" y="${ly}">${escapeHtml(label)}</text>`;
        });

        return (
            `<svg class="report-radar-svg" viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">` +
            rings +
            axes +
            `<polygon class="radar-area" points="${polyPoints}" />` +
            `<polygon class="radar-stroke" points="${polyPoints}" fill="none" />` +
            labels +
            `</svg>`
        );
    }

    function buildBarRows(scores) {
        return DIMENSION_ORDER.map((name) => {
            const v = scores[name];
            if (v == null) {
                return (
                    `<div class="score-row score-row--empty">` +
                    `<span class="score-row-label">${escapeHtml(name)}</span>` +
                    `<div class="score-bar-track"><div class="score-bar-fill score-bar-fill--empty" style="width:0%"></div></div>` +
                    `<span class="score-row-num">—</span>` +
                    `</div>`
                );
            }
            return (
                `<div class="score-row">` +
                `<span class="score-row-label">${escapeHtml(name)}</span>` +
                `<div class="score-bar-track"><div class="score-bar-fill" style="width:${v}%"></div></div>` +
                `<span class="score-row-num">${v}<span class="score-row-unit">分</span></span>` +
                `</div>`
            );
        }).join('');
    }

    function splitSections(text) {
        const orderedMarkers = ['一、', '二、', '三、', '四、', '五、', '六、', '七、'];
        const positions = [];
        for (const m of orderedMarkers) {
            const idx = text.indexOf(m);
            if (idx !== -1) positions.push({ idx, marker: m });
        }
        positions.sort((a, b) => a.idx - b.idx);

        const sections = [];
        if (positions.length === 0) {
            return sections;
        }
        if (positions[0].idx > 0) {
            const pre = text.slice(0, positions[0].idx).trim();
            if (pre) {
                sections.push({ title: '说明', body: pre, marker: '' });
            }
        }
        for (let i = 0; i < positions.length; i++) {
            const start = positions[i].idx;
            const titleEnd = text.indexOf('\n', start);
            const title =
                titleEnd === -1 ? text.slice(start).trim() : text.slice(start, titleEnd).trim();
            const bodyStart = titleEnd === -1 ? text.length : titleEnd + 1;
            const end = i + 1 < positions.length ? positions[i + 1].idx : text.length;
            const body = text.slice(bodyStart, end).trim();
            sections.push({
                title,
                body,
                marker: positions[i].marker,
            });
        }
        return sections;
    }

    function sectionAccentClass(marker) {
        const map = {
            '一、': 'report-section--accent-1',
            '二、': 'report-section--accent-2',
            '三、': 'report-section--accent-3',
            '四、': 'report-section--accent-4',
            '五、': 'report-section--accent-5',
            '六、': 'report-section--accent-6',
            '七、': 'report-section--accent-7',
        };
        return map[marker] || '';
    }

    function renderInterviewSummaryHtml(rawText) {
        const text = (rawText || '').trim();
        if (!text) {
            return '<p class="report-empty">（暂无报告内容）</p>';
        }

        const sections = splitSections(text);
        if (sections.length === 0) {
            return (
                `<div class="report-document">` +
                `<article class="report-section"><div class="report-section-body report-prose">${nl2brEscaped(text)}</div></article>` +
                `</div>`
            );
        }

        let html = '<div class="report-document">';
        for (const sec of sections) {
            const accent = sectionAccentClass(sec.marker);
            const isDim =
                sec.title.includes('多维度') ||
                sec.title.includes('评分') ||
                sec.marker === '二、';
            html += `<article class="report-section ${accent}">`;
            html += '<header class="report-section-head">';
            if (sec.marker) {
                html += `<span class="report-section-num">${escapeHtml(sec.marker.charAt(0))}</span>`;
            }
            html += `<h3 class="report-section-title">${escapeHtml(sec.title)}</h3>`;
            html += '</header>';

            if (isDim && sec.body) {
                const scores = parseDimensionScores(sec.body);
                const prose = stripDimensionLines(sec.body);
                if (hasAnyScore(scores)) {
                    html += '<div class="report-dimension-layout">';
                    html += `<div class="report-radar-column"><div class="report-chart-card">${buildRadarSvg(scores)}</div></div>`;
                    html += `<div class="report-bars-column"><div class="report-chart-card report-bars-card">${buildBarRows(scores)}</div></div>`;
                    html += '</div>';
                    if (prose) {
                        html += `<div class="report-section-body report-prose report-prose--dim">${nl2brEscaped(prose)}</div>`;
                    }
                } else {
                    html += `<div class="report-section-body report-prose">${nl2brEscaped(sec.body)}</div>`;
                }
            } else {
                html += `<div class="report-section-body report-prose">${nl2brEscaped(sec.body)}</div>`;
            }
            html += '</article>';
        }
        html += '</div>';
        return html;
    }

    global.renderInterviewSummaryHtml = renderInterviewSummaryHtml;
})(typeof window !== 'undefined' ? window : globalThis);

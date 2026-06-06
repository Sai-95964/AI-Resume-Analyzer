/**
 * Renders analysis results including full LLM dashboard sections.
 */

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text == null ? '' : String(text);
    return div.innerHTML;
}

function renderRecommendationCards(items) {
    if (!items || !items.length) {
        return '<p class="llm-empty">No items.</p>';
    }
    let html = '';
    items.forEach(rec => {
        const priority = (rec.priority || 'low').toLowerCase();
        html += `
            <div class="recommendation-card priority-${priority}">
                <div class="rec-header">
                    <span class="priority-badge">${escapeHtml(priority.toUpperCase())}</span>
                    <span class="rec-category">${escapeHtml(rec.category || '')}</span>
                </div>
                <p class="rec-message">${escapeHtml(rec.message || '')}</p>
                <p class="rec-action"><strong>Action:</strong> ${escapeHtml(rec.action || '')}</p>
            </div>`;
    });
    return html;
}

function renderList(items, className) {
    if (!items || !items.length) return '';
    let html = `<ul class="llm-list ${className || ''}">`;
    items.forEach(s => { html += '<li>' + escapeHtml(s) + '</li>'; });
    html += '</ul>';
    return html;
}

function renderLlmSections(llm) {
    if (!llm.enabled) {
        if (llm.reason || llm.error) {
            return `<div class="llm-section llm-section-muted">
                <p><strong>LLM layer:</strong> ${escapeHtml(llm.reason || llm.error)}</p>
                <p class="form-hint">Add OPENAI_API_KEY to .env — classical ATS scoring still ran above.</p>
            </div>`;
        }
        return '';
    }

    const review = llm.resume_review || {};
    const strengths = review.strengths || llm.strengths || [];
    const weaknesses = review.weaknesses || llm.weaknesses || [];
    const improvements = review.improvements || llm.improvements || [];
    const missing = llm.missing_skills_analysis || {};
    const fitScore = Number(llm.fit_score);

    let fitCard = '';
    if (!isNaN(fitScore)) {
        fitCard = `
            <div class="score-card score-card-ai">
                <h3>AI Fit Score</h3>
                <div class="score-value">${Math.round(fitScore)}%</div>
                <div class="score-bar">
                    <div class="score-fill score-fill-ai" style="width: ${Math.min(100, fitScore)}%"></div>
                </div>
            </div>`;
    }

    let html = `
        <div class="llm-section">
            <h3>AI Resume Review <span class="llm-badge">${escapeHtml(llm.model || 'LLM')}</span></h3>
            <div class="scores-section scores-section-inline">${fitCard}</div>
            <p class="llm-summary">${escapeHtml(llm.summary || '')}</p>
            <div class="llm-columns">
                <div class="llm-col">
                    <h4 class="llm-subhead llm-subhead-good">Strengths</h4>
                    ${renderList(strengths, 'llm-list-good')}
                </div>
                <div class="llm-col">
                    <h4 class="llm-subhead llm-subhead-warn">Weaknesses</h4>
                    ${renderList(weaknesses, 'llm-list-gaps')}
                </div>
                <div class="llm-col">
                    <h4 class="llm-subhead">Improvements</h4>
                    ${renderList(improvements)}
                </div>
            </div>
        </div>`;

    const learning = missing.learning_path || [];
    const llmMissing = missing.missing_skills || [];
    if (llmMissing.length || learning.length) {
        html += `
        <div class="llm-section">
            <h3>Skill Gap & Learning Path</h3>
            ${llmMissing.length ? '<p><strong>Missing skills:</strong> ' + llmMissing.map(escapeHtml).join(', ') + '</p>' : ''}
            <h4 class="llm-subhead">Recommended learning</h4>
            ${renderList(learning)}
        </div>`;
    }

    const ats = llm.ats_suggestions || [];
    if (ats.length) {
        html += `
        <div class="recommendations-section">
            <h3>ATS Improvement (AI)</h3>
            <div class="recommendations-list">${renderRecommendationCards(ats)}</div>
        </div>`;
    }

    const rewrites = llm.resume_rewrites || [];
    if (rewrites.length) {
        html += '<div class="llm-section"><h3>Resume Rewrites</h3><div class="rewrite-list">';
        rewrites.forEach(r => {
            html += `
                <div class="rewrite-card">
                    <p class="rewrite-label">Before</p>
                    <p class="rewrite-before">${escapeHtml(r.original || '')}</p>
                    <p class="rewrite-label">After</p>
                    <p class="rewrite-after">${escapeHtml(r.improved || '')}</p>
                </div>`;
        });
        html += '</div></div>';
    }

    const questions = llm.interview_questions || llm.interview_tips || [];
    if (questions.length) {
        html += `
        <div class="llm-section">
            <h3>Interview Questions</h3>
            <ol class="llm-ordered">${questions.map(q => '<li>' + escapeHtml(q) + '</li>').join('')}</ol>
        </div>`;
    }

    if (llm.career_guidance) {
        html += `
        <div class="llm-section llm-section-guidance">
            <h3>Career Guidance</h3>
            <p class="llm-summary">${escapeHtml(llm.career_guidance)}</p>
        </div>`;
    }

    return html;
}

function renderResults(results, container) {
    const atsScore = Number(results.ats_score) || 0;
    const similarityScore = Number(results.similarity_score) || 0;
    const matchedSkills = results.matched_skills || [];
    const missingSkills = results.missing_skills || [];
    const totalRequired = results.total_required ?? matchedSkills.length + missingSkills.length;
    const llm = results.llm_insights || {};
    const recommendations = results.recommendations || [];

    let html = `
        <div class="scores-section">
            <div class="score-card">
                <h3>ATS Score <span class="score-tag">TF-IDF + rules</span></h3>
                <div class="score-value">${Math.round(atsScore)}%</div>
                <div class="score-bar">
                    <div class="score-fill" style="width: ${Math.min(100, atsScore)}%"></div>
                </div>
            </div>
            <div class="score-card">
                <h3>Match Score</h3>
                <div class="score-value">${Math.round(similarityScore)}%</div>
                <div class="score-bar">
                    <div class="score-fill" style="width: ${Math.min(100, similarityScore)}%"></div>
                </div>
            </div>
        </div>
        ${renderLlmSections(llm)}
        <div class="skills-section">
            <div class="skills-card">
                <h3>Matched Skills (${matchedSkills.length}/${totalRequired})</h3>
                <div class="skills-list">
                    ${matchedSkills.map(s => '<span class="skill-tag skill-matched">' + escapeHtml(s) + '</span>').join('')}
                </div>
            </div>
            <div class="skills-card">
                <h3>Missing Skills (${missingSkills.length})</h3>
                <div class="skills-list">
                    ${missingSkills.map(s => '<span class="skill-tag skill-missing">' + escapeHtml(s) + '</span>').join('')}
                </div>
            </div>
        </div>`;

    if (!llm.enabled || !(llm.ats_suggestions && llm.ats_suggestions.length)) {
        html += `
        <div class="recommendations-section">
            <h3>${llm.enabled ? 'Career Recommendations' : 'Top Recommendations'}</h3>
            <div class="recommendations-list">
                ${recommendations.length ? renderRecommendationCards(recommendations) : '<p>No recommendations needed.</p>'}
            </div>
        </div>`;
    } else if (recommendations.length) {
        html += `
        <div class="recommendations-section">
            <h3>Career Recommendations</h3>
            <div class="recommendations-list">${renderRecommendationCards(recommendations)}</div>
        </div>`;
    }

    html += `
        <div class="details-section">
            <h3>Detailed Breakdown</h3>
            <div class="details-grid">
                <div class="detail-item">
                    <label>Skill Match:</label>
                    <span>${matchedSkills.length} / ${totalRequired} skills</span>
                </div>
                <div class="detail-item">
                    <label>Match Percentage:</label>
                    <span>${Math.round(Number(results.skill_match_percentage) || 0)}%</span>
                </div>
                <div class="detail-item">
                    <label>Job Seniority:</label>
                    <span>${escapeHtml(results.job_seniority || 'Not detected')}</span>
                </div>
                <div class="detail-item">
                    <label>LLM:</label>
                    <span>${llm.enabled ? escapeHtml(llm.model || 'on') : 'off (rule-based only)'}</span>
                </div>
                <div class="detail-item">
                    <label>Analysis Time:</label>
                    <span>${results.timestamp ? new Date(results.timestamp).toLocaleString() : 'N/A'}</span>
                </div>
            </div>
        </div>`;

    container.innerHTML = html;
}

function exportResultsJson() {
    const raw = sessionStorage.getItem('analysisResults');
    if (!raw) {
        alert('No results to export');
        return;
    }
    const blob = new Blob([raw], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'resume_analysis_' + Date.now() + '.json';
    link.click();
    URL.revokeObjectURL(url);
}

document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('resultsContainer');
    const exportBtn = document.getElementById('exportJsonBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportResultsJson);
    }

    const resultsJson = sessionStorage.getItem('analysisResults');
    if (!resultsJson) {
        container.innerHTML = '<div class="error-message"><p>No results found. Please analyze a resume first.</p></div>';
        return;
    }
    try {
        renderResults(JSON.parse(resultsJson), container);
    } catch (error) {
        container.innerHTML = '<div class="error-message"><p>Error loading results: ' + escapeHtml(error.message) + '</p></div>';
    }
});

// Safely remove only exact footer or paragraph nodes with the unwanted text
document.addEventListener('DOMContentLoaded', function() {
    try {
        const unwanted = '© 2024 AI Resume Analyzer. All rights reserved.';

        function removeMatching(node) {
            if (!node || node.nodeType !== Node.ELEMENT_NODE) return;
            const tag = node.tagName.toLowerCase();
            if (tag === 'footer') {
                node.remove();
                return;
            }
            if (tag === 'p' && node.textContent && node.textContent.trim() === unwanted) {
                node.remove();
                return;
            }
        }

        // remove any existing exact matches
        document.querySelectorAll('footer, p').forEach(removeMatching);

        // observe future additions and remove exact matches only
        const observer = new MutationObserver(mutations => {
            for (const m of mutations) {
                m.addedNodes && m.addedNodes.forEach(n => {
                    if (n.nodeType === Node.ELEMENT_NODE) {
                        removeMatching(n);
                        // also check descendants
                        n.querySelectorAll && n.querySelectorAll('footer, p').forEach(removeMatching);
                    }
                });
            }
        });
        observer.observe(document.documentElement || document.body, { childList: true, subtree: true });
    } catch (e) {
        // noop
    }
});

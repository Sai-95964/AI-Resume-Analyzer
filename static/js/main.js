document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analysisForm');
    const llmHint = document.getElementById('llmHint');
    const useLlmCheckbox = document.getElementById('useLlm');
    const loadSampleBtn = document.getElementById('loadSampleBtn');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingMessage = document.getElementById('loadingMessage');
    const rewriteTool = document.getElementById('rewriteTool');
    const rewriteBtn = document.getElementById('rewriteBtn');
    const rewriteInput = document.getElementById('rewriteInput');
    const rewriteOutput = document.getElementById('rewriteOutput');

    let llmAvailable = false;

    fetch('/health')
        .then(r => r.json())
        .then(data => {
            if (data.llm && data.llm.available) {
                llmAvailable = true;
                if (llmHint) {
                    const provider = data.llm.provider === 'gemini' ? 'Gemini' : 'AI';
                    llmHint.textContent =
                        provider + ' enabled (' + (data.llm.model || 'LLM') + '). Uncheck the box for faster rule-only scoring.';
                }
                if (rewriteTool) rewriteTool.hidden = false;
            } else if (llmHint) {
                llmHint.textContent =
                    'Add GOOGLE_API_KEY (Gemini) or OPENAI_API_KEY in .env. Rule-based ATS works without it.';
            }
        })
        .catch(() => {});

    if (loadSampleBtn) {
        loadSampleBtn.addEventListener('click', async function() {
            try {
                const res = await fetch('/api/samples');
                const data = await res.json();
                if (!res.ok) throw new Error(data.error || 'Failed to load samples');

                document.getElementById('jobDescription').value = data.job_description;

                const resumeInput = document.getElementById('resume');
                const blob = new Blob([data.resume_text], { type: 'text/plain' });
                const file = new File([blob], 'sample_resume.txt', { type: 'text/plain' });
                const dt = new DataTransfer();
                dt.items.add(file);
                resumeInput.files = dt.files;

                showNotification('Demo resume and job description loaded.', 'info');
            } catch (err) {
                alert('Could not load demo: ' + err.message);
            }
        });
    }

    if (rewriteBtn && rewriteInput) {
        rewriteBtn.addEventListener('click', async function() {
            const text = rewriteInput.value.trim();
            const job = document.getElementById('jobDescription').value.trim();
            if (!text) {
                alert('Enter a bullet to rewrite');
                return;
            }
            rewriteBtn.disabled = true;
            rewriteBtn.textContent = 'Rewriting...';
            try {
                const res = await fetch('/api/llm/rewrite', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, job_description: job }),
                });
                const data = await res.json();
                if (!res.ok || !data.enabled) {
                    throw new Error(data.error || data.reason || 'Rewrite failed');
                }
                rewriteOutput.hidden = false;
                rewriteOutput.innerHTML =
                    '<p><strong>Before:</strong> ' + escapeHtml(data.original || text) + '</p>' +
                    '<p><strong>After:</strong> ' + escapeHtml(data.improved || '') + '</p>' +
                    (data.tips ? '<p><em>' + escapeHtml(data.tips) + '</em></p>' : '');
            } catch (err) {
                alert(err.message);
            } finally {
                rewriteBtn.disabled = false;
                rewriteBtn.textContent = 'Rewrite bullet';
            }
        });
    }

    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            const resume = document.getElementById('resume');
            const jobDescription = document.getElementById('jobDescription');

            if (!resume.files.length) {
                alert('Please select a resume file');
                return;
            }
            if (!jobDescription.value.trim()) {
                alert('Please enter a job description');
                return;
            }

            const file = resume.files[0];
            const ext = file.name.split('.').pop().toLowerCase();
            if (!['pdf', 'docx', 'txt'].includes(ext)) {
                alert('Please upload a PDF, DOCX, or TXT file');
                return;
            }

            const useLlm = useLlmCheckbox ? useLlmCheckbox.checked : false;
            const submitBtn = form.querySelector('.btn-analyze');
            const originalText = submitBtn.textContent;

            if (loadingOverlay) {
                loadingOverlay.hidden = false;
                if (loadingMessage) {
                    loadingMessage.textContent = useLlm && llmAvailable
                        ? 'Running ATS + AI analysis...'
                        : 'Running ATS analysis...';
                }
            }
            submitBtn.disabled = true;

            let succeeded = false;
            try {
                const formData = new FormData();
                formData.append('resume', file);
                formData.append('job_description', jobDescription.value);
                formData.append('use_llm', useLlm ? 'true' : 'false');

                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    body: formData,
                });

                let payload = {};
                try {
                    payload = await response.json();
                } catch (_) {
                    payload = { error: 'Invalid server response' };
                }

                if (!response.ok) {
                    alert('Error: ' + (payload.error || 'Analysis failed'));
                    return;
                }

                sessionStorage.setItem('analysisResults', JSON.stringify(payload));
                sessionStorage.setItem('lastJobDescription', jobDescription.value);
                succeeded = true;
                window.location.href = '/results';
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                if (loadingOverlay) loadingOverlay.hidden = true;
                if (!succeeded) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }
            }
        });
    }
});

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text == null ? '' : String(text);
    return div.innerHTML;
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = 'notification notification-' + (type || 'info');
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

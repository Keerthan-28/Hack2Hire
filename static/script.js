document.addEventListener('DOMContentLoaded', () => {
    const jsonInput = document.getElementById('json-input');
    const processBtn = document.getElementById('process-btn');
    const loadExampleBtn = document.getElementById('load-example-btn');
    const clearBtn = document.getElementById('clear-btn');
    const resultsPanel = document.getElementById('results-content');
    const emptyState = document.getElementById('empty-state');

    // --- Event Listeners ---

    loadExampleBtn.addEventListener('click', async () => {
        try {
            const res = await fetch('/api/example');
            const data = await res.json();
            jsonInput.value = JSON.stringify(data, null, 2);
        } catch (e) {
            console.error('Failed to load example', e);
        }
    });

    clearBtn.addEventListener('click', () => {
        jsonInput.value = '';
        showResults(false);
    });

    processBtn.addEventListener('click', async () => {
        const rawJson = jsonInput.value.trim();
        if (!rawJson) return alert('Please enter JSON input first');

        setLoading(true);

        try {
            const payload = JSON.parse(rawJson);
            const res = await fetch('/api/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await res.json();

            if (result.error) {
                alert('Error: ' + result.error);
            } else {
                renderResults(result);
                showResults(true);
            }

        } catch (e) {
            alert('Invalid JSON Format: ' + e.message);
        } finally {
            setLoading(false);
        }
    });

    // --- Functions ---

    function setLoading(isLoading) {
        const loader = processBtn.querySelector('.loader');
        const text = processBtn.querySelector('.btn-text');

        if (isLoading) {
            processBtn.disabled = true;
            loader.classList.remove('hidden');
            text.classList.add('hidden');
        } else {
            processBtn.disabled = false;
            loader.classList.add('hidden');
            text.classList.remove('hidden');
        }
    }

    function showResults(visible) {
        if (visible) {
            emptyState.classList.add('hidden');
            resultsPanel.classList.remove('hidden');
        } else {
            emptyState.classList.remove('hidden');
            resultsPanel.classList.add('hidden');
        }
    }

    function renderResults(data) {
        // 1. Score Circle
        const score = data.final_score;
        document.getElementById('final-score').textContent = score;

        // Calculate stroke offset
        // Max (100% or more) = 0 offset. 0% = 314 offset.
        // Cap visual at 100% even if score > 100
        const visualScore = Math.min(100, Math.max(0, score));
        const offset = 314 - (314 * visualScore / 100);
        document.getElementById('score-ring').style.strokeDashoffset = offset;

        // Color based on score
        const ring = document.getElementById('score-ring');
        if (score >= 90) ring.style.stroke = '#10b981'; // Green
        else if (score >= 70) ring.style.stroke = '#6366f1'; // Indigo
        else if (score >= 50) ring.style.stroke = '#f59e0b'; // Amber
        else ring.style.stroke = '#ef4444'; // Red

        // 2. Stats
        const summary = data.performance_summary;
        document.getElementById('stats-questions').textContent = `${summary.attempted_questions} / ${summary.total_questions}`;
        document.getElementById('stats-time').textContent = summary.average_time_percentage + '%';
        document.getElementById('stats-interruptions').textContent = summary.interruption_count;

        const termBox = document.getElementById('termination-box');
        if (summary.early_termination) {
            termBox.classList.remove('hidden');
            document.getElementById('stats-termination').textContent = summary.termination_reason;
        } else {
            termBox.classList.add('hidden');
        }

        // 3. Breakdown Table
        const tbody = document.getElementById('breakdown-body');
        tbody.innerHTML = '';
        data.score_breakdown.forEach(q => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${q.q_id}</td>
                <td>${q.raw_score}</td>
                <td style="${q.time_penalty > 0 ? 'color: var(--danger)' : ''}">-${q.time_penalty}</td>
                <td style="${q.interruption_penalty > 0 ? 'color: var(--danger)' : ''}">-${q.interruption_penalty}</td>
                <td style="color: var(--primary)">x${q.adaptive_weight}</td>
                <td style="font-weight:700">${q.weighted_score}</td>
            `;
            tbody.appendChild(row);
        });

        // 4. State Log
        const logContainer = document.getElementById('state-log');
        logContainer.innerHTML = '';
        data.state_log.forEach(log => {
            const item = document.createElement('div');
            item.className = 'log-item';
            item.innerHTML = `
                <span class="tag ${log.state}">${log.state}</span>
                <span>${log.question}</span>
                <span class="log-weight">Weight: ${log.weight}</span>
            `;
            logContainer.appendChild(item);
        });
    }
});

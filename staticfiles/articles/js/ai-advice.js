/**
 * تحميل وعرض نصائح الذكاء الاصطناعي
 */

function loadAiAdvice(codArt, inModal = false) {
    const loadingEl = document.getElementById('aiLoading');
    const contentEl = document.getElementById('aiContent');
    const summaryEl = document.getElementById('aiSummary');
    const recommendationsEl = document.getElementById('aiRecommendations');
    const safetyEl = document.getElementById('aiSafety');
    
    if (loadingEl) loadingEl.classList.add('show');
    if (contentEl) contentEl.style.display = 'none';
    
    // ✅ استخدام الدالة المساعدة لبناء الرابط
    const url = getAiAdviceUrl(codArt);
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ cod_art: codArt })
    })
        .then(response => response.json())
        .then(data => {
            if (loadingEl) loadingEl.classList.remove('show');
            if (contentEl) contentEl.style.display = 'block';
            
            // عرض التلميحات
            if (summaryEl) {
                const tips = data.usage_tips_fr || data.usage_tips_ar || [];
                summaryEl.innerHTML = tips.length > 0 ? `
                    <ul class="mb-0">
                        ${tips.map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                ` : '<p class="text-muted">Aucun conseil disponible</p>';
            }
            
            // عرض التوصيات
            if (recommendationsEl) {
                const recs = data.recommended_accessories || [];
                recommendationsEl.innerHTML = recs.length > 0 ? `
                    ${recs.map(rec => `
                        <div class="ai-recommendation">
                            <div class="priority-badge priority-${rec.priority || 'low'}">${rec.priority || 'low'}</div>
                            <div>
                                <strong>${rec.nom}</strong>
                                <div class="small text-muted">${rec.reason}</div>
                            </div>
                        </div>
                    `).join('')}
                ` : '<p class="text-muted">Aucune recommandation</p>';
            }
            
            // عرض ملاحظات السلامة
            if (safetyEl) {
                const notes = data.safety_notes || [];
                safetyEl.innerHTML = notes.length > 0 ? `
                    <ul class="mb-0">
                        ${notes.map(note => `<li>${note}</li>`).join('')}
                    </ul>
                ` : '<p class="text-muted">Aucune note de sécurité</p>';
            }
        })
        .catch(error => {
            console.error('Erreur chargement AI:', error);
            if (loadingEl) loadingEl.classList.remove('show');
            if (summaryEl) {
                summaryEl.innerHTML = `
                    <div class="alert alert-warning small mb-0">
                        <i class="bi bi-exclamation-triangle me-1"></i>
                        Service IA indisponible
                    </div>
                `;
            }
        });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
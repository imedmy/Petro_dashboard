/**
 * تحميل وعرض الإحصائيات المتعلقة بالمقالات المرتبطة
 */

function loadRelatedStats(codArt) {
    const loadingEl = document.getElementById('relatedLoading');
    const contentEl = document.getElementById('relatedContent');
    const listEl = document.getElementById('relatedList');
    const totalMovEl = document.getElementById('totalMovements');
    
    if (loadingEl) loadingEl.classList.add('show');
    if (contentEl) contentEl.style.display = 'none';
    
    // ✅ استخدام الدالة المساعدة لبناء الرابط
    const url = getRelatedStatsUrl(codArt);
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (loadingEl) loadingEl.classList.remove('show');
            if (contentEl) contentEl.style.display = 'block';
            
            if (totalMovEl) {
                totalMovEl.textContent = data.total_movements || 0;
            }
            
            if (!data.related_articles || data.related_articles.length === 0) {
                if (listEl) {
                    listEl.innerHTML = `
                        <div class="text-center text-muted py-4">
                            <i class="bi bi-info-circle fs-4 d-block mb-2"></i>
                            <small>Aucun article associé trouvé</small>
                        </div>
                    `;
                }
                return;
            }
            
            if (listEl) {
                listEl.innerHTML = data.related_articles.map(article => `
                    <div class="related-article-item ${article.confidence_level === 'high' ? 'high-confidence' : article.confidence_level === 'medium' ? 'medium-confidence' : ''}"
                         onclick="selectRelatedArticle('${article.cod_art}')">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>${article.cod_art}</strong>
                                <div class="small text-muted">${article.lib_art || 'Inconnu'}</div>
                            </div>
                            <div class="text-end">
                                <div class="badge ${article.confidence_level === 'high' ? 'bg-success' : article.confidence_level === 'medium' ? 'bg-warning' : 'bg-secondary'}">
                                    ${(article.co_occurrence_rate * 100).toFixed(0)}%
                                </div>
                                <div class="small text-muted mt-1">${article.co_occurrence} fois</div>
                            </div>
                        </div>
                    </div>
                `).join('');
            }
        })
        .catch(error => {
            console.error('Erreur chargement stats:', error);
            if (loadingEl) loadingEl.classList.remove('show');
            if (listEl) {
                listEl.innerHTML = `
                    <div class="text-center text-danger py-4">
                        <i class="bi bi-exclamation-triangle fs-4 d-block mb-2"></i>
                        <small>Erreur de chargement</small>
                    </div>
                `;
            }
        });
}

function selectRelatedArticle(codArt) {
    console.log('Article sélectionné:', codArt);
    openSmartAnalysis(codArt);
}
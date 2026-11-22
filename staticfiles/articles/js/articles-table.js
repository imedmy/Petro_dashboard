/**
 * ============================================================================
 * ✅ articles-table.js - إدارة جدول DataTables للسلع
 * ============================================================================
 * ميزات:
 * - Server-Side Processing مع دعم الفلاتر المتقدمة
 * - تفعيل التبويبات عند اختيار مقال
 * - معالجة أخطاء AJAX بشكل احترافي
 * - دعم البحث متعدد الكلمات مع مشغلات (starts/ends/contains/exact)
 * - تحسينات UX: مؤشرات تحميل، إشعارات، تأثيرات حركية
 * ============================================================================
 */

(function() {
    'use strict';
    
    // ✅ تهيئة الجدول الرئيسية
    window.initArticlesTable = function() {
        const table = $('#articlesTable');
        if (!table.length) {
            console.warn('Table #articlesTable not found');
            return;
        }
        
        // تدمير الجدول إذا كان موجودًا مسبقًا (لتجنب التكرار)
        if ($.fn.DataTable.isDataTable(table)) {
            table.DataTable().destroy();
        }
        
        window.articlesApp.dataTable = table.DataTable({
            // === إعدادات Server-Side Processing ===
            processing: true,
            serverSide: true,
            deferRender: true,  // تحسين الأداء مع بيانات كثيرة
            
            // === مصدر البيانات عبر AJAX ===
            ajax: {
                url: window.articlesUrls?.apiData || '/articles/api/data/',
                type: 'GET',
                cache: false,  // منع التخزين المؤقت لضمان تحديث البيانات
                
                // ✅ معالجة معلمات الإرسال
                data: function(d) {
                    return buildAjaxData(d);
                },
                
                // ✅ معالجة الاستجابة
                dataSrc: function(json) {
                    updateResultsCount(json);
                    hideLoadingIndicator();
                    
                    // التحقق من وجود خطأ في الاستجابة
                    if (json.error) {
                        console.error('API Error:', json.error);
                        showToast('Erreur: ' + json.error, 'error');
                        return [];
                    }
                    
                    return json.data || [];
                },
                
                // ✅ معالجة الأخطاء
                error: function(xhr, status, error) {
                    hideLoadingIndicator();
                    console.error('❌ AJAX Error:', { status, error, response: xhr.responseText });
                    
                    let message = 'Erreur de chargement des données';
                    try {
                        const resp = JSON.parse(xhr.responseText);
                        if (resp.error) message = resp.error;
                    } catch(e) {
                        if (xhr.status === 404) message = 'Endpoint non trouvé';
                        else if (xhr.status === 500) message = 'Erreur serveur interne';
                        else if (xhr.status === 403) message = 'Accès non autorisé';
                    }
                    
                    showToast(message, 'error');
                    updateResultsCount({ recordsFiltered: 0 });
                }
            },
            
            // === تعريف الأعمدة ===
            columns: [
                { 
                    data: 'COD_ART',
                    className: 'text-nowrap',
                    render: function(data, type, row) {
                        if (type === 'display') {
                            return `<code class="article-code" title="${escapeHtml(data || '')}">${escapeHtml(data || '-')}</code>`;
                        }
                        return data;
                    }
                },
                { 
                    data: 'LIB_ART',
                    render: function(data, type, row) {
                        if (type === 'display') {
                            const text = data || '-';
                            return `<span title="${escapeHtml(text)}">${text.length > 60 ? escapeHtml(text.substring(0, 60)) + '...' : escapeHtml(text)}</span>`;
                        }
                        return data;
                    }
                },
                { 
                    data: 'CLASS_COUT', 
                    className: 'text-center',
                    render: function(data) {
                        return data ? `<span class="badge bg-light text-dark">${escapeHtml(data)}</span>` : '-';
                    }
                },
                { 
                    data: 'DATE_CREAT',
                    className: 'text-center',
                    render: function(data, type, row) {
                        if (!data) return '-';
                        if (type === 'sort') return data;  // للفرز نستخدم القيمة الأصلية
                        return formatDate(data);
                    }
                },
                { 
                    data: 'DERNIER_MV',
                    className: 'text-center',
                    render: function(data, type, row) {
                        if (!data) return '-';
                        if (type === 'sort') return data;
                        return formatDate(data);
                    }
                },
                { 
                    data: 'EMPL', 
                    className: 'text-center',
                    render: function(data) {
                        return data ? escapeHtml(data) : '-';
                    }
                },
                { 
                    data: 'PU',
                    className: 'text-end',
                    render: function(data, type, row) {
                        if (type === 'sort') return parseFloat(data) || 0;
                        return data ? parseFloat(data).toFixed(3) : '0.000';
                    }
                },
                { 
                    data: 'QTE_SURSTK',
                    className: 'text-end fw-bold',
                    render: function(data, type, row) {
                        if (type === 'sort') return parseFloat(data) || 0;
                        
                        if (!data) return '<span class="text-danger">0.0</span>';
                        const val = parseFloat(data);
                        const color = val > 0 ? '#0d6efd' : '#dc3545';
                        return `<span style="color:${color}">${val.toFixed(1)}</span>`;
                    }
                },
                { 
                    data: 'LIB_UM', 
                    className: 'text-center',
                    render: function(data) {
                        return data ? `<span class="badge bg-secondary">${escapeHtml(data)}</span>` : '-';
                    }
                },
                { 
                    data: 'VAL_ART',
                    className: 'text-center',
                    render: function(data, type, row) {
                        if (!data) return '<span class="text-muted small">N/A</span>';
                        
                        const map = {
                            '1': {text: '100%', class: 'val-art-1', title: 'Valeur complète'},
                            '2': {text: '75%', class: 'val-art-2', title: 'Valeur partielle'},
                            '3': {text: '25%', class: 'val-art-3', title: 'Valeur faible'},
                            '4': {text: '0%', class: 'val-art-4', title: 'Sans valeur'}
                        };
                        const m = map[data.toString()];
                        if (m) {
                            return `<span class="val-art-badge ${m.class}" title="${m.title}">${m.text}</span>`;
                        }
                        return '<span class="text-muted small">N/A</span>';
                    }
                },
                { 
                    data: 'DESIGNAT',
                    render: function(data, type, row) {
                        if (type === 'display') {
                            const text = data || '-';
                            return `<span title="${escapeHtml(text)}">${text.length > 50 ? escapeHtml(text.substring(0, 50)) + '...' : escapeHtml(text)}</span>`;
                        }
                        return data;
                    }
                },
                { 
                    data: null,
                    className: 'text-center no-sort',
                    orderable: false,
                    render: function(data, type, row) {
                        if (type !== 'display') return '';
                        
                        const caractUrl = getArticleCaracteristiquesUrl(data.COD_ART);
                        const hasSerial = data.has_serial_tracking || false;
                        const suiviUrl = hasSerial ? getArticleSuiviSerialUrl(data.COD_ART) : '#';
                        
                        return `
                            <div class="btn-group btn-group-sm" role="group" aria-label="Actions">
                                <button type="button" class="btn btn-outline-primary action-btn" 
                                        title="Voir la codification" 
                                        aria-label="Codification"
                                        onclick="openCodificationModal('${escapeHtml(data.COD_ART)}', '${escapeHtml(data.LIB_ART || '')}')">
                                    <i class="bi bi-upc"></i>
                                </button>
                                <a href="${caractUrl}"
                                   class="btn btn-outline-success action-btn"
                                   title="Gérer les caractéristiques"
                                   aria-label="Caractéristiques">
                                    <i class="bi bi-tags"></i>
                                </a>
                                ${hasSerial ? `
                                <a href="${suiviUrl}"
                                   class="btn btn-outline-info action-btn"
                                   title="Suivi des unités par numéro de série"
                                   aria-label="Suivi série">
                                    <i class="bi bi-hash"></i>
                                </a>` : ''}
                                <button type="button" class="btn btn-outline-warning action-btn"
                                        title="Analyse intelligente"
                                        aria-label="Analyse IA"
                                        onclick="openSmartAnalysis('${escapeHtml(data.COD_ART)}')">
                                    <i class="bi bi-lightbulb"></i>
                                </button>
                            </div>
                        `;
                    }
                }
            ],
            
            // === اللغة الفرنسية ===
            language: {
                "processing": "Traitement en cours...",
                "search": "Rechercher :",
                "searchPlaceholder": "Filtrer les résultats...",
                "lengthMenu": "Afficher _MENU_ éléments",
                "info": "Affichage de _START_ à _END_ sur _TOTAL_ éléments",
                "infoEmpty": "Aucun élément à afficher",
                "infoFiltered": "(filtré de _MAX_ éléments au total)",
                "loadingRecords": "Chargement...",
                "zeroRecords": "Aucun élément correspondant trouvé",
                "emptyTable": "Aucune donnée disponible dans le tableau",
                "paginate": {
                    "first": "« Premier",
                    "previous": "‹ Précédent",
                    "next": "Suivant ›",
                    "last": "Dernier »"
                },
                "aria": {
                    "sortAscending": ": activer pour trier la colonne par ordre croissant",
                    "sortDescending": ": activer pour trier la colonne par ordre décroissant"
                }
            },
            
            // === خيارات العرض ===
            pageLength: 20,
            lengthMenu: [[20, 50, 100, -1], [20, 50, 100, "Tous"]],
            responsive: {
                details: {
                    type: 'column',
                    target: 'tr'
                }
            },
            
            // === أعمدة غير قابلة للفرز ===
            columnDefs: [
                { targets: 'no-sort', orderable: false },
                { targets: [0, 1, 10], responsivePriority: 1 },  // أولوية عالية للأعمدة المهمة
                { targets: [6, 7], type: 'num' }  // أعمدة رقمية للفرز الصحيح
            ],
            
            // === حدث النقر على السطر - ✅ التصحيح الرئيسي هنا ===
            createdRow: function(row, data, dataIndex) {
                if (!data) return;
                
                $(row).on('click', function(e) {
                    // تجاهل النقر على أزرار الإجراءات
                    if ($(e.target).closest('.action-btn, .btn-group, a').length) {
                        e.stopPropagation();
                        return;
                    }
                    
                    // تبديل تحديد السطر
                    const $row = $(this);
                    const isSelected = $row.toggleClass('selected').hasClass('selected');
                    
                    if (isSelected) {
                        // ✅ تعيين المقال الحالي - هذا هو المفتاح لتفعيل التبويبات
                        window.articlesApp.currentArticle = data;
                        
                        // ✅ تفعيل التبويبات الثانوية وإزالة disabled
                        enableSecondaryTabs();
                        
                        // ✅ تحميل محتوى التبويب النشط تلقائيًا إذا كان واحدًا من الثلاثة
                        const activeTab = document.querySelector('#articlesTabs .nav-link.active');
                        if (activeTab) {
                            const tabTarget = activeTab.dataset.bsTarget;
                            if (tabTarget === '#related') {
                                loadRelatedStats(data.COD_ART);
                            } else if (tabTarget === '#ai') {
                                loadAiAdvice(data.COD_ART);
                            } else if (tabTarget === '#caract') {
                                loadArticleCaracteristiques(data.COD_ART);
                            }
                        }
                        
                        // إشعار صغير
                        showToast(`Article sélectionné: ${data.COD_ART}`, 'info');
                    } else {
                        // إلغاء التحديد
                        window.articlesApp.currentArticle = null;
                        disableSecondaryTabs();
                    }
                });
                
                // إضافة tooltip للأسطر الطويلة
                $(row).find('[title]').tooltip({ trigger: 'hover', placement: 'top' });
            },
            
            // === عند اكتمال الرسم ===
            drawCallback: function(settings) {
                updateTableWidth();
                initializeRowTooltips();
            },
            
            // === عند بدء الطلب ===
            preDrawCallback: function(settings) {
                showLoadingIndicator();
            }
        });
        
        // ✅ ربط أحداث الفلاتر
        bindFilterEvents();
    };
    
    /**
     * ✅ بناء معلمات AJAX للفلاتر
     */
    function buildAjaxData(d) {
        // === معالجة الفلاتر مع المشغلات ===
        
        // دالة مساعدة لإضافة شرط البحث
        function addSearchCondition(fieldName, inputValue, operatorSelector) {
            const val = inputValue?.trim();
            if (!val) return;
            
            const operatorEl = document.querySelector(operatorSelector);
            const operator = operatorEl?.value || 'contains';
            
            const likeValue = buildLikeCondition(val, operator);
            if (likeValue) {
                d[fieldName + '_op'] = operator;  // نرسل المشغل أيضًا
                d[fieldName] = likeValue;
            }
        }
        
        // Code Article
        const codArtVal = document.querySelector('input[name="cod_art"]')?.value;
        if (codArtVal?.trim()) {
            addSearchCondition('cod_art', codArtVal, 'select[data-target="cod_art"]');
        }
        
        // Libellé Article
        const libArtVal = document.querySelector('input[name="lib_art"]')?.value;
        if (libArtVal?.trim()) {
            addSearchCondition('lib_art', libArtVal, 'select[data-target="lib_art"]');
        }
        
        // الفلاتر الأخرى (بدون مشغلات)
        const fields = ['class_cout', 'lib_um', 'empl', 'qte_min', 'qte_max', 
                       'pu_min', 'pu_max', 'val_art', 'nat_stock',
                       'date_min', 'date_max', 'dernier_mv_min', 'dernier_mv_max'];
        
        fields.forEach(field => {
            const el = document.querySelector(`[name="${field}"]`);
            if (el && el.value?.trim()) {
                d[field] = el.value.trim();
            }
        });
        
        return d;
    }
    
    /**
     * ✅ تحديث عدد النتائج
     */
    function updateResultsCount(json) {
        const countEl = document.getElementById('resultsCount');
        if (countEl && json.recordsFiltered !== undefined) {
            countEl.textContent = `${json.recordsFiltered.toLocaleString('fr-FR')} article(s) trouvé(s)`;
            countEl.classList.remove('text-danger');
        }
    }
    
    /**
     * ✅ إظهار/إخفاء مؤشر التحميل
     */
    function showLoadingIndicator() {
        const indicator = document.getElementById('loadingIndicator');
        if (indicator) indicator.style.display = 'inline';
    }
    
    function hideLoadingIndicator() {
        const indicator = document.getElementById('loadingIndicator');
        if (indicator) indicator.style.display = 'none';
    }
    
    /**
     * ✅ تفعيل التبويبات الثانوية عند اختيار مقال
     */
    function enableSecondaryTabs() {
		const tabs = ['#related-tab', '#ai-tab', '#caract-tab', '#stats-tab']; // ← أضف #stats-tab
		tabs.forEach(tabId => {
			const tab = document.querySelector(tabId);
			if (tab) {
				tab.disabled = false;
				tab.classList.remove('disabled');
				tab.title = 'Cliquez pour afficher';
				tab.setAttribute('aria-disabled', 'false');
			}
		});
	}
    
    /**
     * ✅ تعطيل التبويبات الثانوية عند إلغاء التحديد
     */
    function disableSecondaryTabs() {
        const tabs = ['#related-tab', '#ai-tab', '#caract-tab'];
        tabs.forEach(tabId => {
            const tab = document.querySelector(tabId);
            if (tab) {
                tab.disabled = true;
                tab.classList.add('disabled');
                tab.title = 'Sélectionnez un article d\'abord';
                tab.setAttribute('aria-disabled', 'true');
            }
        });
    }
    
    /**
     * ✅ ربط أحداث الفلاتر
     */
    function bindFilterEvents() {
        // زر تطبيق الفلاتر
        const applyBtn = document.getElementById('applyFiltersBtn');
        if (applyBtn) {
            applyBtn.addEventListener('click', function() {
                if (window.articlesApp.dataTable) {
                    window.articlesApp.dataTable.ajax.reload();
                    showToast('Filtres appliqués', 'success');
                }
            });
        }
        
        // زر إعادة التعيين
        const resetBtn = document.getElementById('resetFiltersBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                const form = document.getElementById('advancedFiltersForm');
                if (form) {
                    form.reset();
                    // إعادة تعيين مشغلات البحث إلى القيم الافتراضية
                    const codOp = document.querySelector('select[data-target="cod_art"]');
                    const libOp = document.querySelector('select[data-target="lib_art"]');
                    if (codOp) codOp.value = 'starts';
                    if (libOp) libOp.value = 'contains';
                }
                if (window.articlesApp.dataTable) {
                    window.articlesApp.dataTable.ajax.reload();
                    showToast('Filtres réinitialisés', 'info');
                }
            });
        }
        
        // تحديث فوري عند تغيير مشغل البحث (اختياري)
        document.querySelectorAll('select.filter-operator').forEach(select => {
            select.addEventListener('change', function() {
                // يمكن إضافة تأكيد بصري هنا
                this.closest('.input-group')?.classList.add('border-primary');
                setTimeout(() => {
                    this.closest('.input-group')?.classList.remove('border-primary');
                }, 300);
                // لا نعيد التحميل تلقائيًا لتجنب إزعاج المستخدم
            });
        });
    }
    
    /**
     * ✅ تهيئة tooltips للأسطر
     */
    function initializeRowTooltips() {
        // تهيئة Bootstrap tooltips للعناصر الجديدة
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
                new bootstrap.Tooltip(el);
            });
        }
    }
    
    // ============================================================================
    // ✅ دوال اللوحة الذكية (محافظة على التوافق مع الكود القديم)
    // ============================================================================
    
    window.showSmartPanel = function(article) {
        // هذه الدالة محفوظة للتوافق - يمكن إزالتها إذا لم تعد مستخدمة
        console.log('showSmartPanel deprecated - use tabs instead');
    };
    
    window.hideSmartPanel = function() {
        console.log('hideSmartPanel deprecated - use tabs instead');
    };
    
    // ============================================================================
    // ✅ دوال عامة مساعدة
    // ============================================================================
    
    /**
     * تنسيق التاريخ
     */
    window.formatDate = function(dateString) {
        if (!dateString) return '-';
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) return '-';
            return date.toLocaleDateString('fr-FR', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch(e) {
            return '-';
        }
    };
    
    /**
     * هروب النصوص لعرضها بأمان في HTML
     */
    window.escapeHtml = function(text) {
        if (typeof text !== 'string') return text;
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    };
    
    /**
     * تأخير تنفيذ الدالة (Debounce)
     */
    window.debounce = function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };
    
    /**
     * الحصول على قيمة كوكي
     */
    window.getCookie = function(name) {
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
    };
    
    /**
     * عرض إشعارات صغيرة
     */
    window.showToast = function(message, type = 'info') {
        // إنشاء حاوية الإشعارات إذا لم تكن موجودة
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '1100';
            document.body.appendChild(toastContainer);
        }
        
        const toast = document.createElement('div');
        const bgClass = type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary';
        toast.className = `toast align-items-center text-white bg-${bgClass} border-0 mb-2`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${escapeHtml(message)}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Fermer"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // عرض الإشعار
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
            bsToast.show();
            
            // إزالة العنصر بعد الإخفاء
            toast.addEventListener('hidden.bs.toast', function() {
                toast.remove();
            });
        }
    };
    
    /**
     * تحديث عرض الجدول ديناميكيًا
     */
    window.updateTableWidth = function() {
        // هذه الدالة محفوظة للتوافق - تم إزالة الاعتماد على الشريط الجانبي
        // يمكن توسيعها لاحقًا إذا لزم الأمر
    };
    
})();
/**
✅ articles-table.js - إدارة جدول DataTables للسلع
ميزات:
Server-Side Processing مع دعم الفلاتر المتقدمة
Child Row شامل مع إحصائيات تعمل بشكل صحيح
تفعيل التبويبات عند اختيار مقال
معالجة أخطاء AJAX بشكل احترافي
*/
(function() {
'use strict';
window.articlesApp = window.articlesApp || {};
 window.articlesApp.currentArticle = null;
 window.articlesApp.dataTable = null;
 window.articlesApp.openChildRows = {};
 // ✅ تهيئة الجدول الرئيسية
 window.initArticlesTable = function() {
     const table = $('#articlesTable');
     if (!table.length) {
         console.warn('Table #articlesTable not found');
         return;
     }
     if ($.fn.DataTable.isDataTable(table)) {
         table.DataTable().destroy();
     } 
     window.articlesApp.dataTable = table.DataTable({
         processing: true,
         serverSide: true,
         deferRender: true,
         ajax: {
             url: window.articlesUrls?.apiData || '/articles/api/data/',
             type: 'GET',
             cache: false,
             data: function(d) { return buildAjaxData(d); },
             dataSrc: function(json) {
                 updateResultsCount(json);
                 hideLoadingIndicator();
                 if (json.error) {
                     console.error('API Error:', json.error);
                     showToast('Erreur: ' + json.error, 'error');
                     return [];
                 }
                 return json.data || [];
             },
             error: function(xhr, status, error) {
                 hideLoadingIndicator();
                 console.error('❌ AJAX Error:', { status: status, error: error });
                 showToast('Erreur de chargement', 'error');
                 updateResultsCount({ recordsFiltered: 0 });
             }
         },
         columns: [
             {
                 className: 'details-control',
                 orderable: false,
                 data: null,
                 defaultContent: '',
                 width: '30px'
             },
             { 
                 data: 'COD_ART',
                 className: 'text-nowrap',
                 render: function(data, type, row) {
                     if (type === 'display') {
                         return '<code class="article-code">' + escapeHtml(data || '-') + '</code>';
                     }
                     return data;
                 }
             },
             { 
                 data: 'LIB_ART',
                 render: function(data, type, row) {
                     if (type === 'display') {
                         const text = data || '-';
                         const displayText = text.length > 60 ? escapeHtml(text.substring(0, 60)) + '...' : escapeHtml(text);
                         return '<span title="' + escapeHtml(text) + '">' + displayText + '</span>';
                     }
                     return data;
                 }
             },
             { data: 'CLASS_COUT', className: 'text-center' },
             { 
                 data: 'DATE_CREAT',
                 className: 'text-center',
                 render: function(data, type, row) {
                     if (!data) return '-';
                     if (type === 'sort') return data;
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
             { data: 'EMPL', className: 'text-center' },
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
                     return '<span style="color:' + color + '">' + val.toFixed(1) + '</span>';
                 }
             },
             { data: 'LIB_UM', className: 'text-center' },
             { 
                 data: 'VAL_ART',
                 className: 'text-center',
                 render: function(data, type, row) {
                     if (!data) return '<span class="text-muted small">N/A</span>';
                     const map = {
                         '1': {text: '100%', class: 'val-art-1'},
                         '2': {text: '75%', class: 'val-art-2'},
                         '3': {text: '25%', class: 'val-art-3'},
                         '4': {text: '0%', class: 'val-art-4'}
                     };
                     const m = map[data.toString()];
                     if (m) {
                         return '<span class="val-art-badge ' + m.class + '">' + m.text + '</span>';
                     }
                     return '<span class="text-muted small">N/A</span>';
                 }
             },
             { 
                 data: 'libelle_nature',
                 className: 'text-center',
                 render: function(data, type, row) {
                     if (type === 'display') {
                         return data ? '<span class="badge bg-info text-dark">' + escapeHtml(data) + '</span>' : '—';
                     }
                     return row.nat_stock || '';
                 }
             },
             { 
                 data: 'DESIGNAT',
                 render: function(data, type, row) {
                     if (type === 'display') {
                         const text = data || '-';
                         const displayText = text.length > 50 ? escapeHtml(text.substring(0, 50)) + '...' : escapeHtml(text);
                         return '<span title="' + escapeHtml(text) + '">' + displayText + '</span>';
                     }
                     return data;
                 }
             }
             // ✅ تم حذف عمود Actions بالكامل
         ],
         language: {
             "processing": "Traitement en cours...",
             "search": "Rechercher : ",
             "lengthMenu": "Afficher _MENU_ elements",
             "info": "Affichage de _START_ a _END_ sur _TOTAL_ elements",
             "infoEmpty": "Aucun element a afficher",
             "infoFiltered": "(filtre de _MAX_ elements au total)",
             "loadingRecords": "Chargement...",
             "zeroRecords": "Aucun element correspondant trouve",
             "emptyTable": "Aucune donnee disponible",
             "paginate": { "first": "«", "previous": "‹", "next": "›", "last": "»" }
         },
         pageLength: 20,
         lengthMenu: [[20, 50, 100, -1], [20, 50, 100, "Tous"]],
         columnDefs: [
             { targets: 'no-sort', orderable: false },
             { targets: [0], orderable: false, searchable: false },
             { targets: [1, 2, 11], responsivePriority: 1 },
             { targets: [7, 8], type: 'num' }
         ],
         createdRow: function(row, data, dataIndex) {
             if (!data) return;
             const classCout = data.CLASS_COUT || '';
             const isDeclasse = String(classCout).trim().startsWith('029');
             // ✅ استخدام CSS class بدلاً من inline styles للسطر hachuré
             if (isDeclasse) {
                 $(row).addClass('declasse-row');
             }
             // ✅ النقر على الصف لتحديد المقال وتفعيل التبويبات
             $(row).on('click', function(e) {
                 if ($(e.target).closest('.action-btn, .btn-group, a, .details-control').length) {
                     e.stopPropagation();
                     return;
                 }
                 const $row = $(this);
                 const isSelected = $row.toggleClass('selected').hasClass('selected');
                 if (isSelected) {
                     window.articlesApp.currentArticle = data;
                     enableSecondaryTabs();
                     showToast('Article sélectionné: ' + data.COD_ART, 'info');
                 } else {
                     window.articlesApp.currentArticle = null;
                     disableSecondaryTabs();
                 }
             });
             $(row).find('[title]').tooltip({ trigger: 'hover', placement: 'top' });
         },
         drawCallback: function(settings) {
             initializeRowTooltips();
         },
         preDrawCallback: function(settings) {
             showLoadingIndicator();
         }
     });
     // ✅ إضافة حدث النقر على details-control لفتح Child Row
     $('#articlesTable tbody').on('click', 'td.details-control', function(e) {
         e.stopPropagation();
         const tr = $(this).closest('tr');
         const row = window.articlesApp.dataTable.row(tr);
         const data = row.data();
         if (!data) return;
         const codArt = data.COD_ART;
         if (row.child.isShown()) {
             row.child.hide();
             tr.removeClass('shown');
             delete window.articlesApp.openChildRows[codArt];
         } else {
             row.child(formatChildRow(data)).show();
             tr.addClass('shown');
             window.articlesApp.openChildRows[codArt] = true;
             // تحديد المقال وتفعيل التبويبات
             window.articlesApp.currentArticle = data;
             enableSecondaryTabs();
             // تحميل الإحصائيات الافتراضية
             setTimeout(function() {
                 loadChildStats(codArt, 'achat');
             }, 100);
             showToast('Article sélectionné: ' + codArt, 'info');
         }
     });
     bindFilterEvents();
 };
 // ✅ بناء معلمات AJAX للفلاتر
 function buildAjaxData(d) {
     function addSearchCondition(fieldName, inputValue, operatorSelector) {
         const val = inputValue ? inputValue.trim() : '';
         if (!val) return;
         const operatorEl = document.querySelector(operatorSelector);
         const operator = operatorEl && operatorEl.value ? operatorEl.value : 'contains';
         const likeValue = buildLikeCondition(val, operator);
         if (likeValue) {
             d[fieldName + '_op'] = operator;
             d[fieldName] = likeValue;
         }
     }
     const codArtInput = document.querySelector('input[name="cod_art"]');
     const codArtVal = codArtInput ? codArtInput.value : '';
     if (codArtVal && codArtVal.trim()) {
         addSearchCondition('cod_art', codArtVal, 'select[data-target="cod_art"]');
     }
     const libArtInput = document.querySelector('input[name="lib_art"]');
     const libArtVal = libArtInput ? libArtInput.value : '';
     if (libArtVal && libArtVal.trim()) {
         addSearchCondition('lib_art', libArtVal, 'select[data-target="lib_art"]');
     }
     const fields = ['class_cout', 'lib_um', 'empl', 'qte_min', 'qte_max', 
                    'pu_min', 'pu_max', 'val_art', 'nat_stock',
                    'date_min', 'date_max', 'dernier_mv_min', 'dernier_mv_max'];
     fields.forEach(function(field) {
         const el = document.querySelector('[name="' + field + '"]');
         if (el && el.value && el.value.trim()) {
             d[field] = el.value.trim();
         }
     });
     return d;
 }
 function buildLikeCondition(value, operator) {
     const clean = value.replace(/[%_\[\]]/g, '');
     if (operator === 'starts') return clean + '%';
     if (operator === 'ends') return '%' + clean;
     if (operator === 'exact') return clean;
     return '%' + clean + '%';
 }
 function updateResultsCount(json) {
     const countEl = document.getElementById('resultsCount');
     if (countEl && json.recordsFiltered !== undefined) {
         countEl.textContent = json.recordsFiltered.toLocaleString('fr-FR') + ' article(s) trouve(s)';
     }
 }
 function showLoadingIndicator() {
     const indicator = document.getElementById('loadingIndicator');
     if (indicator) indicator.style.display = 'inline';
 }
 function hideLoadingIndicator() {
     const indicator = document.getElementById('loadingIndicator');
     if (indicator) indicator.style.display = 'none';
 }
 function enableSecondaryTabs() {
     // ✅ إضافة codification-tab
     const tabs = ['#stats-tab', '#caract-tab', '#codification-tab', '#ai-tab', '#related-tab'];
     tabs.forEach(function(tabId) {
         const tab = document.querySelector(tabId);
         if (tab) {
             tab.disabled = false;
             tab.classList.remove('disabled');
         }
     });
 }
 function disableSecondaryTabs() {
     // ✅ إضافة codification-tab
     const tabs = ['#stats-tab', '#caract-tab', '#codification-tab', '#ai-tab', '#related-tab'];
     tabs.forEach(function(tabId) {
         const tab = document.querySelector(tabId);
         if (tab) {
             tab.disabled = true;
             tab.classList.add('disabled');
         }
     });
 }
 function bindFilterEvents() {
     const applyBtn = document.getElementById('applyFiltersBtn');
     if (applyBtn) {
         applyBtn.addEventListener('click', function() {
             if (window.articlesApp.dataTable) {
                 window.articlesApp.dataTable.ajax.reload();
                 showToast('Filtres appliques', 'success');
             }
         });
     }
     const resetBtn = document.getElementById('resetFiltersBtn');
     if (resetBtn) {
         resetBtn.addEventListener('click', function() {
             const form = document.getElementById('advancedFiltersForm');
             if (form) form.reset();
             if (window.articlesApp.dataTable) {
                 window.articlesApp.dataTable.ajax.reload();
                 showToast('Filtres reinitialises', 'info');
             }
         });
     }
 }
 function initializeRowTooltips() {
     if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
         document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function(el) {
             new bootstrap.Tooltip(el);
         });
     }
 }
 // ✅ دوال مساعدة
 window.formatDate = function(dateString) {
     if (!dateString) return '-';
     try {
         const date = new Date(dateString);
         if (isNaN(date.getTime())) return '-';
         return date.toLocaleDateString('fr-FR', { year: 'numeric', month: 'short', day: 'numeric' });
     } catch(e) {
         return '-';
     }
 };
 window.escapeHtml = function(text) {
     if (typeof text !== 'string') return text;
     const div = document.createElement('div');
     div.textContent = text;
     return div.innerHTML;
 };
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
 window.showToast = function(message, type) {
     if (type === undefined) type = 'info';
     let toastContainer = document.getElementById('toastContainer');
     if (!toastContainer) {
         toastContainer = document.createElement('div');
         toastContainer.id = 'toastContainer';
         toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
         toastContainer.style.zIndex = '1100';
         document.body.appendChild(toastContainer);
     }
     const toast = document.createElement('div');
     let bgClass = type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary';
     toast.className = 'toast align-items-center text-white bg-' + bgClass + ' border-0 mb-2';
     toast.innerHTML = '<div class="d-flex"><div class="toast-body">' + escapeHtml(message) + '</div>' +
         '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>';
     toastContainer.appendChild(toast);
     if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
         const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
         bsToast.show();
         toast.addEventListener('hidden.bs.toast', function() { toast.remove(); });
     }
 };
 window.openSmartAnalysis = function(codArt) {
     showToast('Analyse IA pour: ' + codArt, 'info');
 };
 // ============================================================================
 // ✅ تحميل إحصائيات Child Row
 // ============================================================================
 window.loadChildStats = function(codArt, tabType) {
     console.log('📊 loadChildStats:', codArt, tabType);
     const container = document.getElementById('childStatsContent-' + codArt);
     if (!container) {
         console.warn('⚠️ Container childStatsContent-' + codArt + ' non trouvé');
         return;
     }
     // عرض مؤشر التحميل
     container.innerHTML = `
         <div class="text-center py-4">
             <div class="spinner-border text-primary mb-2" role="status"></div>
             <p class="text-muted">Chargement des statistiques...</p>
         </div>
     `;
     const params = new URLSearchParams({
         tab_type: 'article',
         tab: tabType,
         cod_art: codArt,
         draw: 1,
         start: 0,
         length: 50
     });
     const apiUrl = window.articlesUrls?.apiStatistiques || '/articles/api/statistiques/';
     fetch(apiUrl + '?' + params, {
         headers: { 'X-Requested-With': 'XMLHttpRequest' }
     })
     .then(r => {
         if (!r.ok) throw new Error('HTTP ' + r.status);
         return r.json();
     })
     .then(data => {
         if (data.error) throw new Error(data.error);
         renderChildStatsTable(data, tabType, codArt);
         renderChildStatsChart(data, tabType, codArt);
     })
     .catch(err => {
         console.error('❌ Erreur:', err);
         container.innerHTML = `
             <div class="alert alert-danger m-3">
                 <i class="bi bi-exclamation-triangle me-2"></i>
                 Erreur: ${err.message}
             </div>
         `;
     });
 };
 function renderChildStatsTable(data, tabType, codArt) {
     const container = document.getElementById('childStatsContent-' + codArt);
     if (!container) return;
     if (!data || !Array.isArray(data.data)) {
         container.innerHTML = '<p class="text-muted text-center py-3">Aucune donnée disponible.</p>';
         return;
     }
     if (data.data.length === 0) {
         container.innerHTML = '<p class="text-muted text-center py-3">Aucune donnée pour cette période.</p>';
         return;
     }
     const columns = getChildStatsColumns(tabType);
     let html = '<div class="stats-table-container"><table class="table table-sm table-striped table-hover mb-0">';
     html += '<thead class="table-dark"><tr>';
     columns.forEach(col => {
         html += '<th>' + col.title + '</th>';
     });
     html += '</tr></thead><tbody>';
     data.data.slice(0, 20).forEach(row => {
         html += '<tr>';
         columns.forEach(col => {
             let value = row[col.data] || '—';
             if (col.render && typeof col.render === 'function') {
                 value = col.render(value, 'display', row);
             }
             html += '<td>' + value + '</td>';
         });
         html += '</tr>';
     });
     html += '</tbody></table></div>';
     if (data.data.length > 20) {
         html += '<p class="text-muted small text-center mt-2">Affichage de 20 sur ' + data.data.length + ' enregistrements</p>';
     }
     // إضافة الرسم البياني
     html += `
         <div class="card mt-3">
             <div class="card-header py-2">
                 <i class="bi bi-graph-up me-2"></i>Évolution Temporelle
             </div>
             <div class="card-body p-2">
                 <canvas id="childStatsChart-${codArt}" height="200"></canvas>
             </div>
         </div>
     `;
     container.innerHTML = html;
     // رسم الرسم البياني بعد إضافة HTML
     setTimeout(function() {
         renderChildStatsChart(data, tabType, codArt);
     }, 50);
 }
 function getChildStatsColumns(tabType) {
     const baseCols = [
         { data: 'type', title: 'Type' },
         { data: 'date_b', title: 'Date', render: function(d) { return d ? new Date(d).toLocaleDateString('fr-FR') : '-'; } },
         { data: 'numero_bon', title: 'N° Bon' },
         { data: 'lib_art', title: 'Libellé' },
         { data: 'qte_mvt', title: 'Quantité', render: function(d) { return d ? parseFloat(d).toFixed(2) : '0.00'; } },
         { data: 'libelle_nature', title: 'Nature Stock' }
     ];
     if (tabType === 'achat') {
         baseCols.push({ data: 'PU', title: 'P.U (TND)', render: function(d) { return d ? parseFloat(d).toFixed(3) : '0.000'; } });
     }
     return baseCols;
 }
 function renderChildStatsChart(data, tabType, codArt) {
     const canvasId = 'childStatsChart-' + codArt;
     const canvas = document.getElementById(canvasId);
     if (!canvas) return;
     const ctx = canvas.getContext('2d');
     if (!ctx) return;
     // تدمير الرسم البياني السابق إن وجد
     const chartKey = 'childChart_' + codArt;
     if (window[chartKey]) {
         try { window[chartKey].destroy(); } catch (e) {}
     }
     if (!data.months || data.months.length === 0) return;
     const colors = {
         'achat': { border: '#0d6efd', bg: 'rgba(13, 110, 253, 0.2)' },
         'consommation': { border: '#dc3545', bg: 'rgba(220, 53, 69, 0.2)' },
         'retours': { border: '#198754', bg: 'rgba(25, 135, 84, 0.2)' },
         'prestations': { border: '#6f42c1', bg: 'rgba(111, 66, 193, 0.2)' },
         'mouvements': { border: '#6c757d', bg: 'rgba(108, 117, 125, 0.2)' }
     };
     const color = colors[tabType] || colors['consommation'];
     window[chartKey] = new Chart(ctx, {
         type: 'line',
         data: {
             labels: data.months,
             datasets: [{
                 label: 'Évolution',
                 data: data.quantities || [],
                 borderColor: color.border,
                 backgroundColor: color.bg,
                 borderWidth: 2,
                 fill: true,
                 tension: 0.3
             }]
         },
         options: {
             responsive: true,
             maintainAspectRatio: false,
             plugins: { legend: { position: 'top' } },
             scales: {
                 y: { beginAtZero: true },
                 x: { title: { display: true, text: 'Période' } }
             }
         }
     });
 }
 // ✅ تحديث دالة formatChildRow - تصميم Child Row الكامل
 function formatChildRow(data) {
     const codArt = data.COD_ART || '';
     const libArt = data.LIB_ART || '';
     const designat = data.DESIGNAT || '';
     const empl = data.EMPL || '—';
     const qteStock = parseFloat(data.QTE_SURSTK || 0).toFixed(2);
     const pu = parseFloat(data.PU || 0).toFixed(3);
     const valeur = (qteStock * pu).toFixed(3);
     return `
     <div class="child-row-container">
         <!-- معلومات المقال -->
         <div class="child-row-header">
             <div style="flex: 1;">
                 <div class="child-row-title">
                     <i class="bi bi-box-seam me-2"></i>
                     <span class="article-code">${escapeHtml(codArt)}</span>
                     <span class="ms-2">${escapeHtml(libArt)}</span>
                 </div>
                 ${designat ? `<div class="child-row-designation mt-1"><em>${escapeHtml(designat)}</em></div>` : ''}
             </div>
         </div>
         <!-- ✅ Mini Stats - 4 بطاقات -->
         <div class="mini-stats-grid" id="mini-stats-${codArt}">
             <div class="mini-stat-card primary">
                 <div class="mini-stat-label">
                     <i class="bi bi-box-seam me-1"></i>Stock Actuel
                 </div>
                 <div class="mini-stat-value">${qteStock}</div>
                 <small class="text-muted">${escapeHtml(data.LIB_UM || '—')}</small>
             </div>
             <div class="mini-stat-card success">
                 <div class="mini-stat-label">
                     <i class="bi bi-currency-exchange me-1"></i>P.U (TND)
                 </div>
                 <div class="mini-stat-value">${pu}</div>
             </div>
             <div class="mini-stat-card warning">
                 <div class="mini-stat-label">
                     <i class="bi bi-tag me-1"></i>Valeur Stock
                 </div>
                 <div class="mini-stat-value">${valeur}</div>
                 <small class="text-muted">TND</small>
             </div>
             <div class="mini-stat-card info">
                 <div class="mini-stat-label">
                     <i class="bi bi-geo-alt me-1"></i>Emplacement
                 </div>
                 <div class="mini-stat-value" style="font-size: 1rem;">${escapeHtml(empl)}</div>
             </div>
         </div>
         <!-- ✅ Tabs الإحصائيات - تصميم Movement Types أفقي مختصر -->
         <div class="movement-types-container">
             <h6 class="text-muted small text-uppercase fw-bold mb-3">
                 <i class="bi bi-bar-chart me-1"></i>Type de Mouvement
             </h6>
             <div class="movement-types-horizontal">
                 <button class="movement-type-item active" data-stat="achat" onclick="switchChildStatsTab('${codArt}', 'achat')">
                     <div class="movement-number bg-primary">01</div>
                     <div class="movement-icon"><i class="bi bi-cart text-primary"></i></div>
                     <div class="movement-label"><strong>Achat</strong></div>
                 </button>
                 <button class="movement-type-item" data-stat="consommation" onclick="switchChildStatsTab('${codArt}', 'consommation')">
                     <div class="movement-number bg-danger">02</div>
                     <div class="movement-icon"><i class="bi bi-fire text-danger"></i></div>
                     <div class="movement-label"><strong>Conso</strong></div>
                 </button>
                 <button class="movement-type-item" data-stat="retours" onclick="switchChildStatsTab('${codArt}', 'retours')">
                     <div class="movement-number bg-success">03</div>
                     <div class="movement-icon"><i class="bi bi-arrow-return-left text-success"></i></div>
                     <div class="movement-label"><strong>Retours</strong></div>
                 </button>
                 <button class="movement-type-item" data-stat="prestations" onclick="switchChildStatsTab('${codArt}', 'prestations')">
                     <div class="movement-number bg-info">04</div>
                     <div class="movement-icon"><i class="bi bi-tools" style="color:#6f42c1"></i></div>
                     <div class="movement-label"><strong>Prestations</strong></div>
                 </button>
                 <button class="movement-type-item" data-stat="mouvements" onclick="switchChildStatsTab('${codArt}', 'mouvements')">
                     <div class="movement-number bg-secondary">05</div>
                     <div class="movement-icon"><i class="bi bi-diagram-3 text-secondary"></i></div>
                     <div class="movement-label"><strong>Tous</strong></div>
                 </button>
                 <button class="movement-type-item" data-stat="summary" onclick="loadArticleSummary('${codArt}')">
                     <div class="movement-number bg-warning">06</div>
                     <div class="movement-icon"><i class="bi bi-clipboard-data text-warning"></i></div>
                     <div class="movement-label"><strong>Résumé</strong></div>
                 </button>
             </div>
         </div>
         <!-- محتوى الإحصائيات -->
         <div class="tab-content mt-3" id="childStatsContent-${codArt}">
             <div class="text-center py-4">
                 <div class="spinner-border text-primary mb-2" role="status"></div>
                 <p class="text-muted">Chargement des statistiques...</p>
             </div>
         </div>
     </div>
     `;
 }
 // ✅ دالة جديدة: تبديل تبويبات Child Row
 window.switchChildStatsTab = function(codArt, tabType) {
     console.log('🔄 switchChildStatsTab:', codArt, tabType);
     // تحديث الأزرار النشطة داخل Child Row
     const container = document.getElementById('childStatsContent-' + codArt);
     if (container) {
         const parent = container.closest('.child-row-container');
         if (parent) {
             parent.querySelectorAll('.movement-type-item').forEach(btn => {
                 btn.classList.remove('active');
             });
             const activeBtn = parent.querySelector('.movement-type-item[data-stat="' + tabType + '"]');
             if (activeBtn) activeBtn.classList.add('active');
         }
     }
     // إذا كان Résumé
     if (tabType === 'summary') {
         loadArticleSummary(codArt);
         return;
     }
     // تحميل الإحصائيات
     if (!codArt) {
         showToast('Veuillez sélectionner un article', 'warning');
         return;
     }
     loadChildStats(codArt, tabType);
 };
})();
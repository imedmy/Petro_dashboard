/**
✅ articles-table-v2.js - إدارة جدول DataTables للسلع (النسخة المعدلة)
التعديلات في v2:
- بدون عمود Actions
- السطر مخدوش (line-through) للمقالات déclassés (CLASS_COUT يبدأ بـ 029)
- تبويب Codification (شرح الكود)
- تبويب Détails يظهر فقط عند اختيار مقال déclassé
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
             // ✅ السطر مخدوش (line-through) عبر الكلاس declasse-row (CSS في articles.html)
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
                 // ✅ تحديد واحد فقط في كل مرة
                 $row.siblings('.selected').removeClass('selected');
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
             if (window.articlesApp.openChildRows) delete window.articlesApp.openChildRows[codArt];
         } else {
             row.child(formatChildRow(data)).show();
             tr.addClass('shown');
             window.articlesApp.openChildRows = window.articlesApp.openChildRows || {};
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
 var SECONDARY_TABS = ['#stats-tab', '#caract-tab', '#codification-tab', '#ai-tab', '#related-tab'];
 function backToListIfNeeded(tabSelectors) {
     // ✅ إذا كان التبويب النشط سيُعطَّل نعود إلى تبويب Liste
     const active = document.querySelector('#articlesTabs .nav-link.active');
     if (active && tabSelectors.some(function(s) { return active.matches(s); })) {
         const listeTab = document.querySelector('#liste-tab');
         if (listeTab && typeof bootstrap !== 'undefined') bootstrap.Tab.getOrCreateInstance(listeTab).show();
     }
 }
 function enableSecondaryTabs() {
     SECONDARY_TABS.forEach(function(tabId) {
         const tab = document.querySelector(tabId);
         if (tab) {
             tab.disabled = false;
             tab.classList.remove('disabled');
         }
     });
     // ✅ تبويب Détails: يظهر فقط للمقال déclassé
     const declTab = document.querySelector('#declasse-tab');
     if (declTab) {
         if (window.isArticleDeclasse(window.articlesApp.currentArticle)) {
             declTab.disabled = false;
             declTab.classList.remove('disabled');
             declTab.parentElement.classList.remove('d-none');
         } else {
             backToListIfNeeded(['#declasse-tab']);
             declTab.disabled = true;
             declTab.classList.add('disabled');
             declTab.parentElement.classList.add('d-none');
         }
     }
 }
 function disableSecondaryTabs() {
     backToListIfNeeded(SECONDARY_TABS.concat(['#declasse-tab']));
     SECONDARY_TABS.forEach(function(tabId) {
         const tab = document.querySelector(tabId);
         if (tab) {
             tab.disabled = true;
             tab.classList.add('disabled');
         }
     });
     const declTab = document.querySelector('#declasse-tab');
     if (declTab) {
         declTab.disabled = true;
         declTab.classList.add('disabled');
         declTab.parentElement.classList.add('d-none');
     }
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
 // =====================================================================
 // ✅ NOUVEAU : Article déclassé (Classe Coût commençant par 029)
 // =====================================================================
 window.isArticleDeclasse = function(row) {
     return !!row && String(row.CLASS_COUT || '').trim().startsWith('029');
 };

 // =====================================================================
 // ✅ NOUVEAU : Onglet CODIFICATION - explication du code article
 // =====================================================================
 var CODIF_COLORS = ['#0d6efd', '#198754', '#fd7e14', '#6f42c1', '#d63384', '#20c997'];
 var CODIF_REST_COLOR = '#6c757d';

 function codifById(id) { return document.getElementById(id); }

 // يجمع كل العقد في قائمة مسطحة
 function codifFlatten(node, acc) {
     if (!node) return acc;
     acc.push(node);
     (node.children || []).forEach(function(c) { codifFlatten(c, acc); });
     return acc;
 }

 // المسار: العقد التي يكون full_code الخاص بها بادئة للكود
 function codifComputePath(codArt, tree) {
     if (!tree) return [];
     return codifFlatten(tree, [])
         .filter(function(n) { return n.full_code && codArt.indexOf(n.full_code) === 0; })
         .sort(function(a, b) { return a.full_code.length - b.full_code.length; });
 }

 // يبني مقاطع الكود: [{label, start, end, text, node}]
 function codifBuildSegments(codArt, path) {
     const segments = [];
     let pos = 0;
     if (path.length === 0) {
         const famLen = Math.min(3, codArt.length);
         segments.push({ label: 'Famille (3 premiers caractères)', start: 0, end: famLen, node: null });
         pos = famLen;
     } else {
         path.forEach(function(node, i) {
             const end = Math.min(node.full_code.length, codArt.length);
             if (end > pos) {
                 segments.push({
                     label: i === 0 ? 'Famille' : 'Sous-famille niveau ' + (i + 1),
                     start: pos, end: end, node: node
                 });
                 pos = end;
             }
         });
     }
     if (pos < codArt.length) {
         segments.push({ label: 'Reste du code (numéro d\'ordre / identifiant article)', start: pos, end: codArt.length, node: null, rest: true });
     }
     segments.forEach(function(s, i) {
         s.text = codArt.substring(s.start, s.end);
         s.color = s.rest ? CODIF_REST_COLOR : CODIF_COLORS[i % CODIF_COLORS.length];
     });
     return segments;
 }

 function codifRenderBoxes(codArt, segments) {
     let html = '<div class="codif-boxes">';
     for (let i = 0; i < codArt.length; i++) {
         const seg = segments.find(function(s) { return i >= s.start && i < s.end; });
         const color = seg ? seg.color : CODIF_REST_COLOR;
         html += '<div class="codif-char" style="--c:' + color + '">' +
                 '<span class="codif-char-val">' + escapeHtml(codArt.charAt(i)) + '</span>' +
                 '<span class="codif-char-pos">' + (i + 1) + '</span></div>';
     }
     return html + '</div>';
 }

 function codifRenderLegend(segments) {
     let html = '<div class="table-responsive"><table class="table table-sm align-middle codif-legend mb-0">' +
         '<thead><tr><th>Niveau</th><th class="text-center">Positions</th><th class="text-center">Segment</th><th>Code cumulé</th><th>Signification</th></tr></thead><tbody>';
     let cumul = '';
     segments.forEach(function(s) {
         cumul += s.text;
         const name = s.node ? escapeHtml(s.node.name || '') :
             (s.rest ? '<span class="text-muted">Partie propre à l\'article (non définie dans les familles)</span>'
                     : '<span class="text-muted">Famille non définie dans la codification</span>');
         html += '<tr>' +
             '<td><span class="codif-dot" style="background:' + s.color + '"></span>' + escapeHtml(s.label) + '</td>' +
             '<td class="text-center">' + (s.start + 1) + (s.end - s.start > 1 ? ' – ' + s.end : '') + '</td>' +
             '<td class="text-center"><code class="article-code">' + escapeHtml(s.text) + '</code></td>' +
             '<td><code>' + escapeHtml(cumul) + '</code></td>' +
             '<td>' + name + '</td></tr>';
     });
     return html + '</tbody></table></div>';
 }

 function codifRenderTree(node, pathCodes) {
     if (!node) return '';
     const onPath = pathCodes.indexOf(node.full_code) !== -1;
     const isLeafOfPath = onPath && pathCodes[pathCodes.length - 1] === node.full_code;
     let html = '<li><div class="codif-node' + (onPath ? ' on-path' : '') + (isLeafOfPath ? ' is-current' : '') + '">' +
         '<code>' + escapeHtml(node.full_code || '') + '</code> ' +
         '<span>' + escapeHtml(node.name || '') + '</span>' +
         (isLeafOfPath ? ' <i class="bi bi-geo-alt-fill ms-1"></i>' : '') + '</div>';
     if (node.children && node.children.length) {
         html += '<ul>' + node.children.map(function(c) { return codifRenderTree(c, pathCodes); }).join('') + '</ul>';
     }
     return html + '</li>';
 }

 window.loadArticleCodification = function(codArt) {
     if (!codArt) return;
     const loading = codifById('codifLoading');
     const content = codifById('codifContent');
     const empty = codifById('codifEmpty');
     if (empty) empty.style.display = 'none';
     if (content) content.style.display = 'none';
     if (loading) loading.classList.add('show');

     const article = window.articlesApp.currentArticle || {};
     const codeEl = codifById('codifArticleCode');
     const libEl = codifById('codifArticleLib');
     if (codeEl) codeEl.textContent = codArt;
     if (libEl) libEl.textContent = article.LIB_ART || '';

     function render(tree, errorMsg) {
         const path = codifComputePath(codArt, tree);
         const segments = codifBuildSegments(codArt, path);
         const pathCodes = path.map(function(n) { return n.full_code; });
         let html = '<h6 class="text-muted small text-uppercase fw-bold mb-2"><i class="bi bi-upc-scan me-1"></i>Décomposition du code (' + codArt.length + ' caractères)</h6>';
         html += codifRenderBoxes(codArt, segments);
         html += '<div class="card mt-3"><div class="card-body p-2">' + codifRenderLegend(segments) + '</div></div>';
         if (errorMsg) {
             html += '<div class="alert alert-warning mt-3 mb-0 small"><i class="bi bi-exclamation-triangle me-1"></i>' + escapeHtml(errorMsg) +
                     ' — décomposition par défaut affichée.</div>';
         }
         if (tree) {
             html += '<h6 class="text-muted small text-uppercase fw-bold mt-4 mb-2"><i class="bi bi-diagram-3 me-1"></i>Hiérarchie de la famille</h6>' +
                     '<div class="codif-tree"><ul>' + codifRenderTree(tree, pathCodes) + '</ul></div>';
         }
         if (content) { content.innerHTML = html; content.style.display = 'block'; }
         if (loading) loading.classList.remove('show');
     }

     fetch(getArticleFamilyByCodeUrl(codArt), { credentials: 'same-origin' })
         .then(function(r) { return r.ok ? r.json() : Promise.reject(new Error('HTTP ' + r.status)); })
         .then(function(json) { render(json.family || null, json.family ? null : (json.error || 'Famille non trouvée')); })
         .catch(function(err) {
             console.error('❌ Codification:', err);
             render(null, 'Erreur de chargement (' + err.message + ')');
         });
 };

 // =====================================================================
 // ✅ NOUVEAU : Onglet DÉTAILS (uniquement pour un article déclassé sélectionné)
 // =====================================================================
 function daysSince(dateString) {
     if (!dateString) return null;
     const d = new Date(dateString);
     if (isNaN(d.getTime())) return null;
     return Math.floor((Date.now() - d.getTime()) / 86400000);
 }

 function formatDuration(days) {
     if (days === null) return '—';
     if (days < 31) return days + ' jour(s)';
     if (days < 365) return Math.floor(days / 30) + ' mois';
     const y = Math.floor(days / 365);
     const m = Math.floor((days % 365) / 30);
     return y + ' an(s)' + (m ? ' ' + m + ' mois' : '');
 }

 window.loadDeclasseDetails = function(article) {
     const content = document.getElementById('declasseContent');
     const empty = document.getElementById('declasseEmpty');
     if (!content) return;
     if (!article || !window.isArticleDeclasse(article)) {
         content.style.display = 'none';
         if (empty) empty.style.display = 'block';
         return;
     }
     if (empty) empty.style.display = 'none';

     const qte = parseFloat(article.QTE_SURSTK || 0);
     const pu = parseFloat(article.PU || 0);
     const valeur = qte * pu;
     const joursMv = daysSince(article.DERNIER_MV);
     const joursCreat = daysSince(article.DATE_CREAT);
     const valMap = { '1': '100%', '2': '75%', '3': '25%', '4': '0%' };
     const valArt = article.VAL_ART ? (valMap[String(article.VAL_ART)] || 'N/A') : 'N/A';

     function item(icon, label, value, extra) {
         return '<div class="declasse-item"><div class="declasse-item-label"><i class="bi ' + icon + ' me-1"></i>' + label + '</div>' +
                '<div class="declasse-item-value">' + value + '</div>' + (extra ? '<small class="text-muted">' + extra + '</small>' : '') + '</div>';
     }

     let analyse;
     if (qte > 0) {
         analyse = '<div class="alert alert-warning mb-0"><i class="bi bi-exclamation-triangle me-2"></i>' +
             '<strong>Stock résiduel :</strong> ' + qte.toFixed(2) + ' ' + escapeHtml(article.LIB_UM || '') +
             ' valorisé à <strong>' + valeur.toFixed(3) + ' TND</strong>. Cet article déclassé immobilise encore du stock : ' +
             'une décision (réforme, cession, régularisation) est à envisager.</div>';
     } else {
         analyse = '<div class="alert alert-success mb-0"><i class="bi bi-check-circle me-2"></i>' +
             'Aucun stock résiduel pour cet article déclassé.</div>';
     }

     content.innerHTML =
         '<div class="declasse-banner">' +
             '<div><span class="badge bg-danger me-2">DÉCLASSÉ</span>' +
             '<span class="article-code declasse-strike">' + escapeHtml(article.COD_ART || '') + '</span> ' +
             '<span class="declasse-strike ms-2">' + escapeHtml(article.LIB_ART || '') + '</span></div>' +
             (article.DESIGNAT ? '<div class="text-muted small mt-1"><em>' + escapeHtml(article.DESIGNAT) + '</em></div>' : '') +
         '</div>' +
         '<div class="declasse-grid">' +
             item('bi-tag', 'Classe Coût', '<code>' + escapeHtml(String(article.CLASS_COUT || '—')) + '</code>', 'Préfixe 029 = article déclassé') +
             item('bi-calendar-plus', 'Date de création', formatDate(article.DATE_CREAT), joursCreat !== null ? 'Ancienneté : ' + formatDuration(joursCreat) : '') +
             item('bi-calendar-check', 'Dernier mouvement', formatDate(article.DERNIER_MV), joursMv !== null ? 'Inactif depuis : ' + formatDuration(joursMv) : '') +
             item('bi-geo-alt', 'Emplacement', escapeHtml(article.EMPL || '—')) +
             item('bi-box-seam', 'Quantité en stock', qte.toFixed(2), escapeHtml(article.LIB_UM || '')) +
             item('bi-currency-exchange', 'P.U (TND)', pu.toFixed(3)) +
             item('bi-cash-coin', 'Valeur du stock', valeur.toFixed(3), 'TND') +
             item('bi-percent', 'VAL_ART', valArt) +
             item('bi-diagram-2', 'Nature du stock', escapeHtml(article.libelle_nature || article.nat_stock || '—')) +
         '</div>' +
         '<div class="mt-3">' + analyse + '</div>' +
         '<div class="mt-3 d-flex gap-2 flex-wrap">' +
             '<button type="button" class="btn btn-sm btn-outline-primary" onclick="document.getElementById(\'codification-tab\').click()"><i class="bi bi-upc-scan me-1"></i>Voir la codification</button>' +
             '<button type="button" class="btn btn-sm btn-outline-secondary" onclick="document.getElementById(\'stats-tab\').click()"><i class="bi bi-bar-chart-line me-1"></i>Voir les statistiques</button>' +
         '</div>';
     content.style.display = 'block';
 };

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
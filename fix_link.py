#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_petro_links.py  —  إصلاح الروابط والقائمة الجانبية في مشروع Petro_dashboard
=================================================================================
الاستعمال (من جذر المشروع، حيث يوجد manage.py):

    git add -A && git commit -m "backup avant correctifs"      # نسخة احتياطية أولاً
    python fix_petro_links.py            # تطبيق الإصلاحات
    python fix_petro_links.py --dry-run  # عرض ما سيتغير فقط دون كتابة

السكربت آمن للتشغيل أكثر من مرة (idempotent).
"""
import os
import re
import shutil
import sys

DRY = "--dry-run" in sys.argv
LOG = []


# ----------------------------------------------------------------------------
# أدوات مساعدة
# ----------------------------------------------------------------------------
def read(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        raw = f.read()
    crlf = "\r\n" in raw
    return raw.replace("\r\n", "\n"), crlf


def write(path, text, crlf=False):
    if crlf:
        text = text.replace("\n", "\r\n")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def log(msg):
    LOG.append(msg)
    print(("[dry-run] " if DRY else "") + msg)


def patch(path, func, label):
    """يقرأ الملف، يطبّق func(text)->text ويكتب فقط إذا حصل تغيير."""
    if not os.path.exists(path):
        log(f"⚠️  introuvable : {path}")
        return
    text, crlf = read(path)
    new = func(text)
    if new != text:
        if not DRY:
            write(path, new, crlf)
        log(f"✅ {label}  ({path})")
    else:
        log(f"•  déjà OK : {path}")


def create(path, text, label):
    if os.path.exists(path):
        log(f"•  existe déjà : {path}")
        return
    if not DRY:
        write(path, text)
    log(f"✅ {label}  ({path})")


# ----------------------------------------------------------------------------
# تحقق من مكان التشغيل
# ----------------------------------------------------------------------------
if not os.path.exists("manage.py") or not os.path.isdir("templates"):
    sys.exit("❌ Lancez ce script depuis la racine du projet (là où se trouve manage.py).")

# ============================================================================
# 1) قوالب تطبيق articles المفقودة (الأسباب الرئيسية لفساد روابط القائمة)
#    views.py تطلب  articles/xxx.html  لكن الملفات موجودة في templates/core/
# ============================================================================
ART = "apps/articles/templates/articles"
COPIES = {
    "templates/core/caracteristiques.html": f"{ART}/caracteristiques.html",
    "templates/core/famille_codification.html": f"{ART}/famille_codification.html",
    "templates/core/statistiques.html": f"{ART}/statistiques.html",
    "templates/core/recherche_par_caracteristiques.html": f"{ART}/recherche.html",
    "templates/core/article_caracteristiques.html": f"{ART}/article_caracteristiques.html",
}

URL_RENAMES = [
    ("core:gestion_caracteristiques", "articles:gestion_caracteristiques"),
    ("core:api_caracteristiques", "articles:api_caracteristiques"),
    ("core:gestion_famille_codification", "articles:famille_codification"),
    ("core:api_article_families", "articles:api_article_families"),
    ("core:statistiques_ajax", "articles:statistiques_ajax_view"),
    ("core:export_tab_excel", "articles:api_export_stats_excel"),
    ("core:api_articles", "articles:api_articles"),
    ("core:stock_info", "articles:api_stock_info"),
    ("core:api_add_article_caract", "articles:api_add_article_caract"),
    ("core:api_delete_article_caract", "articles:api_delete_article_caract"),
    ("core:api_delete_article_image", "articles:api_delete_article_image"),
    # مسارات مكتوبة يدويًا داخل JavaScript
    ("/core/api/caracteristiques/", "/articles/api/caracteristiques/"),
    ("/core/article-caracteristiques/", "/articles/article-caracteristiques/"),
]


def fix_article_template(text):
    for a, b in URL_RENAMES:
        text = text.replace(a, b)
    # رفع الصور: /core/api/upload-image/<cod>/  ->  /articles/api/<cod>/upload-image/
    text = text.replace(
        "`/core/api/upload-image/${encodeURIComponent(selectedCodArt)}/`",
        "`/articles/api/${encodeURIComponent(selectedCodArt)}/upload-image/`",
    )
    return text


for src, dst in COPIES.items():
    if os.path.exists(dst):
        patch(dst, fix_article_template, "URLs corrigées")
        continue
    if not os.path.exists(src):
        log(f"⚠️  source introuvable : {src}")
        continue
    if not DRY:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
    log(f"✅ copié {src}  ->  {dst}")
    if not DRY:
        patch(dst, fix_article_template, "URLs corrigées")

create(
    f"{ART}/article_suivi_serial.html",
    """{% extends 'base.html' %}
{% block title %}{{ title }}{% endblock %}
{% block content %}
<div class="container-fluid mt-4">
  <h4><i class="bi bi-upc-scan"></i> {{ title }}</h4>
  <p class="text-muted">Suivi des numéros de série pour l'article <strong>{{ cod_art }}</strong> (à compléter).</p>
  <a href="{% url 'articles:list' %}" class="btn btn-secondary">Retour</a>
</div>
{% endblock %}
""",
    "template article_suivi_serial créé",
)

# ============================================================================
# 2) core/urls.py : views موجودة لكن غير مربوطة بأي رابط
# ============================================================================
NEW_ROUTES = """
    # --- routes ajoutées (vues existantes mais non routées) ---
    path('api/search-articles-by-caracts/', views.api_search_articles_by_caracts, name='api_search_articles_by_caracts'),
    path('lectures-index/', views.lecture_index_list, name='lecture_index_list'),
    path('lectures-index/create/', views.lecture_index_create, name='lecture_index_create'),
    path('consommations/', views.consommation_list, name='consommation_list'),
    path('consommations/create/', views.consommation_create, name='consommation_create'),
    path('lectures-pompe/', views.lecture_pompe_list, name='lecture_pompe_list'),
    path('lectures-pompe/create/', views.lecture_pompe_create, name='lecture_pompe_create'),
"""


def fix_core_urls(text):
    if "lecture_index_list" in text and "api_search_articles_by_caracts" in text:
        return text
    marker = "    # ===========================\n    # 8. Notifications"
    if marker in text:
        return text.replace(marker, NEW_ROUTES + "\n" + marker, 1)
    # احتياط: أضف قبل آخر ]
    idx = text.rstrip().rfind("]")
    return text[:idx] + NEW_ROUTES + text[idx:]


patch("core/urls.py", fix_core_urls, "routes ajoutées")

# ============================================================================
# 3) قوالب ما زالت تشير إلى core:dashboard (غير موجود)  ->  dashboard:index
# ============================================================================
for p in [
    "templates/core/forbidden.html",
    "templates/core/not_found.html",
    "templates/core/error.html",
    "templates/partials/header.html",
    "templates/partials/sidebar.html",
]:
    patch(p, lambda t: t.replace("core:dashboard", "dashboard:index"), "core:dashboard -> dashboard:index")

patch(
    "templates/core/lecture_jauge_form.html",
    lambda t: t.replace("core:lecture_pompe_list", "core:lecture_jauge_list"),
    "bouton Annuler -> lecture_jauge_list",
)

# ============================================================================
# 4) قوالب *_confirm_delete المفقودة (زر الحذف كان يعطي خطأ 500)
# ============================================================================
CONFIRM = """{% extends 'base.html' %}
{% block title %}Confirmer la suppression{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header bg-danger text-white"><h4>Confirmation de suppression</h4></div>
        <div class="card-body">
            <p>Êtes-vous sûr de vouloir supprimer : <strong>{{ __VAR__ }}</strong> ?</p>
            <form method="post">
                {% csrf_token %}
                <button type="submit" class="btn btn-danger">Oui, supprimer</button>
                <a href="{% url '__BACK__' %}" class="btn btn-secondary">Annuler</a>
            </form>
        </div>
    </div>
</div>
{% endblock %}
"""
for name, var, back in [
    ("personnel_confirm_delete", "personnel", "core:personnel_list"),
    ("tiers_confirm_delete", "tiers", "core:tiers_list"),
    ("tache_confirm_delete", "tache", "core:tache_list"),
]:
    create(f"templates/core/{name}.html", CONFIRM.replace("__VAR__", var).replace("__BACK__", back), "template de suppression créé")

# ============================================================================
# 5) apps/users/views.py : يطلب قوالب users/*.html وهي موجودة في core/
# ============================================================================
patch(
    "apps/users/views.py",
    lambda t: t.replace("'users/user_list.html'", "'core/users.html'")
    .replace("'users/user_form.html'", "'core/user_form.html'")
    .replace("'users/user_confirm_delete.html'", "'core/user_confirm_delete.html'")
    .replace("'users/permissions.html'", "'core/permissions.html'"),
    "apps/users -> templates core/",
)

# ============================================================================
# 6) projets : اسم ملف خاطئ  (.htm بدل .html)  + أخطاء وسوم Django
# ============================================================================
htm = "apps/projets/templates/projets/execution/realisation_detail.htm"
html = htm + "l"
if os.path.exists(htm) and not os.path.exists(html):
    if not DRY:
        os.rename(htm, html)
    log(f"✅ renommé {htm} -> .html")

patch(
    "apps/projets/templates/projets/execution/realisation_list.html",
    lambda t: t.replace("{% endif %.", "{% endif %}"),
    "balise {% endif %} corrigée",
)


def fix_tache_form(text):
    lines = text.split("\n")
    # الحالة: {% with %} داخل {% if tache %}  يُغلق بـ endif بدل endwith
    for i, l in enumerate(lines):
        if "{% with debut=tache.date_debut_prevue" in l:
            if any("{% endwith %}" in x for x in lines[i + 1:i + 12]):
                break  # déjà corrigé
            depth = 0
            for j in range(i + 1, min(i + 12, len(lines))):
                s = lines[j]
                depth += s.count("{% if ") - s.count("{% endif %}")
                if depth < 0:
                    lines[j] = s.replace("{% endif %}", "{% endwith %}", 1)
                    break
            break
    return "\n".join(lines)


patch("apps/projets/templates/projets/tache_form.html", fix_tache_form, "{% endwith %} corrigée")

patch(
    "templates/core/partials/caracteristique_tree.html",
    lambda t: t if "{% load carac_extras %}" in t else "{% load carac_extras %}\n" + t,
    "{% load carac_extras %} ajouté",
)

# ============================================================================
# 7) templates/base.html : القائمة الجانبية + تسجيل الخروج + تفعيل الرابط الحالي
# ============================================================================
GROUPS = [
    ("parametrageSubMenu", "bi-gear", "Paramétrage", [
        ("core:service_list", "bi-building", "Services"),
        ("core:personnel_list", "bi-people", "Personnel"),
        ("core:tiers_list", "bi-building", "Tiers"),
        ("core:types_mouvement", "bi-arrow-repeat", "Types de Mouvements"),
        ("core:nature_stock_list", "bi-archive", "Nature du Stock"),
        ("core:valeur_article_list", "bi-percent", "Valeur d'Article"),
        ("core:etape_dossier_list", "bi-folder-check", "Étape de Dossier"),
        ("core:db_monitor", "bi-server", "Surveillance DB"),
    ]),
    ("articlesSubMenu", "bi-box-seam", "Gestion des articles", [
        ("articles:list", "bi-inbox", "Articles en stock"),
        ("articles:gestion_caracteristiques", "bi-list-task", "Caractéristiques"),
        ("articles:famille_codification", "bi-upc", "Codification"),
        ("articles:article_caracteristiques_with_cod", "bi-tag", "Assigner caractéristiques"),
        ("articles:recherche", "bi-search", "Recherche"),
        ("articles:statistiques", "bi-bar-chart", "Statistiques"),
    ]),
    ("BCSubMenu", "bi-file-earmark-text", "Gestion des BC", [
        ("core:bons_commande", "bi-file-text", "Bons de Commande"),
        ("core:suivi_etapes", "bi-signpost-split", "Suivi des étapes"),
        ("core:etat_b1", "bi-clipboard-data", "État B1"),
        ("core:comparaison_commande_reception", "bi-arrow-left-right", "Commande / Réception"),
        ("core:avis_arrivee_list_page", "bi-truck", "Avis d'Arrivée"),
    ]),
    ("projetsSubMenu", "bi-briefcase", "Gestion des Projets", [
        ("projets:dashboard", "bi-speedometer2", "Tableau de bord projets"),
        ("projets:projet_list", "bi-folder2-open", "Liste des projets"),
        ("projets:projet_create", "bi-plus-circle", "Nouveau projet"),
    ]),
    ("tachesSubMenu", "bi-check2-square", "Gestion des Tâches", [
        ("core:planning_referentiel_list", "bi-journal-bookmark", "Planning"),
        ("core:tache_list", "bi-list-task", "Liste des Tâches"),
    ]),
    ("citerneSubMenu", "bi-fuel-pump", "Station Service", [
        ("core:citerne_list", "bi-list", "Citernes"),
        ("core:citerne_create", "bi-plus-circle", "Nouvelle citerne"),
        ("core:engin_list", "bi-truck-flatbed", "Engins"),
        ("core:equipement_list", "bi-tools", "Équipements"),
        ("core:lecture_jauge_list", "bi-speedometer", "Lectures jauge"),
        ("core:lecture_index_list", "bi-123", "Lectures index"),
        ("core:lecture_pompe_list", "bi-droplet", "Lectures pompe"),
        ("core:consommation_list", "bi-fuel-pump-diesel", "Consommations"),
        ("core:lectures_consommations", "bi-graph-up", "Lectures & consommations"),
    ]),
    ("usersSubMenu", "bi-people", "Utilisateurs", [
        ("core:user_list", "bi-person-lines-fill", "Liste"),
        ("core:user_create", "bi-person-plus", "Ajouter"),
        ("core:permissions", "bi-shield-lock", "Permissions"),
    ]),
]


def build_nav():
    out = '<nav class="sidebar-menu nav flex-column px-2">\n'
    out += """                <!-- Tableau de bord -->
                <a class="nav-link" href="{% url 'dashboard:index' %}">
                    <i class="bi bi-house-door"></i> <span>Tableau de bord</span>
                </a>
"""
    for gid, icon, label, items in GROUPS:
        out += f"""                <!-- {label} -->
                <a class="nav-link dropdown-toggle" data-bs-toggle="collapse" href="#{gid}" role="button" aria-expanded="false">
                    <i class="bi {icon}"></i> <span>{label}</span>
                </a>
                <div class="collapse" id="{gid}">
                    <nav class="nav flex-column">
"""
        for url, ic, text in items:
            out += f"""                        <a class="nav-link" href="{{% url '{url}' %}}"><i class="bi {ic}"></i> {text}</a>\n"""
        out += """                    </nav>
                </div>
"""
    return out + "            "


ACTIVE_JS = """
<script>
// ✅ تفعيل الرابط الحالي وفتح القائمة الفرعية تلقائياً (sidebar-autoactive)
(function () {
    var path = window.location.pathname;
    var best = null, bestLen = -1;
    document.querySelectorAll('#sidebarMenu a.nav-link[href]').forEach(function (a) {
        if (a.hasAttribute('data-bs-toggle')) return;
        var href = a.getAttribute('href');
        if (!href || href.charAt(0) !== '/') return;
        if ((path === href || path.indexOf(href) === 0) && href.length > bestLen) { best = a; bestLen = href.length; }
    });
    if (!best) return;
    best.classList.add('active');
    var box = best.closest('.collapse');
    if (box) {
        box.classList.add('show');
        var toggle = document.querySelector('#sidebarMenu a[href="#' + box.id + '"]');
        if (toggle) { toggle.classList.add('active'); toggle.setAttribute('aria-expanded', 'true'); }
    }
})();
</script>
"""

LOGOUT_FORM = """<form method="post" action="{% url 'accounts:logout' %}" class="d-inline m-0">
                            {% csrf_token %}
                            <button type="submit" class="btn btn-outline-light btn-sm" title="Déconnexion"><i class="bi bi-box-arrow-right"></i><span class="d-none d-md-inline"> Déconnexion</span></button>
                        </form>"""


def fix_base(text):
    # (أ) القائمة الجانبية
    if "projetsSubMenu" not in text:
        start = text.find('<nav class="sidebar-menu nav flex-column px-2">')
        end = text.find("</nav>\n        </div>\n    </aside>")
        if start == -1 or end == -1:
            log("⚠️  base.html : bloc sidebar introuvable, remplacez-le à la main")
        else:
            text = text[:start] + build_nav() + text[end:]
    # (ب) تسجيل الخروج: Django 5 يقبل POST فقط
    m = re.search(r"<a href=\"\{% url 'accounts:logout' %\}\".*?</a>", text, re.S)
    if m:
        text = text.replace(m.group(0), LOGOUT_FORM)
    # (ج) JS
    if "sidebar-autoactive" not in text:
        text = text.replace("{% block extra_js %}{% endblock %}", ACTIVE_JS + "{% block extra_js %}{% endblock %}", 1)
    return text


patch("templates/base.html", fix_base, "sidebar + logout POST + auto-active")

print("\n──────────────────────────────────────────────")
print("Terminé. Étapes suivantes :")
print("  1) python manage.py check")
print("  2) python manage.py runserver  puis tester chaque lien du menu")
print("  3) git diff   (pour relire les changements)")

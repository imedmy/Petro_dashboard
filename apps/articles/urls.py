from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    # =========================================
    # ✅ الصفحات الرئيسية
    # =========================================
    path('', views.articles_view, name='list'),
    path('caracteristiques/', views.gestion_caracteristiques, name='gestion_caracteristiques'),
    path('famille-codification/', views.famille_codification_view, name='famille_codification'),
    path('statistiques/', views.statistiques_view, name='statistiques'),
    path('recherche/', views.recherche_par_caracteristiques, name='recherche'),
    
    # صفحات إضافية للخصائص والترميز
    path('article-caracteristiques/', views.article_caracteristiques_with_cod, name='article_caracteristiques_with_cod'),
    path('article-caracteristiques/<str:cod_art>/', views.article_caracteristiques_with_cod, name='article_caracteristiques_with_cod_detail'),
    path('article-suivi-serial/<str:cod_art>/', views.article_suivi_serial, name='article_suivi_serial'),
    
    # =========================================
    # ✅ DataTables Server-Side
    # =========================================
    path('api/data/', views.api_articles_data, name='api_articles_data'),
    
    # =========================================
    # ✅ APIs الثابتة (يجب أن تأتي قبل المسارات الديناميكية)
    # =========================================
    
    # APIs البحث والقوائم
    path('api/articles/', views.api_articles, name='api_articles'),
    path('api/caracteristiques/', views.api_caracteristiques, name='api_caracteristiques'),
    path('api/families/', views.api_article_families, name='api_article_families'),
    
    # APIs المساعدة (Nature Stock, Stock Info)
    path('api/nature-stock/', views.api_nature_stock, name='api_nature_stock'),
    path('api/stock-info/', views.get_stock_info_view, name='api_stock_info'),
    
    # APIs الإحصائيات والتحليل
    path('api/statistiques/', views.statistiques_ajax_view, name='statistiques_ajax_view'),
    path('api/stats/', views.statistiques_ajax_view, name='api_statistiques'),
    path('api/export-excel/', views.export_stats_excel, name='export_stats_excel'),
    path('api/stats/export-excel/', views.export_tab_excel, name='api_export_stats_excel'),
    path('api/article-family-by-code/', views.api_article_family_by_code, name='api_article_family_by_code'),
    
    # APIs إدارة الخصائص والصور
    path('api/add-caract/', views.api_add_article_caract, name='api_add_article_caract'),
    path('api/delete-caract/', views.api_delete_article_caract, name='api_delete_article_caract'),
    path('api/delete-image/', views.api_delete_article_image, name='api_delete_article_image'),
    
    # APIs التحليل (Analysis)
    path('api/analysis/<uuid:workflow_id>/progress/', views.api_analysis_progress, name='api_analysis_progress'),
    path('api/analysis/cleanup/', views.api_cleanup_workflows, name='api_cleanup_workflows'),     
    
    # =========================================
    # ✅ APIs الديناميكية (تأخذ cod_art كمتغير)
    # يجب أن تكون في النهاية لتجنب تضارب المسارات
    # =========================================
    
    path('api/<str:cod_art>/related-stats/', views.api_article_related_stats, name='api_article_related_stats'),
    path('api/<str:cod_art>/ai-advice/', views.api_article_ai_advice, name='api_article_ai_advice'),
    path('api/<str:cod_art>/summary/', views.api_article_summary, name='api_article_summary'),
    path('api/<str:cod_art>/caract-values/', views.api_article_caract_values, name='api_article_caract_values'),
    path('api/<str:cod_art>/upload-image/', views.api_upload_article_image, name='api_upload_article_image'),
    
    # هذا المسار يجب أن يكون الأخير أو في نهاية مجموعة المسارات الديناميكية
    path('api/<str:cod_art>/', views.api_article_basic_info, name='api_article_basic_info'),
        # =========================================
    # ✅ تصدير نتائج الفلترة إلى Excel
    # =========================================
    path('export-articles-excel/', views.export_articles_excel, name='export_articles_excel'),
]
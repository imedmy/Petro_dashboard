# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # ===========================
    # 1. الصفحات الأساسية
    # ===========================
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('page/<str:page_name>/', views.page_view, name='page'),
    
    path('parametrage/types-mouvement/', views.types_mouvement_view, name='types_mouvement'),
    path('api/type-mouvement/create/', views.api_create_type_mouvement, name='api_create_type_mouvement'),
    path('api/type-mouvement/update/<int:pk>/', views.api_update_type_mouvement, name='api_update_type_mouvement'),
    path('api/type-mouvement/delete/<int:pk>/', views.api_delete_type_mouvement, name='api_delete_type_mouvement'),
    # ===========================
    # 2. إدارة السلع والمخزون
    # ===========================
    path('articles/', views.articles_view, name='articles'),
    path('api/article-family-by-code/', views.api_article_family_by_code, name='api_article_family_by_code'),
    path('codification/<str:codart>/', views.codification_view, name='codification'),
    path('statistiques/', views.statistiques_view, name='statistiques_articles'),
    path('statistiques/ajax/', views.statistiques_ajax_view, name='statistiques_ajax'),
    path('statistiques/stock-info/', views.get_stock_info_view, name='stock_info'),
    path('statistiques/export/', views.export_tab_excel, name='export_tab_excel'),
    # ---------------------------
    # إدارة خصائص السلع (جديدة)
    # ---------------------------
    # صفحة رئيسية لإدارة خصائص السلع (بدون اختيار مسبق)
    path('article-caracteristiques/',
         views.article_caracteristiques,
         name='article_caracteristiques'),

    # صفحة مع تحديد كود السلعة مباشرة من الرابط
    path('article-caracteristiques/<str:cod_art>/',
         views.article_caracteristiques,
         name='article_caracteristiques_with_cod'),
    # صفحةالبحث  عن السلعة  من خلال خصائصها
    path('recherche-par-caracteristiques/', views.recherche_par_caracteristiques, name='recherche_par_caracteristiques'),
    path('api/search-articles-by-caracts/', views.api_search_articles_by_caracts, name='api_search_articles_by_caracts'),
    # nature_stock 
    path('nature-stock/', views.nature_stock_list, name='nature_stock_list'),
    path('nature-stock/create/', views.nature_stock_create, name='nature_stock_create'),
    path('nature-stock/<int:pk>/update/', views.nature_stock_update, name='nature_stock_update'),
    path('nature-stock/<int:pk>/delete/', views.nature_stock_delete, name='nature_stock_delete'),
    
    # valeur_article
    path('valeur-article/', views.valeur_article_list, name='valeur_article_list'),
    path('valeur-article/create/', views.valeur_article_create, name='valeur_article_create'),
    path('valeur-article/<int:pk>/update/', views.valeur_article_update, name='valeur_article_update'),
    path('valeur-article/<int:pk>/delete/', views.valeur_article_delete, name='valeur_article_delete'),
    # etape_dossier
    path('etape-dossier/', views.etape_dossier_list, name='etape_dossier_list'),
    path('etape-dossier/create/', views.etape_dossier_create, name='etape_dossier_create'),
    path('etape-dossier/<int:pk>/update/', views.etape_dossier_update, name='etape_dossier_update'),
    path('etape-dossier/<int:pk>/delete/', views.etape_dossier_delete, name='etape_dossier_delete'),
    # API: بحث في السلع (لـ Lookup Panel)
    path('api/articles/', views.api_articles, name='api_articles'),

    # API: بحث في الخصائص التقنية
    path('api/caracteristiques/', views.api_caracteristiques, name='api_caracteristiques'),

    # API: جلب قيم الخصائص للمقال
    path('api/article-caract-values/<str:cod_art>/', views.api_article_caract_values, name='api_article_caract_values'),

    # API: إضافة قيمة خاصية لمقال
    path('api/add-article-caract/', views.api_add_article_caract, name='api_add_article_caract'),

    # API: حذف قيمة خاصية من مقال
    path('api/delete-article-caract/', views.api_delete_article_caract, name='api_delete_article_caract'),

    # API: رفع صورة لمقال
    path('api/upload-image/<str:cod_art>/', views.api_upload_article_image, name='api_upload_article_image'),

    # API: حذف صورة
    path('api/delete-image/', views.api_delete_article_image, name='api_delete_article_image'),
    
    # BC
    path('bons-commande/', views.bons_commande_view, name='bons_commande'),
    path('bons-commande/ajax/', views.bons_commande_ajax_view, name='bons_commande_ajax'),
    path('bons-commande/details/', views.bons_commande_details_view, name='bons_commande_details'),
    path('api/fournisseurs/', views.api_fournisseurs, name='api_fournisseurs'),
    
    # Suivie BC

    path('bons-commande/etapes/', views.suivi_etapes_view, name='suivi_etapes'),
    path('bons-commande/etapes/create/', views.suivi_etapes_create_view, name='suivi_etapes_create'),
    path('bons-commande/etapes/update/', views.suivi_etapes_update_view, name='suivi_etapes_update'),
    path('bons-commande/etapes/delete/', views.suivi_etapes_delete_view, name='suivi_etapes_delete'),
    path('api/etapes/', views.api_etapes_view, name='api_etapes'),
    path('bons-commande/etapes/detail/', views.suivi_etapes_detail_view, name='suivi_etapes_detail'),
    path('etape/details/', views.etape_details_view, name='etape_details'),
    path('etape/upload/', views.upload_piece_jointe_view, name='upload_piece_jointe'),
    path('etape/pieces/', views.liste_pieces_jointes_view, name='liste_pieces_jointes'),
    
    # عرض وتعديل Avis d'Arrivée
    path('avis-arrivee/list/', views.avis_arrivee_list, name='avis_arrivee_list'),
    path('avis-arrivee/details/', views.avis_arrivee_details, name='avis_arrivee_details'),
    path('avis-arrivee/create/', views.avis_arrivee_create, name='avis_arrivee_create'),
    path('avis-arrivee/update/', views.avis_arrivee_update, name='avis_arrivee_update'),
    path('avis-arrivee/delete/', views.avis_arrivee_delete, name='avis_arrivee_delete'),

    # تفاصيل السلع في إشعار الاستلام
    path('detail-avis/create/', views.detail_avis_create, name='detail_avis_create'),
    path('detail-avis/update/', views.detail_avis_update, name='detail_avis_update'),
    path('detail-avis/delete/', views.detail_avis_delete, name='detail_avis_delete'),
    
    path('avis-arrivee/<int:pk>/details/', views.avis_arrivee_detail_view, name='avis_arrivee_detail_page'),
    path('api/items/', views.api_items, name='api_items'),
    path('api/item-qte-um/', views.api_item_qte_um, name='api_item_qte_um'),
    path('avis-arrivee/detail/create/', views.detail_avis_create, name='detail_avis_create'),
    path('avis-arrivee/detail/update/', views.detail_avis_update, name='detail_avis_update'),
    path('avis-arrivee/detail/delete/', views.detail_avis_delete, name='detail_avis_delete'),
    
    path('api/ligne-by-item/', views.api_ligne_commande_by_item, name='api_ligne_by_item'),
    path('api/unite-libelle/', views.api_unite_libelle, name='api_unite_libelle'),
    
    # Suivie BC B1
    
    path('etat-b1/', views.etat_b1_view, name='etat_b1'),
    path('etat-b1/update/', views.etat_b1_update, name='etat_b1_update'),
    path('etat-b1/delete/', views.etat_b1_delete, name='etat_b1_delete'),
    path('api/items/', views.api_items_view, name='api_items'),
    path('api/item-details/', views.api_item_details_view, name='api_item_details'),
    path('api/item-qte-um/', views.api_item_qte_um, name='api_item_qte_um'),
    path('etat-b1/sync/', views.etat_b1_sync_view, name='etat_b1_sync'),
    
    # Suivie comparaison BC B1   
    
    path('comparaison/', views.comparaison_commande_reception, name='comparaison_commande_reception'),
    
    # Suivie avis_arrivee_standalone
   
    path('avis-arrivee/', views.avis_arrivee_list_view, name='avis_arrivee_list_page'),
    path('avis-arrivee/create/', views.avis_arrivee_create_view, name='avis_arrivee_create_page'),
    path('avis-arrivee/<int:pk>/edit/', views.avis_arrivee_update_view, name='avis_arrivee_update_page'),
    path('avis-arrivee/<int:pk>/delete/', views.avis_arrivee_delete_view, name='avis_arrivee_delete_page'),
    path('avis-arrivee/<int:pk>/details/', views.avis_arrivee_detail_view, name='avis_arrivee_detail_page'),
    path('avis-arrivee/<int:avis_id>/piece-jointe/upload/', views.upload_piece_jointe_avis, name='upload_piece_jointe_avis'),
    path('avis-arrivee/<int:avis_id>/piece-jointe/delete/<int:piece_id>/', views.delete_piece_jointe_avis, name='delete_piece_jointe_avis'),
    
    # ---------------------------
    # إدارة العائلات والترميز
    # ---------------------------
    path('caracteristiques/', views.gestion_caracteristiques, name='gestion_caracteristiques'),
    path('details-caracteristiques/', views.details_caracteristiques_view, name='details_caracteristiques'),
    path('famille-codification/', views.famille_codification_view, name='gestion_famille_codification'),
    path('api/article-families/', views.api_article_families, name='api_article_families'),

    # ===========================
    # 3. إدارة المستخدمين والصلاحيات
    # ===========================
    path('users/', views.user_list_view, name='user_list'),
    path('users/create/', views.user_create_view, name='user_create'),
    path('users/edit/<int:user_id>/', views.user_edit_view, name='user_edit'),
    path('users/delete/<int:user_id>/', views.user_delete_view, name='user_delete'),
    path('permissions/', views.permission_management_view, name='permissions'),
    path('api/pages/', views.api_pages, name='api_pages'),
    path('api/save_permission/', views.api_save_permission, name='api_save_permission'),
    path('api/delete_permission/<int:perm_id>/', views.api_delete_permission, name='api_delete_permission'),

    # ===========================
    # 4. صفحات أخرى
    # ===========================
    path('forbidden/', views.forbidden_view, name='forbidden'),
    path('db-monitor/', views.db_monitor_view, name='db_monitor'),
    path('db-monitor/kill/', views.kill_session_view, name='kill_session'),
    
]
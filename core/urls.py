# core/urls.py
from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'core'

urlpatterns = [
    # ===========================
    # 1. الصفحات العامة
    # ===========================
    path('page/<str:page_name>/', views.page_view, name='page'),
    path('forbidden/', views.forbidden_view, name='forbidden'),
    
    # ===========================
    # 2. إدارة المستخدمين والصلاحيات
    # ===========================
    path('users/', views.user_list_view, name='user_list'),
    path('users/create/', views.user_create_view, name='user_create'),
    path('users/edit/<int:user_id>/', views.user_edit_view, name='user_edit'),
    path('users/delete/<int:user_id>/', views.user_delete_view, name='user_delete'),
    path('permissions/', views.permission_management_view, name='permissions'),
    path('api/pages/', views.api_pages, name='api_pages'),
    path('api/save-permission/', views.api_save_permission, name='api_save_permission'),
    path('api/delete-permission/<int:perm_id>/', views.api_delete_permission, name='api_delete_permission'),
    
    # ===========================
    # 3. الإعدادات (Paramétrage)
    # ===========================
    # Services
    path('services/', views.service_list, name='service_list'),
    path('services/create/', views.service_create, name='service_create'),
    path('services/<int:pk>/edit/', views.service_update, name='service_update'),
    path('services/<int:pk>/delete/', views.service_delete, name='service_delete'),
    
    # Personnel
    path('personnel/', views.personnel_list_view, name='personnel_list'),
    path('personnel/create/', views.personnel_create_view, name='personnel_create'),
    path('personnel/<int:pk>/edit/', views.personnel_update_view, name='personnel_update'),
    path('personnel/<int:pk>/delete/', views.personnel_delete_view, name='personnel_delete'),
    
    # Tiers
    path('tiers/', views.tiers_list_view, name='tiers_list'),
    path('tiers/create/', views.tiers_create_view, name='tiers_create'),
    path('tiers/<int:pk>/edit/', views.tiers_update_view, name='tiers_update'),
    path('tiers/<int:pk>/delete/', views.tiers_delete_view, name='tiers_delete'),
    
    # Types de Mouvement
    path('types-mouvement/', views.types_mouvement_view, name='types_mouvement'),
    path('api/type-mouvement/create/', views.api_create_type_mouvement, name='api_create_type_mouvement'),
    path('api/type-mouvement/update/<int:pk>/', views.api_update_type_mouvement, name='api_update_type_mouvement'),
    path('api/type-mouvement/delete/<int:pk>/', views.api_delete_type_mouvement, name='api_delete_type_mouvement'),
    
    # Nature Stock
    path('nature-stock/', views.nature_stock_list, name='nature_stock_list'),
    path('nature-stock/create/', views.nature_stock_create, name='nature_stock_create'),
    path('nature-stock/<int:pk>/update/', views.nature_stock_update, name='nature_stock_update'),
    path('nature-stock/<int:pk>/delete/', views.nature_stock_delete, name='nature_stock_delete'),
    
    # Valeur Article
    path('valeur-article/', views.valeur_article_list, name='valeur_article_list'),
    path('valeur-article/create/', views.valeur_article_create, name='valeur_article_create'),
    path('valeur-article/<int:pk>/update/', views.valeur_article_update, name='valeur_article_update'),
    path('valeur-article/<int:pk>/delete/', views.valeur_article_delete, name='valeur_article_delete'),
    
    # Étape Dossier
    path('etape-dossier/', views.etape_dossier_list, name='etape_dossier_list'),
    path('etape-dossier/create/', views.etape_dossier_create, name='etape_dossier_create'),
    path('etape-dossier/<int:pk>/update/', views.etape_dossier_update, name='etape_dossier_update'),
    path('etape-dossier/<int:pk>/delete/', views.etape_dossier_delete, name='etape_dossier_delete'),
    
    # ===========================
    # 4. Bons de Commande
    # ===========================
    path('bons-commande/', views.bons_commande_view, name='bons_commande'),
    path('bons-commande/ajax/', views.bons_commande_ajax_view, name='bons_commande_ajax'),
    path('bons-commande/details/', views.bons_commande_details_view, name='bons_commande_details'),
    path('api/fournisseurs/', views.api_fournisseurs, name='api_fournisseurs'),
    path('api/commandes/', views.api_commandes, name='api_commandes'),
    
    # Suivi des étapes
    path('bons-commande/etapes/', views.suivi_etapes_view, name='suivi_etapes'),
    path('bons-commande/etapes/create/', views.suivi_etapes_create_view, name='suivi_etapes_create'),
    path('bons-commande/etapes/update/', views.suivi_etapes_update_view, name='suivi_etapes_update'),
    path('bons-commande/etapes/delete/', views.suivi_etapes_delete_view, name='suivi_etapes_delete'),
    path('api/etapes/', views.api_etapes_view, name='api_etapes'),
    path('bons-commande/etapes/detail/', views.suivi_etapes_detail_view, name='suivi_etapes_detail'),
    path('etape/details/', views.etape_details_view, name='etape_details'),
    path('etape/upload/', views.upload_piece_jointe_view, name='upload_piece_jointe'),
    path('etape/pieces/', views.liste_pieces_jointes_view, name='liste_pieces_jointes'),
    
    # État B1
    path('etat-b1/', views.etat_b1_view, name='etat_b1'),
    path('etat-b1/update/', views.etat_b1_update, name='etat_b1_update'),
    path('etat-b1/delete/', views.etat_b1_delete, name='etat_b1_delete'),
    path('etat-b1/sync/', views.etat_b1_sync_view, name='etat_b1_sync'),
    
    # Comparaison Commande/Réception
    path('comparaison/', views.comparaison_commande_reception, name='comparaison_commande_reception'),
    
    # APIs Ligne Commande
    path('api/items/', views.api_items_view, name='api_items'),
    path('api/item-details/', views.api_item_details_view, name='api_item_details'),
    path('api/item-qte-um/', views.api_item_qte_um, name='api_item_qte_um'),
    path('api/ligne-commande-by-item/', views.api_ligne_commande_by_item, name='api_ligne_commande_by_item'),
    path('api/unite-libelle/', views.api_unite_libelle, name='api_unite_libelle'),
    
    # ===========================
    # 5. Avis d'Arrivée
    # ===========================
    path('avis-arrivee/', views.avis_arrivee_list_view, name='avis_arrivee_list_page'),
    path('avis-arrivee/new/', views.avis_arrivee_create_view, name='avis_arrivee_create_page'),
    path('avis-arrivee/<int:pk>/edit/', views.avis_arrivee_update_view, name='avis_arrivee_update_page'),
    path('avis-arrivee/<int:pk>/delete/', views.avis_arrivee_delete_view, name='avis_arrivee_delete_page'),
    path('avis-arrivee/<int:pk>/details/', views.avis_arrivee_detail_view, name='avis_arrivee_detail_page'),
    path('avis-arrivee/<int:avis_id>/piece-jointe/upload/', views.upload_piece_jointe_avis, name='upload_piece_jointe_avis'),
    path('avis-arrivee/<int:avis_id>/piece-jointe/delete/<int:piece_id>/', views.delete_piece_jointe_avis, name='delete_piece_jointe_avis'),
    
    # APIs Avis d'Arrivée
    path('api/avis-arrivee/list/', views.avis_arrivee_list, name='avis_arrivee_list'),
    path('api/avis-arrivee/details/', views.avis_arrivee_details, name='avis_arrivee_details'),
    path('api/avis-arrivee/create/', views.avis_arrivee_create, name='avis_arrivee_create'),
    path('api/avis-arrivee/update/', views.avis_arrivee_update, name='avis_arrivee_update'),
    path('api/avis-arrivee/delete/', views.avis_arrivee_delete, name='avis_arrivee_delete'),
    path('api/detail-avis/create/', views.detail_avis_create, name='detail_avis_create'),
    path('api/detail-avis/update/', views.detail_avis_update, name='detail_avis_update'),
    path('api/detail-avis/delete/', views.detail_avis_delete, name='detail_avis_delete'),
    
    # ===========================
    # 6. Gestion des Tâches
    # ===========================
    path('taches/', views.tache_list_view, name='tache_list'),
    path('taches/create/', views.tache_create_view, name='tache_create'),
    path('taches/<int:pk>/edit/', views.tache_update_view, name='tache_update'),
    path('taches/<int:pk>/delete/', views.tache_delete_view, name='tache_delete'),
    path('taches/<int:pk>/details/', views.tache_detail_view, name='tache_detail'),
    path('planning/referentiel/', views.planning_referentiel_list_view, name='planning_referentiel_list'),
    path('planning/referentiel/create/', views.planning_referentiel_create_view, name='planning_referentiel_create'),
    path('planning/referentiel/<int:pk>/edit/', views.planning_referentiel_update_view, name='planning_referentiel_update'),
    path('planning/referentiel/<int:pk>/delete/', views.planning_referentiel_delete_view, name='planning_referentiel_delete'),
    
    # ===========================
    # 7. Station Service
    # ===========================
    path('citernes/', views.citerne_list, name='citerne_list'),
    path('citernes/create/', views.citerne_create, name='citerne_create'),
    path('citernes/<int:pk>/edit/', views.citerne_update, name='citerne_update'),
    path('citernes/<int:citerne_id>/barremage/', views.barremage_list_for_citerne, name='barremage_list_for_citerne'),
    
    path('engins/', views.engin_list, name='engin_list'),
    path('engins/create/', views.engin_create, name='engin_create'),
    path('engins/<int:pk>/edit/', views.engin_update, name='engin_update'),
    path('engins/<int:pk>/delete/', views.engin_delete, name='engin_delete'),
    
    path('equipements/', views.equipement_list, name='equipement_list'),
    path('equipements/create/', views.equipement_create, name='equipement_create'),
    path('equipements/<int:pk>/edit/', views.equipement_update, name='equipement_update'),
    path('equipements/<int:pk>/delete/', views.equipement_delete, name='equipement_delete'),
    
    path('lectures-jauge/', views.lecture_jauge_list, name='lecture_jauge_list'),
    path('lectures-jauge/create/', views.lecture_jauge_create, name='lecture_jauge_create'),
    path('station-service/lectures-consommations/', views.lectures_consommations_view, name='lectures_consommations'),

    # ===========================
    # 8. projets
    # ===========================
    
    

    # --- routes ajoutées (vues existantes mais non routées) ---
    path('api/search-articles-by-caracts/', views.api_search_articles_by_caracts, name='api_search_articles_by_caracts'),
    path('lectures-index/', views.lecture_index_list, name='lecture_index_list'),
    path('lectures-index/create/', views.lecture_index_create, name='lecture_index_create'),
    path('consommations/', views.consommation_list, name='consommation_list'),
    path('consommations/create/', views.consommation_create, name='consommation_create'),
    path('lectures-pompe/', views.lecture_pompe_list, name='lecture_pompe_list'),
    path('lectures-pompe/create/', views.lecture_pompe_create, name='lecture_pompe_create'),

    # ===========================
    # 8. Notifications
    # ===========================
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/notifications/<int:notification_id>/read/', views.mark_notification_as_read, name='mark_notification_as_read'),
    
    # ===========================
    # 9. Database Monitor
    # ===========================
    path('db-monitor/', views.db_monitor_view, name='db_monitor'),
    path('db-monitor/kill/', views.kill_session_view, name='kill_session'),
]
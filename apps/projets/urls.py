# =============================================================================
# ✅ URLs لتطبيق Gestion des Projets
# =============================================================================
from django.urls import path
from . import views
from . import execution_views, reference_views

app_name = 'projets'

urlpatterns = [
    # ============================================================
    # DASHBOARD
    # ============================================================
    path('dashboard/', views.dashboard_projets, name='dashboard'),

    # ============================================================
    # PROJETS (CRUD)
    # ============================================================
    path('', views.projet_list, name='projet_list'),
    path('new/', views.projet_create, name='projet_create'),
    path('<int:pk>/', views.projet_detail, name='projet_detail'),
    path('<int:pk>/edit/', views.projet_update, name='projet_update'),
    path('<int:pk>/delete/', views.projet_delete, name='projet_delete'),

    # ============================================================
    # LOTS (CRUD)
    # ============================================================
    path('projet/<int:projet_id>/lots/new/', views.lot_create, name='lot_create'),
    path('lots/<int:pk>/', views.lot_detail, name='lot_detail'),
    path('lots/<int:pk>/edit/', views.lot_update, name='lot_update'),

    # ============================================================
    # OUVRAGES (CRUD)
    # ============================================================
    path('lots/<int:lot_id>/ouvrages/new/', views.ouvrage_create, name='ouvrage_create'),
    path('ouvrages/<int:pk>/', views.ouvrage_detail, name='ouvrage_detail'),

    # ============================================================
    # TÂCHES PROJET (CRUD)
    # ============================================================
    path('ouvrages/<int:ouvrage_id>/taches/new/', views.tache_create, name='tache_create'),
    path('taches/<int:pk>/', views.tache_detail, name='tache_detail'),

    # ============================================================
    # ARTICLES DE BORDEREAU
    # ============================================================
    path('ouvrages/<int:ouvrage_id>/articles/new/', views.article_create, name='article_create'),

    # ============================================================
    # CONTRATS & AVENANTS
    # ============================================================
    path('projet/<int:projet_id>/contrat/', views.contrat_create, name='contrat_create'),
    path('projet/<int:projet_id>/avenants/new/', views.avenant_create, name='avenant_create'),

    # ============================================================
    # DÉCOMPTES
    # ============================================================
    path('projet/<int:projet_id>/decomptes/', views.decompte_list, name='decompte_list'),
    path('projet/<int:projet_id>/decomptes/new/', views.decompte_create, name='decompte_create'),

    # ============================================================
    # FACTURES EXTRA & GARANTIES
    # ============================================================
    path('projet/<int:projet_id>/factures-extra/new/', views.facture_extra_create, name='facture_extra_create'),
    path('projet/<int:projet_id>/garanties/new/', views.garantie_create, name='garantie_create'),

    # ============================================================
    # RÉUNIONS
    # ============================================================
    path('projet/<int:projet_id>/reunions/', views.reunion_list, name='reunion_list'),
    path('projet/<int:projet_id>/reunions/new/', views.reunion_create, name='reunion_create'),

    # ============================================================
    # CORRESPONDANCES
    # ============================================================
    path('projet/<int:projet_id>/correspondances/', views.correspondance_list, name='correspondance_list'),
    path('projet/<int:projet_id>/correspondances/new/', views.correspondance_create, name='correspondance_create'),

    # ============================================================
    # COMPTES RENDUS, SUSPENSIONS, LIVRABLES
    # ============================================================
    path('projet/<int:projet_id>/comptes-rendus/new/', views.compte_rendu_create, name='compte_rendu_create'),
    path('projet/<int:projet_id>/suspensions/new/', views.suspension_create, name='suspension_create'),
    path('projet/<int:projet_id>/livrables/new/', views.livrable_create, name='livrable_create'),

    # ============================================================
    # GED (GESTION ÉLECTRONIQUE DES DOCUMENTS)
    # ============================================================
    path('projet/<int:projet_id>/ged/', views.ged_list, name='ged_list'),
    path('projet/<int:projet_id>/ged/upload/', views.ged_upload, name='ged_upload'),
    path('ged/<int:pk>/', views.ged_document_detail, name='ged_document_detail'),

    # ============================================================
    # INTÉGRATIONS (RH & MATÉRIEL)
    # ============================================================
    path('projet/<int:projet_id>/rh/new/', views.affectation_rh_create, name='affectation_rh_create'),
    path('projet/<int:projet_id>/rh/', views.affectation_rh_list, name='affectation_rh_list'),
    path('projet/<int:projet_id>/materiel/new/', views.mobilisation_materiel_create, name='mobilisation_materiel_create'),
    path('projet/<int:projet_id>/materiel/', views.mobilisation_materiel_list, name='mobilisation_materiel_list'),

    # ============================================================
    # ✅ SUIVI EXÉCUTION (NOUVEAU - Réalisations)
    # ============================================================
    path('projet/<int:projet_id>/realisations/', execution_views.realisation_list, name='realisation_list'),
    path('projet/<int:projet_id>/realisations/new/', execution_views.realisation_create, name='realisation_create'),
    path('realisation/<int:pk>/', execution_views.realisation_detail, name='realisation_detail'),

    # Détails de réalisation
    path('realisation/<int:realisation_id>/detail/new/', execution_views.detail_realisation_create, name='detail_realisation_create'),

    # Événements logistiques
    path('realisation/<int:realisation_id>/evenement/new/', execution_views.evenement_logistique_create, name='evenement_create'),

    # Consommations
    path('realisation/<int:realisation_id>/consommation/new/', execution_views.consommation_create, name='consommation_create'),

    # Résultats
    path('realisation/<int:realisation_id>/resultat/new/', execution_views.resultat_create, name='resultat_create'),

    # Liens achat
    path('realisation/<int:realisation_id>/achat/new/', execution_views.lien_achat_create, name='lien_achat_create'),

    # ============================================================
    # ✅ RÉFÉRENCES (NOUVEAU - Procédures de référence)
    # ============================================================
    path('references/', reference_views.reference_list, name='reference_list'),
    path('references/new/', reference_views.reference_create, name='reference_create'),
    path('references/<int:pk>/', reference_views.reference_detail, name='reference_detail'),

    # ============================================================
    # APIs (JSON)
    # ============================================================
    path('<int:pk>/gantt-data/', views.projet_gantt_data, name='projet_gantt_data'),
    path('<int:pk>/stats-api/', views.projet_stats_api, name='projet_stats_api'),
    path('<int:pk>/kanban-data/', views.projet_kanban_data, name='projet_kanban_data'),
    path('recherche/', views.recherche_globale, name='recherche_globale'),
]
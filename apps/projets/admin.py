from django.contrib import admin
from .models import (
    # SECTION 1: Tables de référence
    TypeProjet, Unite, DomaineCompetence,
    # SECTION 2: Structure du projet
    Projet, Lot, Ouvrage, TacheProjet, ArticleBordereau,
    # SECTION 3: Gestion financière
    Contrat, Avenant, Decompte, FactureExtra, Garantie,
    # SECTION 4: Gestion administrative
    Reunion, Correspondance, CompteRendu, Suspension, Livrable,
    # SECTION 5: GED
    GedDocument, GedVersion,
    # SECTION 6: Workflow
    Workflow, WorkflowEtape, WorkflowInstance, WorkflowAction,
    # SECTION 7: Intégrations
    AffectationRh, MobilisationMateriel,
    # SECTION 8: Suivi de l'exécution (NOUVEAUX)
    ReferenceProcedure, Realisation, DetailsRealisation,
    EvenementLogistique, LienAchat, Consommation, Resultat,
)


# =============================================================================
# SECTION 1: TABLES DE RÉFÉRENCE
# =============================================================================
@admin.register(TypeProjet)
class TypeProjetAdmin(admin.ModelAdmin):
    list_display = ('code', 'libelle', 'categorie', 'actif')
    list_filter = ('actif', 'categorie')
    search_fields = ('code', 'libelle')
    list_per_page = 25


@admin.register(Unite)
class UniteAdmin(admin.ModelAdmin):
    list_display = ('code', 'libelle', 'symbole')
    search_fields = ('code', 'libelle', 'symbole')
    list_per_page = 50


@admin.register(DomaineCompetence)
class DomaineCompetenceAdmin(admin.ModelAdmin):
    list_display = ('code', 'libelle', 'categorie', 'couleur')
    list_filter = ('categorie',)
    search_fields = ('code', 'libelle')
    list_per_page = 25


# =============================================================================
# SECTION 2: STRUCTURE DU PROJET
# =============================================================================
class LotInline(admin.TabularInline):
    model = Lot
    extra = 0
    fields = ('numero', 'designation', 'montant', 'pourcentage', 'statut')


class OuvrageInline(admin.TabularInline):
    model = Ouvrage
    extra = 0
    fields = ('code', 'designation', 'quantite', 'unite', 'montant', 'statut')


class TacheProjetInline(admin.TabularInline):
    model = TacheProjet
    extra = 0
    fields = ('code', 'designation', 'statut', 'pourcentage_avancement', 'date_fin_prevue')


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('reference', 'nom', 'type_projet', 'maitre_ouvrage',
                    'statut', 'montant_final', 'pourcentage_avancement')
    list_filter = ('statut', 'type_projet', 'priorite', 'created_at')
    search_fields = ('reference', 'nom', 'lieu')
    list_per_page = 25
    date_hierarchy = 'created_at'
    inlines = [LotInline]


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = ('projet', 'numero', 'designation', 'montant', 'statut')
    list_filter = ('statut', 'projet')
    search_fields = ('designation', 'projet__reference')
    inlines = [OuvrageInline]


@admin.register(Ouvrage)
class OuvrageAdmin(admin.ModelAdmin):
    list_display = ('lot', 'code', 'designation', 'montant', 'statut')
    list_filter = ('statut', 'lot__projet')
    search_fields = ('code', 'designation')
    inlines = [TacheProjetInline]


@admin.register(TacheProjet)
class TacheProjetAdmin(admin.ModelAdmin):
    list_display = ('code', 'designation', 'ouvrage', 'statut',
                    'pourcentage_avancement', 'date_fin_prevue')
    list_filter = ('statut', 'priorite', 'ouvrage__lot__projet')
    search_fields = ('code', 'designation')


@admin.register(ArticleBordereau)
class ArticleBordereauAdmin(admin.ModelAdmin):
    list_display = ('code_bordereau', 'designation', 'ouvrage',
                    'quantite_prevue', 'prix_unitaire', 'montant_partiel')
    list_filter = ('type_article', 'ouvrage__lot__projet')
    search_fields = ('code_bordereau', 'designation')


# =============================================================================
# SECTION 3: GESTION FINANCIÈRE
# =============================================================================
@admin.register(Contrat)
class ContratAdmin(admin.ModelAdmin):
    list_display = ('numero', 'projet', 'type_contrat', 'montant_initial', 'date_signature')
    list_filter = ('type_contrat',)
    search_fields = ('numero', 'projet__reference', 'objet')


@admin.register(Avenant)
class AvenantAdmin(admin.ModelAdmin):
    list_display = ('numero', 'contrat', 'motif', 'montant_avenant',
                    'delai_supplementaire', 'statut')
    list_filter = ('statut', 'motif', 'contrat__projet')
    search_fields = ('numero', 'objet')


@admin.register(Decompte)
class DecompteAdmin(admin.ModelAdmin):
    list_display = ('numero', 'projet', 'type_decompte', 'date_decompte',
                    'montant_brut', 'montant_net', 'statut')
    list_filter = ('statut', 'type_decompte', 'projet')
    search_fields = ('projet__reference',)
    date_hierarchy = 'date_decompte'


@admin.register(FactureExtra)
class FactureExtraAdmin(admin.ModelAdmin):
    list_display = ('numero', 'projet', 'montant_ht', 'montant_ttc',
                    'statut', 'date_facture')
    list_filter = ('statut', 'projet')
    search_fields = ('numero', 'description')


@admin.register(Garantie)
class GarantieAdmin(admin.ModelAdmin):
    list_display = ('reference', 'projet', 'type_garantie', 'montant',
                    'date_emission', 'date_expiration', 'statut')
    list_filter = ('statut', 'type_garantie', 'projet')
    search_fields = ('reference', 'organisme_garant')


# =============================================================================
# SECTION 4: GESTION ADMINISTRATIVE
# =============================================================================
@admin.register(Reunion)
class ReunionAdmin(admin.ModelAdmin):
    list_display = ('numero', 'projet', 'type_reunion', 'objet', 'date_reunion', 'lieu')
    list_filter = ('type_reunion', 'projet')
    search_fields = ('objet', 'lieu')
    date_hierarchy = 'date_reunion'


@admin.register(Correspondance)
class CorrespondanceAdmin(admin.ModelAdmin):
    list_display = ('reference', 'projet', 'type_correspondance', 'direction',
                    'expediteur', 'destinataire', 'date_document')
    list_filter = ('direction', 'type_correspondance', 'projet')
    search_fields = ('reference', 'objet', 'expediteur', 'destinataire')
    date_hierarchy = 'date_document'


@admin.register(CompteRendu)
class CompteRenduAdmin(admin.ModelAdmin):
    list_display = ('numero', 'projet', 'type_cr', 'date_cr', 'objet')
    list_filter = ('type_cr', 'projet')
    search_fields = ('numero', 'objet')
    date_hierarchy = 'date_cr'


@admin.register(Suspension)
class SuspensionAdmin(admin.ModelAdmin):
    list_display = ('projet', 'motif', 'date_debut', 'date_fin_prevue', 'delai_accorde')
    list_filter = ('motif', 'projet')
    search_fields = ('motif_detail',)


@admin.register(Livrable)
class LivrableAdmin(admin.ModelAdmin):
    list_display = ('designation', 'projet', 'type_livrable', 'version',
                    'date_echeance', 'statut')
    list_filter = ('statut', 'type_livrable', 'projet')
    search_fields = ('designation',)
    date_hierarchy = 'date_echeance'


# =============================================================================
# SECTION 5: GED
# =============================================================================
@admin.register(GedDocument)
class GedDocumentAdmin(admin.ModelAdmin):
    list_display = ('titre', 'projet', 'categorie', 'version_courante',
                    'statut', 'created_at')
    list_filter = ('categorie', 'statut', 'projet')
    search_fields = ('titre', 'reference', 'description')


@admin.register(GedVersion)
class GedVersionAdmin(admin.ModelAdmin):
    list_display = ('document', 'numero_version', 'taille', 'uploaded_by', 'created_at')
    list_filter = ('document__projet',)
    search_fields = ('document__titre',)


# =============================================================================
# SECTION 6: WORKFLOW
# =============================================================================
@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'actif', 'created_at')
    list_filter = ('actif',)
    search_fields = ('code', 'nom')


@admin.register(WorkflowEtape)
class WorkflowEtapeAdmin(admin.ModelAdmin):
    list_display = ('workflow', 'ordre', 'nom', 'action', 'role_requis')
    list_filter = ('action', 'workflow')
    search_fields = ('nom',)


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ('workflow', 'projet', 'entity_type', 'entity_id',
                    'statut', 'date_debut')
    list_filter = ('statut', 'entity_type', 'projet')


@admin.register(WorkflowAction)
class WorkflowActionAdmin(admin.ModelAdmin):
    list_display = ('instance', 'etape', 'utilisateur', 'action_effectuee', 'date_action')
    list_filter = ('action_effectuee',)
    date_hierarchy = 'date_action'


# =============================================================================
# SECTION 7: INTÉGRATIONS
# =============================================================================
@admin.register(AffectationRh)
class AffectationRhAdmin(admin.ModelAdmin):
    list_display = ('personnel', 'projet', 'tache', 'role',
                    'date_debut', 'date_fin', 'pourcentage_temps')
    list_filter = ('projet',)
    search_fields = ('personnel__nom', 'role')


@admin.register(MobilisationMateriel)
class MobilisationMaterielAdmin(admin.ModelAdmin):
    list_display = ('projet', 'type_mobilisation', 'date_debut',
                    'date_fin', 'heures_utilisees', 'cout')
    list_filter = ('type_mobilisation', 'projet')


# =============================================================================
# SECTION 8: SUIVI DE L'EXÉCUTION (NOUVEAUX MODÈLES)
# =============================================================================

# --- 📚 ReferenceProcedure ---
@admin.register(ReferenceProcedure)
class ReferenceProcedureAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'domaine', 'actif', 'created_at')
    list_filter = ('domaine', 'actif')
    search_fields = ('code', 'nom', 'description_standard')
    list_per_page = 25
    fieldsets = (
        ('📌 Informations générales', {
            'fields': ('code', 'nom', 'domaine', 'actif')
        }),
        ('📝 Description & Critères', {
            'fields': ('description_standard', 'criteres_qualite'),
            'classes': ('collapse',)
        }),
        ('🔧 Ressources & Documents', {
            'fields': ('ressources_typiques', 'documents_reference', 'details_attendus'),
            'classes': ('collapse',)
        }),
    )


# --- Inlines pour Realisation ---
class DetailsRealisationInline(admin.TabularInline):
    model = DetailsRealisation
    extra = 0
    fields = ('type_detail', 'reference_procedure', 'description',
              'quantite', 'unite', 'prix_unitaire', 'cout_total',
              'fournisseur', 'document_joint')
    readonly_fields = ('cout_total',)
    autocomplete_fields = ('reference_procedure',)


class EvenementLogistiqueInline(admin.TabularInline):
    model = EvenementLogistique
    fk_name = 'realisation'
    extra = 0
    fields = ('type_evenement', 'date_evenement', 'description',
              'impact_delai_jours', 'engin', 'document_joint')


class LienAchatInline(admin.TabularInline):
    model = LienAchat
    fk_name = 'realisation'
    extra = 0
    fields = ('numero_bc', 'fournisseur', 'montant_prevu', 'montant_reel',
              'statut_livraison', 'date_livraison_prevue')


class ConsommationInline(admin.TabularInline):
    model = Consommation
    extra = 0
    fields = ('type_consommation', 'designation', 'quantite', 'unite',
              'cout_unitaire', 'cout_total', 'date_consommation')
    readonly_fields = ('cout_total',)


class ResultatInline(admin.TabularInline):
    model = Resultat
    extra = 0
    fields = ('type_resultat', 'titre', 'conforme', 'laboratoire',
              'date_resultat', 'document_joint')


# --- 🎯 Realisation (Master) ---
@admin.register(Realisation)
class RealisationAdmin(admin.ModelAdmin):
    list_display = ('nom', 'projet', 'lot', 'tache', 'statut',
                    'pourcentage_avancement', 'cout_total_display',
                    'date_debut_reelle')
    list_filter = ('statut', 'projet', 'responsable')
    search_fields = ('nom', 'description', 'projet__reference')
    list_per_page = 25
    date_hierarchy = 'date_debut_reelle'
    autocomplete_fields = ('projet', 'lot', 'ouvrage', 'tache', 'responsable')

    fieldsets = (
        ('📌 Informations générales', {
            'fields': ('nom', 'description', 'projet', 'lot', 'ouvrage', 'tache')
        }),
        ('📅 Dates & Avancement', {
            'fields': ('date_debut_reelle', 'date_fin_reelle',
                      'statut', 'pourcentage_avancement')
        }),
        ('👤 Responsabilité', {
            'fields': ('responsable',)
        }),
    )

    inlines = [
        DetailsRealisationInline,
        EvenementLogistiqueInline,
        LienAchatInline,
        ConsommationInline,
        ResultatInline,
    ]

    def cout_total_display(self, obj):
        total = obj.cout_total
        return f"{total:,.3f} TND" if total else "0.000 TND"
    cout_total_display.short_description = '💰 Coût total'


# --- 📝 DetailsRealisation ---
@admin.register(DetailsRealisation)
class DetailsRealisationAdmin(admin.ModelAdmin):
    list_display = ('description', 'type_detail', 'realisation',
                    'reference_procedure', 'quantite', 'cout_total')
    list_filter = ('type_detail', 'realisation__projet', 'reference_procedure')
    search_fields = ('description', 'fournisseur', 'observation')
    autocomplete_fields = ('realisation', 'reference_procedure')  # ✅ أزلنا engin و equipement
    raw_id_fields = ('engin', 'equipement')  # ✅ بديل أفضل: يعرض حقل ID مع زر بحث
    readonly_fields = ('cout_total', 'created_at')

# --- 🚚 EvenementLogistique ---
@admin.register(EvenementLogistique)
class EvenementLogistiqueAdmin(admin.ModelAdmin):
    list_display = ('type_evenement', 'projet', 'realisation',
                    'date_evenement', 'impact_delai_jours')
    list_filter = ('type_evenement', 'projet')
    search_fields = ('description', 'projet__reference')
    date_hierarchy = 'date_evenement'
    autocomplete_fields = ('projet', 'realisation', 'declare_par')  # ✅ أزلنا engin و equipement
    raw_id_fields = ('engin', 'equipement')  # ✅ بديل أفضل


# --- 🛒 LienAchat ---
@admin.register(LienAchat)
class LienAchatAdmin(admin.ModelAdmin):
    list_display = ('numero_bc', 'realisation', 'fournisseur',
                    'montant_prevu', 'statut_livraison', 'date_bc')
    list_filter = ('statut_livraison', 'realisation__projet')
    search_fields = ('numero_bc', 'fournisseur')
    autocomplete_fields = ('realisation', 'detail_realisation')


# --- ⛽ Consommation ---
@admin.register(Consommation)
class ConsommationAdmin(admin.ModelAdmin):
    list_display = ('designation', 'type_consommation', 'realisation',
                    'quantite', 'cout_total', 'date_consommation')
    list_filter = ('type_consommation', 'realisation__projet')
    search_fields = ('designation', 'cod_art')
    date_hierarchy = 'date_consommation'
    autocomplete_fields = ('realisation',)
    readonly_fields = ('cout_total',)


# --- 📊 Resultat ---
@admin.register(Resultat)
class ResultatAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type_resultat', 'realisation',
                    'conforme_display', 'laboratoire', 'date_resultat')
    list_filter = ('type_resultat', 'conforme', 'realisation__projet')
    search_fields = ('titre', 'description', 'laboratoire')
    date_hierarchy = 'date_resultat'
    autocomplete_fields = ('realisation', 'realise_par')

    def conforme_display(self, obj):
        return "✅ Conforme" if obj.conforme else "❌ Non conforme"
    conforme_display.short_description = 'Conformité'
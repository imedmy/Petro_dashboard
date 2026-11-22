from django.db import models
from django.conf import settings
from django.urls import reverse
from accounts.models import CustomUser
from core.models import Tiers, Personnel, Engin, Equipement
from django.core.validators import MaxValueValidator
from django.utils import timezone
from datetime import date, datetime, timedelta

# =============================================================================
# SECTION 1: TABLES DE RÉFÉRENCE
# =============================================================================

class TypeProjet(models.Model):
    """أنواع المشاريع (Industriel, Pétrolier, BTP, IT...)"""
    code = models.CharField("Code", max_length=20, unique=True)
    libelle = models.CharField("Libellé", max_length=100)
    categorie = models.CharField("Catégorie", max_length=100, blank=True)
    description = models.TextField("Description", blank=True)
    actif = models.BooleanField("Actif", default=True)

    class Meta:
        db_table = 'projets_type_projet'
        verbose_name = "Type de projet"
        verbose_name_plural = "Types de projet"
        ordering = ['libelle']

    def __str__(self):
        return self.libelle


class Unite(models.Model):
    """وحدات القياس (m, m², m³, kg, U, h, j...)"""
    code = models.CharField("Code", max_length=20, unique=True)
    libelle = models.CharField("Libellé", max_length=100)
    symbole = models.CharField("Symbole", max_length=10, blank=True)

    class Meta:
        db_table = 'projets_unite'
        verbose_name = "Unité"
        verbose_name_plural = "Unités"
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.libelle}"


class DomaineCompetence(models.Model):
    """مجالات الكفاءات (Forage, WO, HSE, Électricité...)"""
    code = models.CharField("Code", max_length=20, unique=True)
    libelle = models.CharField("Libellé", max_length=100)
    categorie = models.CharField("Catégorie", max_length=100, blank=True)
    description = models.TextField("Description", blank=True)
    couleur = models.CharField("Couleur", max_length=7, default='#6c757d')

    class Meta:
        db_table = 'projets_domaine_competence'
        verbose_name = "Domaine de compétence"
        verbose_name_plural = "Domaines de compétence"
        ordering = ['libelle']

    def __str__(self):
        return self.libelle


# =============================================================================
# SECTION 2: STRUCTURE DU PROJET
# =============================================================================

class Projet(models.Model):
    """المشروع / الصفقة - الجدول المركزي"""
    STATUTS = [
        ('PLANIFIE', 'Planifié'),
        ('EN_COURS', 'En cours'),
        ('SUSPENDU', 'Suspendu'),
        ('ACHEVE', 'Achevé'),
        ('RESILIE', 'Résilié'),
    ]
    PRIORITES = [
        ('BASSE', 'Basse'),
        ('MOYENNE', 'Moyenne'),
        ('HAUTE', 'Haute'),
        ('CRITIQUE', 'Critique'),
    ]

    # --- Informations générales ---
    reference = models.CharField("Référence", max_length=50, unique=True)
    nom = models.CharField("Nom du projet", max_length=200)
    description = models.TextField("Description", blank=True)
    type_projet = models.ForeignKey(
        TypeProjet, on_delete=models.PROTECT,
        related_name='projets', verbose_name="Type"
    )

    # --- الأطراف (FK vers core.Tiers) ---
    maitre_ouvrage = models.ForeignKey(
        Tiers, on_delete=models.PROTECT,
        related_name='projets_maitre_ouvrage',
        verbose_name="Maître d'ouvrage"
    )
    maitre_oeuvre = models.ForeignKey(
        Tiers, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='projets_maitre_oeuvre',
        verbose_name="Maître d'oeuvre"
    )
    entreprise_principale = models.ForeignKey(
        Tiers, on_delete=models.PROTECT,
        related_name='projets_entreprise',
        verbose_name="Entreprise principale"
    )

    # --- التواريخ والآجال ---
    date_debut_prevue = models.DateField("Date début prévue", null=True, blank=True)
    date_fin_prevue = models.DateField("Date fin prévue", null=True, blank=True)
    date_debut_reelle = models.DateField("Date début réelle", null=True, blank=True)
    date_fin_reelle = models.DateField("Date fin réelle", null=True, blank=True)
    delai_jours = models.IntegerField("Délai (jours)", default=0)

    # --- المالية ---
    montant_initial = models.DecimalField("Montant initial", max_digits=15, decimal_places=3, default=0)
    montant_avenants = models.DecimalField("Montant avenants", max_digits=15, decimal_places=3, default=0)
    montant_final = models.DecimalField("Montant final", max_digits=15, decimal_places=3, default=0)
    devise = models.CharField("Devise", max_length=3, default='TND')

    # --- الحالة ---
    statut = models.CharField("Statut", max_length=20, choices=STATUTS, default='PLANIFIE')
    priorite = models.CharField("Priorité", max_length=20, choices=PRIORITES, default='MOYENNE')
    pourcentage_avancement = models.DecimalField("Avancement (%)", max_digits=5, decimal_places=2, default=0)

    # --- الموقع ---
    lieu = models.CharField("Lieu", max_length=200, blank=True)
    coordonnees_gps = models.CharField("Coordonnées GPS", max_length=100, blank=True)

    # --- Meta ---
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.PROTECT,
        related_name='projets_created', verbose_name="Créé par"
    )
    chef_projet = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='projets_chef',
        verbose_name="Chef de projet"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    actif = models.BooleanField("Actif", default=True)

    class Meta:
        db_table = 'projets_projet'
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} - {self.nom}"

    def get_absolute_url(self):
        return reverse('projets:projet_detail', kwargs={'pk': self.pk})

    def calculer_montant_final(self):
        """إعادة حساب المبلغ النهائي بعد إضافة ملحق"""
        self.montant_final = self.montant_initial + self.montant_avenants
        self.save(update_fields=['montant_final'])
        return self.montant_final


class Lot(models.Model):
    """الحزمة - تقسيم المشروع إلى حزم متجانسة"""
    STATUTS = [
        ('NON_COMMENCE', 'Non commencé'),
        ('EN_COURS', 'En cours'),
        ('SUSPENDU', 'Suspendu'),
        ('ACHEVE', 'Achevé'),
    ]

    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='lots')
    numero = models.PositiveIntegerField("Numéro du lot")
    designation = models.CharField("Désignation", max_length=200)
    description = models.TextField("Description", blank=True)
    montant = models.DecimalField("Montant", max_digits=15, decimal_places=3, default=0)
    pourcentage = models.DecimalField("Pourcentage", max_digits=5, decimal_places=2, default=0)
    ordre_execution = models.PositiveIntegerField("Ordre d'exécution", default=0)
    date_debut = models.DateField("Date début", null=True, blank=True)
    date_fin = models.DateField("Date fin", null=True, blank=True)
    statut = models.CharField("Statut", max_length=20, choices=STATUTS, default='NON_COMMENCE')
    pourcentage_avancement = models.DecimalField("Avancement (%)", max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projets_lot'
        verbose_name = "Lot"
        verbose_name_plural = "Lots"
        unique_together = ['projet', 'numero']
        ordering = ['ordre_execution', 'numero']

    def __str__(self):
        return f"{self.projet.reference} / Lot {self.numero} - {self.designation}"

    def get_absolute_url(self):
        return reverse('projets:lot_detail', kwargs={'pk': self.pk})


class Ouvrage(models.Model):
    """المنشأة / الأشغال الرئيسية داخل كل Lot"""
    STATUTS = [
        ('NON_COMMENCE', 'Non commencé'),
        ('EN_COURS', 'En cours'),
        ('SUSPENDU', 'Suspendu'),
        ('ACHEVE', 'Achevé'),
    ]

    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name='ouvrages')
    code = models.CharField("Code", max_length=50)
    designation = models.CharField("Désignation", max_length=200)
    description = models.TextField("Description", blank=True)
    type_ouvrage = models.CharField("Type d'ouvrage", max_length=100, blank=True)
    quantite = models.DecimalField("Quantité", max_digits=12, decimal_places=3, default=0)
    unite = models.ForeignKey(Unite, on_delete=models.PROTECT, null=True, blank=True)
    prix_unitaire = models.DecimalField("Prix unitaire", max_digits=12, decimal_places=3, default=0)
    montant = models.DecimalField("Montant", max_digits=15, decimal_places=3, default=0)
    date_debut = models.DateField("Date début", null=True, blank=True)
    date_fin = models.DateField("Date fin", null=True, blank=True)
    statut = models.CharField("Statut", max_length=20, choices=STATUTS, default='NON_COMMENCE')
    pourcentage_avancement = models.DecimalField("Avancement (%)", max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projets_ouvrage'
        verbose_name = "Ouvrage"
        verbose_name_plural = "Ouvrages"
        unique_together = ['lot', 'code']
        ordering = ['code']

    def __str__(self):
        return f"{self.lot} / {self.code} - {self.designation}"

    def get_absolute_url(self):
        return reverse('projets:ouvrage_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        if not self.montant:
            self.montant = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)


class TacheProjet(models.Model):
    """مهام المشروع - مختلفة عن core.Tache (taches opérationnelles)"""
    STATUTS = [
        ('A_FAIRE', 'À faire'),
        ('EN_COURS', 'En cours'),
        ('EN_REVIEW', 'En révision'),
        ('BLOQUEE', 'Bloquée'),
        ('TERMINEE', 'Terminée'),
        ('ANNULEE', 'Annulée'),
    ]
    PRIORITES = [
        ('BASSE', 'Basse'),
        ('MOYENNE', 'Moyenne'),
        ('HAUTE', 'Haute'),
        ('URGENTE', 'Urgente'),
    ]

    ouvrage = models.ForeignKey(Ouvrage, on_delete=models.CASCADE, related_name='taches')
    tache_parente = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='sous_taches'
    )
    code = models.CharField("Code", max_length=50)
    designation = models.CharField("Désignation", max_length=200)
    description = models.TextField("Description", blank=True)

    # --- المسؤولية ---
    responsable = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='taches_projet_responsables',
        verbose_name="Responsable (utilisateur)"
    )
    personnel_responsable = models.ForeignKey(
        Personnel, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='taches_projet',
        verbose_name="Personnel responsable"
    )

    # --- التبعيات ---
    dependances = models.ManyToManyField(
        'self', symmetrical=False, blank=True,
        related_name='taches_dependantes'
    )

    # --- التواريخ ---
    date_debut_prevue = models.DateField("Date début prévue", null=True, blank=True)
    date_fin_prevue = models.DateField("Date fin prévue", null=True, blank=True)
    date_debut_reelle = models.DateField("Date début réelle", null=True, blank=True)
    date_fin_reelle = models.DateField("Date fin réelle", null=True, blank=True)

    # --- الحالة ---
    statut = models.CharField("Statut", max_length=20, choices=STATUTS, default='A_FAIRE')
    priorite = models.CharField("Priorité", max_length=20, choices=PRIORITES, default='MOYENNE')
    pourcentage_avancement = models.DecimalField("Avancement (%)", max_digits=5, decimal_places=2, default=0)

    # --- الساعات ---
    heures_prevues = models.DecimalField("Heures prévues", max_digits=8, decimal_places=2, default=0)
    heures_reelles = models.DecimalField("Heures réelles", max_digits=8, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projets_tache_projet'
        verbose_name = "Tâche projet"
        verbose_name_plural = "Tâches projet"
        unique_together = ['ouvrage', 'code']
        ordering = ['code']

    def __str__(self):
        return f"{self.ouvrage.code} / {self.code} - {self.designation}"

    def get_absolute_url(self):
        return reverse('projets:tache_detail', kwargs={'pk': self.pk})


class ArticleBordereau(models.Model):
    """بنود دفتر الأثمان - مختلفة عن core.Article (articles de stock)"""
    TYPES = [
        ('CONTRACTUEL', 'Contractuel'),
        ('AVENANT', 'Avenant'),
        ('EXTRA', 'Travaux extra'),
    ]

    ouvrage = models.ForeignKey(Ouvrage, on_delete=models.CASCADE, related_name='articles', null=True, blank=True)
    tache = models.ForeignKey(TacheProjet, on_delete=models.CASCADE, related_name='articles', null=True, blank=True)
    code_bordereau = models.CharField("Code bordereau", max_length=50)
    designation = models.CharField("Désignation", max_length=255)
    description = models.TextField("Description", blank=True)
    type_article = models.CharField("Type", max_length=20, choices=TYPES, default='CONTRACTUEL')
    unite = models.ForeignKey(Unite, on_delete=models.PROTECT)
    quantite_prevue = models.DecimalField("Quantité prévue", max_digits=12, decimal_places=3, default=0)
    quantite_realisee = models.DecimalField("Quantité réalisée", max_digits=12, decimal_places=3, default=0)
    quantite_contradictoire = models.DecimalField("Quantité contradictoire", max_digits=12, decimal_places=3, default=0)
    prix_unitaire = models.DecimalField("Prix unitaire", max_digits=12, decimal_places=3, default=0)
    montant_partiel = models.DecimalField("Montant partiel", max_digits=15, decimal_places=3, default=0)
    pourcentage_avancement = models.DecimalField("Avancement (%)", max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projets_article_bordereau'
        verbose_name = "Article de bordereau"
        verbose_name_plural = "Articles de bordereau"
        ordering = ['code_bordereau']

    def __str__(self):
        return f"{self.code_bordereau} - {self.designation}"

    def save(self, *args, **kwargs):
        self.montant_partiel = self.quantite_realisee * self.prix_unitaire
        super().save(*args, **kwargs)


# =============================================================================
# SECTION 3: GESTION FINANCIÈRE
# =============================================================================

class Contrat(models.Model):
    """العقد الأصلي للمشروع"""
    TYPES = [
        ('MARCHE_PUBLIC', 'Marché public'),
        ('MARCHE_PRIVE', 'Marché privé'),
        ('CONTRAT_PRIVE', 'Contrat privé'),
        ('BON_COMMANDE', 'Bon de commande'),
        ('CONVENTION', 'Convention'),
    ]

    projet = models.OneToOneField(Projet, on_delete=models.CASCADE, related_name='contrat')
    numero = models.CharField("Numéro", max_length=50, unique=True)
    type_contrat = models.CharField("Type", max_length=20, choices=TYPES)
    objet = models.TextField("Objet")
    montant_initial = models.DecimalField("Montant initial", max_digits=15, decimal_places=3)
    delai_jours = models.IntegerField("Délai (jours)", default=0)
    delai_mois = models.IntegerField("Délai (mois)", default=0)
    date_signature = models.DateField("Date de signature")
    date_notification = models.DateField("Date de notification", null=True, blank=True)
    conditions_paiement = models.TextField("Conditions de paiement", blank=True)
    conditions_revision = models.TextField("Conditions de révision", blank=True)
    retenue_garantie_pourcentage = models.DecimalField("Retenue de garantie (%)", max_digits=5, decimal_places=2, default=0)
    penalites_retard_pourcentage = models.DecimalField("Pénalités de retard (%/jour)", max_digits=5, decimal_places=4, default=0)
    document = models.FileField(upload_to='projets/contrats/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projets_contrat'
        verbose_name = "Contrat"
        verbose_name_plural = "Contrats"

    def __str__(self):
        return f"{self.numero} - {self.projet.nom}"


class Avenant(models.Model):
    """الملحق (تعديل العقد)"""
    STATUTS = [
        ('EN_PREPARATION', 'En préparation'),
        ('SIGNE', 'Signé'),
        ('APPROUVE', 'Approuvé'),
        ('REJETE', 'Rejeté'),
    ]
    MOTIFS = [
        ('QUANTITES_SUPP', 'Quantités supplémentaires'),
        ('TRAVAUX_NOUVEAUX', 'Travaux nouveaux'),
        ('PROLONGATION', 'Prolongation de délai'),
        ('REVISION_PRIX', 'Révision de prix'),
        ('MODIFICATION', 'Modification technique'),
    ]

    contrat = models.ForeignKey(Contrat, on_delete=models.CASCADE, related_name='avenants')
    numero = models.PositiveIntegerField("Numéro")
    objet = models.TextField("Objet")
    motif = models.CharField("Motif", max_length=30, choices=MOTIFS)
    motif_detail = models.TextField("Détail du motif", blank=True)
    montant_avenant = models.DecimalField("Montant avenant", max_digits=15, decimal_places=3, default=0)
    delai_supplementaire = models.IntegerField("Délai supplémentaire (jours)", default=0)
    pourcentage_revision = models.DecimalField("% du montant initial", max_digits=5, decimal_places=2, default=0)
    date_signature = models.DateField("Date de signature", null=True, blank=True)
    statut = models.CharField("Statut", max_length=20, choices=STATUTS, default='EN_PREPARATION')
    document = models.FileField(upload_to='projets/avenants/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projets_avenant'
        verbose_name = "Avenant"
        verbose_name_plural = "Avenants"
        unique_together = ['contrat', 'numero']
        ordering = ['numero']

    def __str__(self):
        return f"Avenant n°{self.numero} - {self.contrat.numero}"

    def save(self, *args, **kwargs):
        if self.contrat.montant_initial > 0:
            self.pourcentage_revision = (abs(self.montant_avenant) / self.contrat.montant_initial) * 100
        super().save(*args, **kwargs)
        if self.statut in ['SIGNE', 'APPROUVE']:
            self.contrat.projet.calculer_montant_final()


class Decompte(models.Model):
    """الحساب (مؤقت/نهائي)"""
    TYPES = [
        ('PROVISOIRE', 'Provisoire'),
        ('DEFINITIF', 'Définitif'),
        ('REVISION_PRIX', 'Révision de prix'),
    ]
    STATUTS = [
        ('PREPARE', 'Préparé'),
        ('SOUMIS', 'Soumis'),
        ('VALIDE', 'Validé'),
        ('PAYE', 'Payé'),
        ('REJETE', 'Rejeté'),
    ]

    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='decomptes')
    numero = models.PositiveIntegerField("Numéro")
    type_decompte = models.CharField("Type", max_length=20, choices=TYPES)
    date_decompte = models.DateField("Date")
    montant_brut = models.DecimalField("Montant brut", max_digits=15, decimal_places=3, default=0)
    retenue_garantie = models.DecimalField("Retenue garantie", max_digits=15, decimal_places=3, default=0)
    penalites = models.DecimalField("Pénalités", max_digits=15, decimal_places=3, default=0)
    tva_taux = models.DecimalField("TVA (%)", max_digits=5, decimal_places=2, default=19)
    tva_montant = models.DecimalField("TVA (montant)", max_digits=15, decimal_places=3, default=0)
    montant_net = models.DecimalField("Montant net", max_digits=15, decimal_places=3, default=0)
    statut = models.CharField("Statut", max_length=20, choices=STATUTS, default='PREPARE')
    observations = models.TextField("Observations", blank=True)
    document = models.FileField(upload_to='projets/decomptes/%Y/%m/', blank=True, null=True)
    valide_par = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='decomptes_valides')
    date_paiement = models.DateField("Date de paiement", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projets_decompte'
        verbose_name = "Décompte"
        verbose_name_plural = "Décomptes"
        unique_together = ['projet', 'numero']
        ordering = ['numero']

    def __str__(self):
        return f"Décompte n°{self.numero} - {self.projet.reference}"

    def calculer_montants(self):
        """حساب TVA والمبلغ الصافي"""
        base_ht = self.montant_brut - self.retenue_garantie - self.penalites
        self.tva_montant = base_ht * (self.tva_taux / 100)
        self.montant_net = base_ht + self.tva_montant
        self.save(update_fields=['tva_montant', 'montant_net'])


class FactureExtra(models.Model):
    """فواتير الأشغال الإضافية (خارج العقد الأصلي)"""
    STATUTS = [
        ('BROUILLON', 'Brouillon'),
        ('SOUMISE', 'Soumise'),
        ('APPROUVEE', 'Approuvée'),
        ('PAYEE', 'Payée'),
        ('REJETEE', 'Rejetée'),
    ]

    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='factures_extra')
    numero = models.CharField("Numéro", max_length=50)
    reference_os = models.CharField("Référence OS", max_length=100, blank=True)
    description = models.TextField("Description")
    justification = models.TextField("Justification", blank=True)
    montant_ht = models.DecimalField("Montant HT", max_digits=15, decimal_places=3, default=0)
    tva_taux = models.DecimalField("TVA (%)", max_digits=5, decimal_places=2, default=19)
    tva_montant = models.DecimalField("TVA (montant)", max_digits=15, decimal_places=3, default=0)
    montant_ttc = models.DecimalField("Montant TTC", max_digits=15, decimal_places=3, default=0)
    statut = models.CharField("Statut", max_length=20, choices=STATUTS, default='BROUILLON')
    date_facture = models.DateField("Date")
    approuvee_par = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='factures_extra_approuvees')
    document = models.FileField(upload_to='projets/factures_extra/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'projets_facture_extra'
        verbose_name = "Facture extra"
        verbose_name_plural = "Factures extra"

    def __str__(self):
        return f"Facture Extra {self.numero} - {self.projet.reference}"


class Garantie(models.Model):
    """الضمانات (بنكية / احتجازات)"""
    TYPES = [
        ('CAUTION_BANCAIRE', 'Caution bancaire'),
        ('RETENUE_DECOMPTE', 'Retenue sur décompte'),
        ('GARANTIE_BONNE_EXECUTION', 'Garantie de bonne exécution'),
        ('GARANTIE_RETENUE_GARANTIE', 'Garantie retenue de garantie'),
    ]
    STATUTS = [
        ('ACTIVE', 'Active'),
        ('MAINLEVEE', 'Mainlevée'),
        ('UTILISEE', 'Utilisée'),
        ('EXPIREE', 'Expirée'),
    ]

    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='garanties')
    type_garantie = models.CharField("Type", max_length=30, choices=TYPES)
    reference = models.CharField("Référence", max_length=100)
    organisme_garant = models.CharField("Organisme garant", max_length=200, blank=True)
    montant = models.DecimalField("Montant", max_digits=15, decimal_places=3)
    date_emission = models.DateField("Date d'émission")
    date_expiration = models.DateField("Date d'expiration")
    statut = models.CharField("Statut", max_length=20, choices=STATUTS, default='ACTIVE')
    document = models.FileField(upload_to='projets/garanties/%Y/%m/', blank=True, null=True)
    observations = models.TextField("Observations", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'projets_garantie'
        verbose_name = "Garantie"
        verbose_name_plural = "Garanties"

    def __str__(self):
        return f"{self.get_type_garantie_display()} - {self.reference}"


# =============================================================================
# SECTION 4: GESTION ADMINISTRATIVE
# =============================================================================

class Reunion(models.Model):
    """اجتماعات العمل"""
    TYPES = [
        ('CHANTIER', 'Réunion de chantier'),
        ('COORDINATION', 'Coordination'),
        ('AVANCEMENT', 'Avancement'),
        ('TECHNIQUE', 'Technique'),
        ('HSE', 'HSE'),
        ('AUTRE', 'Autre'),
    ]

    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='reunions')
    numero = models.PositiveIntegerField("Numéro")
    type_reunion = models.CharField("Type", max_length=20, choices=TYPES)
    objet = models.CharField("Objet", max_length=255)
    date_reunion = models.DateTimeField("Date")
    lieu = models.CharField("Lieu", max_length=200, blank=True)
    duree_heures = models.DecimalField("Durée (heures)", max_digits=4, decimal_places=1, default=1)
    animateur = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reunions_animees')
    participants = models.JSONField("Participants", default=list, blank=True)
    ordre_jour = models.TextField("Ordre du jour", blank=True)
    decisions = models.TextField("Décisions", blank=True)
    document = models.FileField(upload_to='projets/reunions/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'projets_reunion'
        verbose_name = "Réunion"
        verbose_name_plural = "Réunions"
        unique_together = ['projet', 'numero']
        ordering = ['-date_reunion']

    def __str__(self):
        return f"Réunion n°{self.numero} - {self.projet.reference}"


class Correspondance(models.Model):
    """المراسلات (واردة/صادرة)"""
    TYPES = [
        ('LETTRE', 'Lettre'),
        ('EMAIL', 'Email'),
        ('FAX', 'Fax'),
        ('NOTE_SERVICE', 'Note de service'),
        ('COURRIER', 'Courrier officiel'),
    ]
    DIRECTIONS = [
        ('ENTRANT', 'Entrant'),
        ('SORTANT', 'Sortant'),
    ]

    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='correspondances')
    reference = models.CharField("Référence", max_length=100)
    type_correspondance = models.CharField("Type", max_length=20, choices=TYPES)
    direction = models.CharField("Direction", max_length=10, choices=DIRECTIONS)
    date_document = models.DateField("Date du document")
    date_reception_envoi = models.DateField("Date réception/envoi")
    expediteur = models.CharField("Expéditeur", max_length=200)
    destinataire = models.CharField("Destinataire", max_length=200)
    objet = models.CharField("Objet", max_length=255)
    contenu = models.TextField("Contenu", blank=True)
    correspondance_parente = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='reponses')
    document = models.FileField(upload_to='projets/correspondances/%Y/%m/', blank=True, null=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='correspondances_created')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'projets_correspondance'
        verbose_name = "Correspondance"
        verbose_name_plural = "Correspondances"
        ordering = ['-date_document']

    def __str__(self):
        return f"{self.reference} - {self.objet}"


class CompteRendu(models.Model):
    """محاضر الاجتماعات والتقارير"""
    TYPES = [
        ('CR_REUNION', 'CR de réunion'),
        ('RAPPORT_JOURNALIER', 'Rapport journalier'),
        ('RAPPORT_HEBDOMADAIRE', 'Rapport hebdomadaire'),
        ('RAPPORT_MENSUEL', 'Rapport mensuel'),
        ('RAPPORT_SPECIAL', 'Rapport spécial'),
    ]

    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='comptes_rendus')
    reunion = models.ForeignKey(Reunion, on_delete=models.SET_NULL, null=True, blank=True, related_name='comptes_rendus')
    numero = models.CharField("Numéro", max_length=50)
    type_cr = models.CharField("Type", max_length=25, choices=TYPES)
    date_cr = models.DateField("Date")
    periode_du = models.DateField("Période du", null=True, blank=True)
    periode_au = models.DateField("Période au", null=True, blank=True)
    objet = models.CharField("Objet", max_length=255)
    contenu = models.TextField("Contenu")
    redige_par = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='cr_rediges')
    valide_par = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='cr_valides')
    document = models.FileField(upload_to='projets/comptes_rendus/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'projets_compte_rendu'
        verbose_name = "Compte rendu"
        verbose_name_plural = "Comptes rendus"
        ordering = ['-date_cr']

    def __str__(self):
        return f"{self.numero} - {self.objet}"


class Suspension(models.Model):
    """حالات تعليق المشروع"""
    MOTIFS = [
        ('FORCE_MAJEURE', 'Force majeure'),
        ('INTEMPERIES', 'Intempéries'),
        ('ORDRE_SERVICE', 'Ordre de service'),
        ('MANQUE_PAIEMENT', 'Manque de paiement'),
        ('AUTRE', 'Autre'),
    ]

    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='suspensions')
    motif = models.CharField("Motif", max_length=25, choices=MOTIFS)
    motif_detail = models.TextField("Détail du motif")
    date_debut = models.DateField("Date de début")
    date_fin_prevue = models.DateField("Date de fin prévue", null=True, blank=True)
    date_fin_reelle = models.DateField("Date de fin réelle", null=True, blank=True)
    delai_accorde = models.IntegerField("Délai accordé (jours)", default=0)
    reference_os = models.CharField("Référence OS", max_length=100, blank=True)
    document = models.FileField(upload_to='projets/suspensions/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'projets_suspension'
        verbose_name = "Suspension"
        verbose_name_plural = "Suspensions"

    def __str__(self):
        return f"Suspension {self.projet.reference} du {self.date_debut}"


class Livrable(models.Model):
    """المنتوجات/التسليمات"""
    TYPES = [
        ('PLAN', 'Plan'),
        ('RAPPORT', 'Rapport'),
        ('ETUDE', 'Étude'),
        ('PROTOTYPE', 'Prototype'),
        ('DOCUMENT', 'Document'),
        ('CODE_SOURCE', 'Code source'),
        ('FORMATION', 'Formation'),
        ('AUTRE', 'Autre'),
    ]
    STATUTS = [
        ('A_FAIRE', 'À faire'),
        ('EN_COURS', 'En cours'),
        ('LIVRE', 'Livré'),
        ('VALIDE', 'Validé'),
        ('REFUSE', 'Refusé'),
    ]

    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='livrables')
    designation = models.CharField("Désignation", max_length=200)
    description = models.TextField("Description", blank=True)
    type_livrable = models.CharField("Type", max_length=20, choices=TYPES)
    date_echeance = models.DateField("Date d'échéance")
    date_livraison_reelle = models.DateField("Date de livraison réelle", null=True, blank=True)
    version = models.PositiveIntegerField("Version", default=1)
    statut = models.CharField("Statut", max_length=20, choices=STATUTS, default='A_FAIRE')
    document = models.FileField(upload_to='projets/livrables/%Y/%m/', blank=True, null=True)
    valide_par = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='livrables_valides')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'projets_livrable'
        verbose_name = "Livrable"
        verbose_name_plural = "Livrables"
        ordering = ['date_echeance']

    def __str__(self):
        return f"{self.designation} (v{self.version})"


# =============================================================================
# SECTION 5: GED - GESTION ÉLECTRONIQUE DES DOCUMENTS
# =============================================================================

class GedDocument(models.Model):
    """وثيقة GED - أرشفة إلكترونية"""
    CATEGORIES = [
        ('CCTP', 'CCTP'), ('CCAP', 'CCAP'), ('CSPS', 'CSPS'),
        ('PLAN', 'Plan'), ('PV', 'Procès-verbal'), ('RAPPORT', 'Rapport'),
        ('CORRESPONDANCE', 'Correspondance'), ('PHOTO', 'Photo'),
        ('ATTACHEMENT', 'Attachement'), ('SITUATION', 'Situation de travaux'),
        ('DECOMPTE', 'Décompte'), ('OS', 'Ordre de service'),
        ('AVENANT', 'Avenant'), ('FACTURE', 'Facture'),
        ('CONTRAT', 'Contrat'), ('AUTRE', 'Autre'),
    ]
    STATUTS = [
        ('BROUILLON', 'Brouillon'),
        ('VALIDE', 'Validé'),
        ('ARCHIVE', 'Archivé'),
        ('OBSOLETE', 'Obsolète'),
    ]

    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='ged_documents')
    titre = models.CharField("Titre", max_length=255)
    reference = models.CharField("Référence", max_length=100, blank=True)
    categorie = models.CharField("Catégorie", max_length=20, choices=CATEGORIES)
    description = models.TextField("Description", blank=True)
    version_courante = models.PositiveIntegerField("Version courante", default=1)
    fichier = models.FileField(upload_to='projets/ged/%Y/%m/')
    taille = models.BigIntegerField("Taille (bytes)", default=0)
    type_mime = models.CharField("Type MIME", max_length=100, blank=True)
    statut = models.CharField("Statut", max_length=20, choices=STATUTS, default='BROUILLON')
    linked_model = models.CharField("Modèle lié", max_length=50, blank=True)
    linked_id = models.PositiveIntegerField("ID lié", null=True, blank=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='ged_documents_uploaded')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projets_ged_document'
        verbose_name = "Document GED"
        verbose_name_plural = "Documents GED"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titre} (v{self.version_courante})"


class GedVersion(models.Model):
    """إصدارات الوثيقة"""
    document = models.ForeignKey(GedDocument, on_delete=models.CASCADE, related_name='versions')
    numero_version = models.PositiveIntegerField("Numéro de version")
    fichier = models.FileField(upload_to='projets/ged/versions/%Y/%m/')
    taille = models.BigIntegerField("Taille (bytes)", default=0)
    description = models.TextField("Description", blank=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'projets_ged_version'
        verbose_name = "Version document"
        verbose_name_plural = "Versions documents"
        unique_together = ['document', 'numero_version']
        ordering = ['-numero_version']

    def __str__(self):
        return f"{self.document.titre} - v{self.numero_version}"


# =============================================================================
# SECTION 6: WORKFLOW ENGINE
# =============================================================================

class Workflow(models.Model):
    """تعريف مسار العمل"""
    code = models.CharField("Code", max_length=50, unique=True)
    nom = models.CharField("Nom", max_length=100)
    description = models.TextField("Description", blank=True)
    actif = models.BooleanField("Actif", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'projets_workflow'
        verbose_name = "Workflow"
        verbose_name_plural = "Workflows"

    def __str__(self):
        return self.nom


class WorkflowEtape(models.Model):
    """مرحلة في مسار العمل"""
    ACTIONS = [
        ('CREATION', 'Création'),
        ('VALIDATION', 'Validation'),
        ('REJET', 'Rejet'),
        ('SIGNATURE', 'Signature'),
        ('PAIEMENT', 'Paiement'),
        ('ARCHIVAGE', 'Archivage'),
    ]

    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='etapes')
    ordre = models.PositiveIntegerField("Ordre")
    nom = models.CharField("Nom", max_length=100)
    action = models.CharField("Action", max_length=20, choices=ACTIONS)
    role_requis = models.CharField("Rôle requis", max_length=100, blank=True)
    delai_max_jours = models.PositiveIntegerField("Délai max (jours)", default=0)
    conditions = models.JSONField("Conditions", default=dict, blank=True)

    class Meta:
        db_table = 'projets_workflow_etape'
        verbose_name = "Étape workflow"
        verbose_name_plural = "Étapes workflow"
        unique_together = ['workflow', 'ordre']
        ordering = ['ordre']

    def __str__(self):
        return f"{self.workflow.nom} - Étape {self.ordre}: {self.nom}"


class WorkflowInstance(models.Model):
    """تنفيذ مسار العمل على وثيقة"""
    STATUTS = [
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
        ('REJETE', 'Rejeté'),
        ('ANNULE', 'Annulé'),
    ]

    workflow = models.ForeignKey(Workflow, on_delete=models.PROTECT, related_name='instances')
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='workflow_instances')
    entity_type = models.CharField("Type d'entité", max_length=50)
    entity_id = models.PositiveIntegerField("ID entité")
    etape_courante = models.ForeignKey(WorkflowEtape, on_delete=models.SET_NULL, null=True, blank=True)
    statut = models.CharField("Statut", max_length=20, choices=STATUTS, default='EN_COURS')
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'projets_workflow_instance'
        verbose_name = "Instance workflow"
        verbose_name_plural = "Instances workflow"

    def __str__(self):
        return f"{self.workflow.nom} - {self.entity_type}#{self.entity_id}"


class WorkflowAction(models.Model):
    """سجل الإجراءات المنفذة"""
    instance = models.ForeignKey(WorkflowInstance, on_delete=models.CASCADE, related_name='actions')
    etape = models.ForeignKey(WorkflowEtape, on_delete=models.PROTECT)
    utilisateur = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    action_effectuee = models.CharField("Action effectuée", max_length=20)
    commentaire = models.TextField("Commentaire", blank=True)
    document_joint = models.FileField(upload_to='projets/workflow/%Y/%m/', blank=True, null=True)
    date_action = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'projets_workflow_action'
        verbose_name = "Action workflow"
        verbose_name_plural = "Actions workflow"
        ordering = ['-date_action']


# =============================================================================
# SECTION 7: INTÉGRATIONS (RH & MATÉRIEL)
# =============================================================================

class AffectationRh(models.Model):
    """تعيين الموارد البشرية (core.Personnel) على المشاريع"""
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE, related_name='affectations_projet')
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='affectations_rh')
    tache = models.ForeignKey(TacheProjet, on_delete=models.SET_NULL, null=True, blank=True, related_name='affectations_rh')
    role = models.CharField("Rôle", max_length=100, blank=True)
    date_debut = models.DateField("Date début")
    date_fin = models.DateField("Date fin", null=True, blank=True)
    pourcentage_temps = models.DecimalField("% temps", max_digits=5, decimal_places=2, default=100)
    heures_prevues = models.DecimalField("Heures prévues", max_digits=8, decimal_places=2, default=0)
    heures_reelles = models.DecimalField("Heures réelles", max_digits=8, decimal_places=2, default=0)

    class Meta:
        db_table = 'projets_affectation_rh'
        verbose_name = "Affectation RH"
        verbose_name_plural = "Affectations RH"

    def __str__(self):
        return f"{self.personnel} → {self.projet.reference} ({self.role})"


class MobilisationMateriel(models.Model):
    """تعبئة الموارد المادية (core.Engin / core.Equipement) على المشاريع"""
    TYPES = [
        ('PROPRE', 'Propre'),
        ('LOCATION', 'Location'),
    ]

    engin = models.ForeignKey(Engin, on_delete=models.SET_NULL, null=True, blank=True, related_name='mobilisations_projet')
    equipement = models.ForeignKey(Equipement, on_delete=models.SET_NULL, null=True, blank=True, related_name='mobilisations_projet')
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='mobilisations_materiel')
    tache = models.ForeignKey(TacheProjet, on_delete=models.SET_NULL, null=True, blank=True)
    type_mobilisation = models.CharField("Type", max_length=10, choices=TYPES)
    date_debut = models.DateField("Date début")
    date_fin = models.DateField("Date fin", null=True, blank=True)
    heures_utilisees = models.DecimalField("Heures utilisées", max_digits=8, decimal_places=2, default=0)
    cout = models.DecimalField("Coût", max_digits=15, decimal_places=3, default=0)

    class Meta:
        db_table = 'projets_mobilisation_materiel'
        verbose_name = "Mobilisation matériel"
        verbose_name_plural = "Mobilisations matériel"

    def __str__(self):
        materiel = self.engin or self.equipement
        return f"{materiel} → {self.projet.reference}"


# =============================================================================
# SECTION 8: SUIVI DE L'EXÉCUTION (RÉALISATIONS)
# =============================================================================

class ReferenceProcedure(models.Model):
    """
    📚 مكتبة الإجراءات المرجعية (Knowledge Base)
    ❌ لا تحتوي على مدة أو تكلفة (تختلف من مشروع لآخر)
    ✅ فقط: وصف، معايير جودة، متطلبات نموذجية، تفاصيل متوقعة
    """
    code = models.CharField(
        "Code Procédure", max_length=50, unique=True,
        help_text="Ex: GC-FOND-001, EL-CABL-002"
    )
    nom = models.CharField("Nom de la procédure", max_length=255)
    domaine = models.ForeignKey(
        'DomaineCompetence', on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Domaine de compétence"
    )
    description_standard = models.TextField(
        "Description standard", blank=True,
        help_text="Description technique détaillée de la procédure"
    )

    # ✅ المعايير والموارد المرجعية
    criteres_qualite = models.JSONField(
        "Critères de qualité", default=list, blank=True,
        help_text='Ex: ["Résistance béton ≥ 25 MPa", "Épaisseur dalle = 20cm"]'
    )
    ressources_typiques = models.JSONField(
        "Ressources typiques", default=list, blank=True,
        help_text='Ex: ["Grue 50T", "Camion malaxeur", "Coffrage métallique"]'
    )
    documents_reference = models.JSONField(
        "Documents de référence", default=list, blank=True,
        help_text='Ex: ["Norme NF P18-305", "Plan type PT-001"]'
    )

    # ✅ NEW: قائمة التفاصيل المتوقعة (قالب للتفاصيل الفعلية)
    details_attendus = models.JSONField(
        "Détails attendus", default=list, blank=True,
        help_text='Ex: [{"type": "ACHAT", "description": "Béton C25", "unite": "m³"}, {"type": "LOCATION", "description": "Pompe"}]'
    )

    actif = models.BooleanField("Actif", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Procédure de Référence"
        verbose_name_plural = "Procédures de Référence"
        ordering = ['domaine', 'code']

    def __str__(self):
        return f"[{self.code}] {self.nom}"


class Realisation(models.Model):
    """
    🎯 تتبع التنفيذ الفعلي في مشروع محدد (Master)
    ❌ لا تحتوي على reference_procedure (الربط في DetailsRealisation)
    ✅ فقط: المشروع، التواريخ الفعلية، الحالة
    """
    STATUT_CHOICES = [
        ('PLANIFIE', 'Planifié'),
        ('EN_COURS', 'En cours'),
        ('SUSPENDU', 'Suspendu'),
        ('TERMINE', 'Terminé'),
        ('ANNULE', 'Annulé'),
    ]

    # الربط بالهيكل الهرمي للمشروع
    projet = models.ForeignKey(
        'Projet', on_delete=models.CASCADE,
        related_name='realisations',
        verbose_name="Projet"
    )
    lot = models.ForeignKey(
        'Lot', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='realisations',
        verbose_name="Lot"
    )
    ouvrage = models.ForeignKey(
        'Ouvrage', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='realisations',
        verbose_name="Ouvrage"
    )
    tache = models.ForeignKey(
        'TacheProjet', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='realisations',
        verbose_name="Tâche"
    )

    # المعلومات الأساسية
    nom = models.CharField("Nom de la réalisation", max_length=255)
    description = models.TextField("Description", blank=True)

    # التواريخ الفعلية
    date_debut_reelle = models.DateField("Date début réelle", null=True, blank=True)
    date_fin_reelle = models.DateField("Date fin réelle", null=True, blank=True)

    # الحالة والتقدم
    statut = models.CharField(
        "Statut", max_length=20,
        choices=STATUT_CHOICES, default='PLANIFIE'
    )
    pourcentage_avancement = models.PositiveSmallIntegerField(
        "Avancement (%)", default=0,
        validators=[MaxValueValidator(100)]
    )

    # المسؤول
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Responsable de l'exécution"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Réalisation"
        verbose_name_plural = "Réalisations"
        ordering = ['-date_debut_reelle']

    def __str__(self):
        return f"{self.nom} ({self.get_statut_display()})"

    @property
    def cout_total(self):
        """حساب التكلفة الإجمالية من جميع DetailsRealisation"""
        from django.db.models import Sum
        total = self.details.aggregate(total=Sum('cout_total'))['total']
        return total or 0

    @property
    def duree_reelle_jours(self):
        """حساب المدة الفعلية بالأيام"""
        if self.date_debut_reelle and self.date_fin_reelle:
            return (self.date_fin_reelle - self.date_debut_reelle).days
        return None


class DetailsRealisation(models.Model):
    """
    📝 تفاصيل التنفيذ الفعلية
    ✅ مرتبطة بـ: Realisation (التنفيذ الفعلي)
    ✅ مرتبطة بـ: ReferenceProcedure (المرجع القياسي)
    
    ⚠️ ملاحظة: كل نوع من التفاصيل له حقوله الخاصة:
    - TRAVAUX: personnel
    - ACHAT: fournisseur
    - LOCATION: engin, equipement
    - LOGISTIQUE: impact_delai_jours → يُستخدم EvenementLogistique بدلاً من هذا
    - RH: personnel
    
    ❌ لا يحتوي على: impact_delai_jours, conforme, valeurs_mesurees
       (هذه الحقول موجودة في EvenementLogistique و Resultat)
    """
    TYPE_DETAIL_CHOICES = [
        ('TRAVAUX', '🔨 Travaux / Main d\'oeuvre'),
        ('ACHAT', '🛒 Achat / Approvisionnement'),
        ('LOCATION', '🚜 Location / Location'),
        ('LOGISTIQUE', '🚚 Logistique / Transport'),
        ('RH', '👥 Ressources Humaines'),
        ('AUTRE', '📝 Autre'),
    ]

    # ✅ الربط بالتنفيذ الفعلي (Master)
    realisation = models.ForeignKey(
        'Realisation', on_delete=models.CASCADE,
        related_name='details',
        verbose_name="Réalisation"
    )

    # ✅ الربط بالمرجع القياسي (اختياري)
    reference_procedure = models.ForeignKey(
        'ReferenceProcedure', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='details_realisation',
        verbose_name="Procédure de référence"
    )

    # نوع التفصيل
    type_detail = models.CharField(
        "Type de détail", max_length=20,
        choices=TYPE_DETAIL_CHOICES, default='TRAVAUX'
    )

    # الوصف
    description = models.CharField("Description", max_length=255)

    # الكميات والتكاليف (حقول مشتركة)
    quantite = models.DecimalField("Quantité", max_digits=10, decimal_places=2, default=0)
    unite = models.CharField("Unité", max_length=20, blank=True)
    prix_unitaire = models.DecimalField("Prix unitaire (TND)", max_digits=12, decimal_places=3, default=0)
    cout_total = models.DecimalField("Coût total (TND)", max_digits=14, decimal_places=3, default=0)

    # ✅ معلومات إضافية حسب النوع
    fournisseur = models.CharField(
        "Fournisseur / Prestataire", max_length=255, blank=True,
        help_text="Pour type = ACHAT"
    )
    personnel = models.JSONField(
        "Personnel impliqué", default=list, blank=True,
        help_text='Pour type = TRAVAUX ou RH. Ex: ["Ahmed", "Sami"]'
    )
    engin = models.ForeignKey(
        'core.Engin', on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Engin utilisé",
        help_text="Pour type = LOCATION"
    )
    equipement = models.ForeignKey(
        'core.Equipement', on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Équipement utilisé",
        help_text="Pour type = LOCATION"
    )

    # الوثائق
    document_joint = models.FileField(
        "Document justificatif",
        upload_to='projets/details_realisation/',
        blank=True, null=True
    )

    # ملاحظات
    observation = models.TextField("Observations", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Détail de Réalisation"
        verbose_name_plural = "Détails de Réalisation"
        ordering = ['type_detail', 'created_at']

    def __str__(self):
        return f"{self.get_type_detail_display()} - {self.description}"

    def save(self, *args, **kwargs):
        """حساب cout_total تلقائياً"""
        if not self.cout_total and self.quantite and self.prix_unitaire:
            self.cout_total = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)


class EvenementLogistique(models.Model):
    """
    🚚 تتبع الأحداث اللوجستية (شاحنات، معدات، حوادث)
    ✅ Master: Realisation (nullable) + Projet (obligatoire)
    ✅ Paramétrable: يمكن إضافة أنواع جديدة
    
    ⚠️ هذا النموذج هو المسؤول عن:
    - impact_delai_jours (تأثير على الجدول الزمني)
    - أحداث الشاحنات والمعدات
    - الحوادث والتأخيرات
    """
    TYPE_EVENEMENT_CHOICES = [
        ('ENTREE_CAMION', '🚚 Entrée camion'),
        ('SORTIE_CAMION', '🚛 Sortie camion'),
        ('MOBILISATION_ENGIN', '🚜 Mobilisation engin'),
        ('DEMOBILISATION_ENGIN', '🔙 Démobilisation engin'),
        ('LIVRAISON_MATERIEL', '📦 Livraison matériel'),
        ('INCIDENT', '🚨 Incident / Arrêt'),
        ('INTEMPERIES', '🌧️ Intempéries'),
        ('REUNION_CHANTIER', '👥 Réunion de chantier'),
        ('AUTRE', '📝 Autre'),
    ]

    # ✅ الربط بـ Master (اختياري - يمكن أن يكون على مستوى المشروع فقط)
    realisation = models.ForeignKey(
        'Realisation', on_delete=models.CASCADE,
        related_name='evenements_logistiques',
        null=True, blank=True,
        verbose_name="Réalisation concernée"
    )

    # ✅ الربط بالمشروع (إلزامي)
    projet = models.ForeignKey(
        'Projet', on_delete=models.CASCADE,
        related_name='evenements_logistiques',
        verbose_name="Projet"
    )

    # نوع الحدث
    type_evenement = models.CharField(
        "Type d'événement", max_length=30,
        choices=TYPE_EVENEMENT_CHOICES, default='AUTRE'
    )

    # التاريخ والوصف
    date_evenement = models.DateTimeField(
        "Date et heure", default=timezone.now
    )
    description = models.TextField("Description détaillée")

    # الربط بالمعدات (اختياري)
    engin = models.ForeignKey(
        'core.Engin', on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Engin concerné"
    )
    equipement = models.ForeignKey(
        'core.Equipement', on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Équipement concerné"
    )

    # ✅ التأثير على الجدول الزمني (الحقل المسؤول هنا)
    impact_delai_jours = models.FloatField(
        "Impact sur délai (jours)", default=0.0,
        help_text="Positif = retard, Négatif = gain, 0 = neutre"
    )

    # وثائق
    document_joint = models.FileField(
        "Document justificatif",
        upload_to='projets/logistique/%Y/%m/',
        blank=True, null=True
    )

    # من سجّل الحدث
    declare_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Déclaré par"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Événement Logistique"
        verbose_name_plural = "Événements Logistiques"
        ordering = ['-date_evenement']

    def __str__(self):
        ref = self.realisation.nom if self.realisation else self.projet.reference
        return f"[{self.get_type_evenement_display()}] {ref} - {self.date_evenement.strftime('%d/%m/%Y')}"


class LienAchat(models.Model):
    """
    🛒 ربط DetailsRealisation (نوع ACHAT) بطلبات الشراء الفعلية
    ✅ Master: Realisation
    ✅ مرتبط بـ: DetailsRealisation (اختياري - للتتبع الدقيق)
    """
    STATUT_LIVRAISON_CHOICES = [
        ('COMMANDE', '📋 Commandé'),
        ('EN_LIVRAISON', '🚚 En livraison'),
        ('LIVRE', '✅ Livré'),
        ('RETARD', '⚠️ Retard'),
        ('ANNULE', '❌ Annulé'),
    ]

    # ✅ الربط بـ Master (Realisation)
    realisation = models.ForeignKey(
        'Realisation', on_delete=models.CASCADE,
        related_name='liens_achat',
        verbose_name="Réalisation"
    )

    # ✅ الربط بـ DetailsRealisation (اختياري)
    detail_realisation = models.ForeignKey(
        'DetailsRealisation', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='liens_achat',
        verbose_name="Détail d'achat lié"
    )

    # معلومات طلب الشراء
    numero_bc = models.CharField("N° Bon de Commande", max_length=50)
    date_bc = models.DateField("Date du BC", null=True, blank=True)
    fournisseur = models.CharField("Fournisseur", max_length=255, blank=True)

    # المبلغ
    montant_prevu = models.DecimalField("Montant prévu (TND)", max_digits=15, decimal_places=3, default=0)
    montant_reel = models.DecimalField("Montant réel (TND)", max_digits=15, decimal_places=3, default=0)

    # المتابعة
    statut_livraison = models.CharField(
        "Statut livraison", max_length=20,
        choices=STATUT_LIVRAISON_CHOICES, default='COMMANDE'
    )
    date_livraison_prevue = models.DateField("Date livraison prévue", null=True, blank=True)
    date_livraison_reelle = models.DateField("Date livraison réelle", null=True, blank=True)

    # وثائق
    document_bc = models.FileField(
        "Document BC", upload_to='projets/bons_commande/%Y/%m/',
        blank=True, null=True
    )

    # ملاحظات
    observation = models.TextField("Observations", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lien Achat (BC)"
        verbose_name_plural = "Liens Achats (BC)"
        ordering = ['-date_bc']

    def __str__(self):
        return f"BC {self.numero_bc} - {self.fournisseur or 'Sans fournisseur'}"

    @property
    def ecart_livraison_jours(self):
        """حساب الفرق بين التاريخ المتوقع والفعلي"""
        if self.date_livraison_prevue and self.date_livraison_reelle:
            return (self.date_livraison_reelle - self.date_livraison_prevue).days
        return None


class Consommation(models.Model):
    """
    ⛽ تسجيل الاستهلاك الفعلي للمواد والموارد
    ✅ Master: Realisation
    ✅ Paramétrable: يمكن إضافة أنواع جديدة
    """
    TYPE_CONSOMMATION_CHOICES = [
        ('MATERIAU', '🧱 Matériaux (Béton, Acier...)'),
        ('CARBURANT', '⛽ Carburant'),
        ('EAU', '💧 Eau'),
        ('ELECTRICITE', '⚡ Électricité'),
        ('MAIN_OEUVRE', '👷 Main d\'oeuvre'),
        ('LOCATION_ENGIN', '🚜 Location engins'),
        ('AUTRE', '📝 Autre'),
    ]

    # ✅ الربط بـ Master (Realisation)
    realisation = models.ForeignKey(
        'Realisation', on_delete=models.CASCADE,
        related_name='consommations',
        verbose_name="Réalisation"
    )

    # نوع الاستهلاك
    type_consommation = models.CharField(
        "Type de consommation", max_length=20,
        choices=TYPE_CONSOMMATION_CHOICES, default='MATERIAU'
    )

    date_consommation = models.DateField(
        "Date de consommation", default=timezone.now
    )

    # المعلومات الأساسية
    designation = models.CharField("Désignation", max_length=255)

    # الكميات والتكلفة
    quantite = models.DecimalField("Quantité", max_digits=12, decimal_places=2, default=0)
    unite = models.CharField("Unité", max_length=20, blank=True)
    cout_unitaire = models.DecimalField("Coût unitaire (TND)", max_digits=12, decimal_places=3, default=0)
    cout_total = models.DecimalField("Coût total (TND)", max_digits=15, decimal_places=3, default=0)

    # ربط بالمخزون (اختياري)
    cod_art = models.CharField(
        "Code Article (Stock)", max_length=50, blank=True,
        help_text="Code article depuis le module stock"
    )

    # ملاحظات
    observation = models.TextField("Observations", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Consommation"
        verbose_name_plural = "Consommations"
        ordering = ['-date_consommation']

    def __str__(self):
        return f"{self.get_type_consommation_display()} - {self.designation} ({self.quantite} {self.unite})"

    def save(self, *args, **kwargs):
        """حساب cout_total تلقائياً"""
        if not self.cout_total and self.quantite and self.cout_unitaire:
            self.cout_total = self.quantite * self.cout_unitaire
        super().save(*args, **kwargs)


class Resultat(models.Model):
    """
    📊 تسجيل النتائج (essais, contrôles, PV de réception)
    ✅ Master: Realisation
    ✅ Paramétrable: يمكن إضافة أنواع جديدة
    ✅ Flexible: valeurs_mesurees (JSON) للمرونة
    
    ⚠️ هذا النموذج هو المسؤول عن:
    - conforme (المطابقة للمعايير)
    - valeurs_mesurees (القيم المقاسة)
    - valeurs_reference (القيم المرجعية للمقارنة)
    """
    TYPE_RESULTAT_CHOICES = [
        ('ESSAI_BETON', '🧪 Essai béton'),
        ('ESSAI_SOL', '🏔️ Essai sol'),
        ('ESSAI_MATERIAU', '🔬 Essai matériau'),
        ('CONTROLE_QUALITE', '✅ Contrôle qualité'),
        ('PV_RECEPTION', '📋 PV de réception'),
        ('RAPPORT_TECHNIQUE', '📄 Rapport technique'),
        ('MESURE_DIMENSION', '📏 Mesure dimensionnelle'),
        ('AUTRE', '📝 Autre'),
    ]

    # ✅ الربط بـ Master (Realisation)
    realisation = models.ForeignKey(
        'Realisation', on_delete=models.CASCADE,
        related_name='resultats',
        verbose_name="Réalisation"
    )

    # نوع النتيجة
    type_resultat = models.CharField(
        "Type de résultat", max_length=30,
        choices=TYPE_RESULTAT_CHOICES, default='CONTROLE_QUALITE'
    )

    # المعلومات الأساسية
    titre = models.CharField("Titre", max_length=255)
    description = models.TextField("Description", blank=True)

    # ✅ القيم المقاسة (JSON للمرونة)
    valeurs_mesurees = models.JSONField(
        "Valeurs mesurées", default=dict, blank=True,
        help_text='Ex: {"résistance": "28 MPa", "épaisseur": "20.5 cm"}'
    )

    # ✅ القيم المرجعية (للمقارنة)
    valeurs_reference = models.JSONField(
        "Valeurs de référence", default=dict, blank=True,
        help_text='Ex: {"résistance_min": "25 MPa", "épaisseur_min": "20 cm"}'
    )

    # ✅ الحكم (المطابقة)
    conforme = models.BooleanField("Conforme aux normes", default=True)
    ecart_constate = models.TextField("Écart constaté (si non conforme)", blank=True)

    # التاريخ
    date_resultat = models.DateField("Date du résultat", default=timezone.now)

    # الوثائق
    document_joint = models.FileField(
        "Document (PV, Rapport)",
        upload_to='projets/resultats/%Y/%m/',
        blank=True, null=True
    )

    # من أنجز النتيجة
    realise_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Réalisé par"
    )

    # الربط بمختبر (اختياري)
    laboratoire = models.CharField(
        "Laboratoire / Organisme", max_length=255, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Résultat / Contrôle"
        verbose_name_plural = "Résultats / Contrôles"
        ordering = ['-date_resultat']

    def __str__(self):
        statut = "✅" if self.conforme else "❌"
        return f"{statut} {self.titre} ({self.get_type_resultat_display()})"

    @property
    def nombre_mesures(self):
        """عدد القياسات"""
        return len(self.valeurs_mesurees) if self.valeurs_mesurees else 0
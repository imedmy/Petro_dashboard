# core/models.py
from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import CustomUser
from django.contrib.auth.hashers import make_password, check_password
import os
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

class CompanyInfo(models.Model):
    name = models.CharField("الاسم", max_length=255)
    address = models.TextField("العنوان", blank=True, null=True)
    phone = models.CharField("الهاتف", max_length=50, blank=True, null=True)
    email = models.EmailField("البريد الإلكتروني", blank=True, null=True)
    logo = models.ImageField("اللوجو", upload_to='logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "معلومات الشركة"
        verbose_name_plural = "معلومات الشركة"

class Personnel(models.Model):
    matricule = models.CharField("Matricule", max_length=20, unique=True)
    nom = models.CharField("Nom", max_length=100)
    prenom = models.CharField("Prénom", max_length=100)
    email = models.EmailField("Email", unique=True)
    telephone = models.CharField("Téléphone", max_length=20, blank=True)
    poste = models.CharField("Poste", max_length=100, blank=True)
    actif = models.BooleanField("Actif", default=True)
    username = models.CharField("Nom d'utilisateur", max_length=150, unique=True)
    password = models.CharField("Mot de passe", max_length=128)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    class Meta:
        db_table = 'personnel'
        verbose_name = "Personnel"
        verbose_name_plural = "Personnels"

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.matricule})"

class Tiers(models.Model):
    code_tiers = models.CharField("Code Tiers", max_length=50, unique=True)
    raison_sociale = models.CharField("Raison Sociale", max_length=255)
    contact = models.CharField("Contact", max_length=100, blank=True)
    telephone = models.CharField("Téléphone", max_length=20, blank=True)
    email = models.EmailField("Email", blank=True)
    TYPE_CHOICES = [
        ('fournisseur', 'Fournisseur'),
        ('prestataire', 'Prestataire'),
        ('autre', 'Autre')
    ]
    type_tiers = models.CharField("Type", max_length=20, choices=TYPE_CHOICES, default='autre')
    actif = models.BooleanField("Actif", default=True)

    class Meta:
        db_table = 'tiers'
        verbose_name = "Tiers"
        verbose_name_plural = "Tiers"

    def __str__(self):
        return f"{self.raison_sociale} ({self.code_tiers})"    

class Page(models.Model):
    name_fr = models.CharField("الاسم (FR)", max_length=100)
    name_ar = models.CharField("الاسم (AR)", max_length=100)
    url_name = models.CharField("اسم الرابط", max_length=50, unique=True)
    order = models.IntegerField("الترتيب", default=0)
    is_active = models.BooleanField("مفعّل", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_page'
        ordering = ['order']
        verbose_name = "صفحة"
        verbose_name_plural = "الصفحات"

    def __str__(self):
        return self.name_fr


class PermissionMatrix(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="المستخدم")
    page = models.ForeignKey(Page, on_delete=models.CASCADE, verbose_name="الصفحة")
    can_consulte = models.BooleanField("العرض", default=False)
    can_insert = models.BooleanField("الإضافة", default=False)
    can_update = models.BooleanField("التعديل", default=False)
    can_delete = models.BooleanField("الحذف", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_permissionmatrix'
        unique_together = ('user', 'page')
        verbose_name = "مصفوفة الصلاحيات"
        verbose_name_plural = "مصفوفات الصلاحيات"

    def __str__(self):
        return f"{self.user.username} - {self.page.name_fr}"

class ArticleFamily(models.Model):
    name = models.CharField("Nom de la famille", max_length=200)
    code_segment = models.CharField("Segment de code", max_length=5)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Famille parente"
    )
    description = models.TextField("Description", blank=True, null=True)
    
    # ✅ الكود الكامل (يُحسب تلقائيًا)
    full_code = models.CharField("Code complet", max_length=9, blank=True, db_index=True)

    class Meta:
        db_table = 'core_articlefamily'  # ✅ تحديد اسم الجدول
        verbose_name = "Famille d'article"
        verbose_name_plural = "Familles d'articles"
        ordering = ['full_code']

    def __str__(self):
        return f"{self.full_code} - {self.name}"

    def save(self, *args, **kwargs):
        old_full_code = self.full_code if self.pk else None

        if self.parent:
            self.full_code = f"{self.parent.full_code}{self.code_segment}"
        else:
            self.full_code = self.code_segment

        super().save(*args, **kwargs)

        # تحديث أبناء هذه العائلة إذا تغير full_code
        if old_full_code and old_full_code != self.full_code:
            self._update_children_full_codes()

    def _update_children_full_codes(self):
        """تحديث full_code لجميع الأبناء عند تغير الكود الأصل"""
        for child in self.children.all():
            old_code = child.full_code
            if child.parent:
                child.full_code = f"{child.parent.full_code}{child.code_segment}"
            child.save()
            if old_code != child.full_code:
                child._update_children_full_codes()


class Caracteristique(models.Model):
    nom = models.CharField("Nom de la caractéristique", max_length=100)

    TYPE_VALEUR_CHOICES = [
        ('text', 'Texte'),
        ('number', 'Nombre'),
        ('unit', 'Nombre avec unité'),
        ('choice', 'Choix prédéfini'),
        ('boolean', 'Oui/Non'),
    ]
    type_valeur = models.CharField(
        "Type de valeur",
        max_length=20,
        choices=TYPE_VALEUR_CHOICES,
        default='text'
    )
    unite = models.CharField("Unité", max_length=20, blank=True, null=True)
    utilisable_dans_recherche = models.BooleanField(
        "Utilisable dans la recherche",
        default=True
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='enfants'
    )

    class Meta:
        db_table = 'core_caracteristique'  # ✅ تحديد اسم الجدول
        verbose_name = "Caractéristique Technique"
        verbose_name_plural = "Caractéristiques Techniques"
        ordering = ['nom']

    def __str__(self):
        if self.unite:
            return f"{self.nom} ({self.unite})"
        return self.nom

    def get_hierarchy_level(self):
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level


def article_image_upload_path(instance, filename):
    """
    دالة ديناميكية لتحديد مكان حفظ الصورة
    مثال: media/articles/ABC123/photo.jpg
    """
    return f'articles/{instance.cod_art}/{filename}'


class ArticleCaracteristique(models.Model):
    cod_art = models.CharField("Code Article", max_length=50)
    caracteristique = models.ForeignKey(Caracteristique, on_delete=models.CASCADE)
    valeur = models.TextField("Valeur", blank=True, null=True)

    class Meta:
        db_table = 'core_articlecaracteristique'
        verbose_name = "Valeur Caractéristique Article"
        verbose_name_plural = "Valeurs Caractéristiques Articles"
        unique_together = ('cod_art', 'caracteristique')

    def __str__(self):
        return f"{self.cod_art} - {self.caracteristique.nom}: {self.valeur}"

    def clean(self):
        if not self.cod_art or len(self.cod_art.strip()) == 0:
            raise ValidationError({"cod_art": "Le code article est obligatoire."})


class ArticleImage(models.Model):
    cod_art = models.CharField("Code Article", max_length=50)
    image = models.ImageField("Image", upload_to=article_image_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_articleimage'
        verbose_name = "Image Article"
        verbose_name_plural = "Images Articles"

    def __str__(self):
        return f"Image de {self.cod_art}"

    def delete(self, *args, **kwargs):
        # حذف الملف الفعلي من السيرفر عند الحذف
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super().delete(*args, **kwargs)

    def clean(self):
        if not self.cod_art or len(self.cod_art.strip()) == 0:
            raise ValidationError({"cod_art": "Le code article est obligatoire."})

class NatureStock(models.Model):
    code_nature = models.PositiveSmallIntegerField(
        unique=True,
        verbose_name="Code Nature"
    )
    libelle_nature = models.CharField(
        max_length=255,
        verbose_name="Libellé de la Nature"
    )

    class Meta:
        db_table = 'nature_stock'
        verbose_name = "Nature de stock"
        verbose_name_plural = "Natures de stock"
        ordering = ['code_nature']  # لفرزها تلقائيًا حسب الكود

    def __str__(self):
        return f"{self.code_nature} - {self.libelle_nature}"

class ValeurArticle(models.Model):
    code_valeur = models.PositiveSmallIntegerField(
        unique=True,
        verbose_name="Code Valeur"
    )
    libelle_valeur = models.CharField(
        max_length=255,
        verbose_name="Libellé de la Valeur"
    )

    class Meta:
        db_table = 'valeur_article'
        verbose_name = "Valeur d'article"
        verbose_name_plural = "Valeurs d'article"
        ordering = ['code_valeur']

    def __str__(self):
        return f"{self.code_valeur} - {self.libelle_valeur}"        

class SerialUnit(models.Model):
    """
    نموذج لتتبع الوحدات التي تُعرف برقم تسلسلي.
    المعرف الفريد لكل وحدة هو التركيبة: (cod_art + val_art + numero_serie)
    """

    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('en_reparation', 'En réparation'),
        ('hs', 'Hors service'),
        ('stock', 'En stock'),
    ]

    # الحقول الأساسية - بنفس أسماء قاعدة البيانات
    cod_art = models.CharField(
        max_length=20,
        verbose_name="Code Article"
    )
    val_art = models.IntegerField(
        verbose_name="Valeur Article (VAL_ART)"
    )
    numero_serie = models.CharField(
        max_length=100,
        verbose_name="Numéro de Série",
        help_text="Doit être unique par unité"
    )

    # معلومات إضافية
    date_ajout = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'ajout"
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='stock',
        verbose_name="Statut"
    )
    emplacement = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Emplacement"
    )
    utilisateur = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Utilisateur / Responsable"
    )

    class Meta:
        # منع التكرار: لا يمكن لنفس الرقم التسلسلي أن يكون مسجلًا لنفس (cod_art + val_art)
        unique_together = ('cod_art', 'val_art', 'numero_serie')
        # اختياري: فرز افتراضي
        ordering = ['-date_ajout']
        verbose_name = "Unité avec Numéro de Série"
        verbose_name_plural = "Unités avec Numéro de Série"

    def get_statut_display(self):
        return dict(self.STATUT_CHOICES).get(self.statut, self.statut)

    def get_statut_badge(self):
        mapping = {
            'actif': 'success',
            'en_reparation': 'warning',
            'hs': 'danger',
            'stock': 'info'
        }
        return mapping.get(self.statut, 'secondary')

    def __str__(self):
        return f"{self.numero_serie} | {self.cod_art} (VAL_ART={self.val_art})"

class TypeMouvement(models.Model):
    """
    نموذج لتعريف أنواع حركات المخزون.
    مثال: دخول، خروج، تحويل، صيانة...
    """

    # كود قصير فريد (مثلاً: ENT, SORT, TRANS)
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Code du mouvement",
        help_text="Ex: ENT, SORT, TRANS"
    )

    # اسم النوع بالفرنسية
    libelle = models.CharField(
        max_length=50,
        verbose_name="Libellé",
        help_text="Ex: Entrée, Sortie, Transfert"
    )

    # وصف اختياري
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description"
    )

    # نوع الحركة: زيادة أم نقصان في الكمية؟
    sens = models.CharField(
        max_length=10,
        choices=[
            ('entree', 'Entrée (Stock +)'),
            ('sortie', 'Sortie (Stock -)'),
            ('neutre', 'Neutre')
        ],
        default='neutre',
        verbose_name="Sens du mouvement"
    )

    # هل هذا النوع نشط؟
    actif = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )

    # تاريخ الإنشاء/التحديث
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'type_mouvement'  # اسم الجدول في قاعدة البيانات
        verbose_name = "Type de Mouvement"
        verbose_name_plural = "Types de Mouvements"
        ordering = ['code']

    def __str__(self):
        return f"[{self.code}] {self.libelle}"

class EtapeDossier(models.Model):
    # أنواع التأثير الممكنة
    INFLUENCE_CHOICES = [
        ('instance', 'Instance'),
        ('cloture', 'Clôture'),
        ('litige', 'Litige'),
        ('archivage', 'Archivage'),
        ('reouverture', 'Réouverture'),
        ('autre', 'Autre'),
    ]
    
    code_etape = models.PositiveSmallIntegerField(
        unique=True,
        verbose_name="Code Étape"
    )
    libelle_etape = models.CharField(
        max_length=255,
        verbose_name="Libellé de l'Étape"
    )
    influence = models.CharField(
        max_length=20,
        choices=INFLUENCE_CHOICES,
        default='autre',
        verbose_name="Influence sur le dossier"
    )

    class Meta:
        db_table = 'etape_dossier'
        verbose_name = "Étape de dossier"
        verbose_name_plural = "Étapes de dossier"
        ordering = ['code_etape']

    def __str__(self):
        return f"{self.code_etape} - {self.libelle_etape} ({self.get_influence_display()})"   
        
class SuiviDossier(models.Model):
    # معرفات بطاقة الأمر (من قاعدة بيانات SQL Server)
    numero_com = models.CharField(max_length=50)
    dat_com = models.DateField()
    code_fourn = models.CharField(max_length=20)  # ليس ضروريًا للتفرد، لكنه مفيد للربط
    
    # المرجع من جدول etape_dossier (في MySQL)
    
    INFLUENCE_CHOICES = [
        ('instance', 'Instance'),
        ('cloture', 'Clôture'),
        ('litige', 'Litige'),
        ('archivage', 'Archivage'),
        ('reouverture', 'Réouverture'),
        ('autre', 'Autre'),
    ]
    
    id_etape = models.PositiveSmallIntegerField()  # يتوافق مع code_etape في etape_dossier
    influence_sur_dossier = models.CharField(
        max_length=20,
        choices=INFLUENCE_CHOICES,  # ← هذه السطر ضروري
        default='instance'
    )
    libelle_etape = models.CharField(max_length=255)

    # تاريخ إدخال المرحلة
    date_etape = models.DateField(auto_now_add=True)

    # الحقول الإضافية
    numero_bordereau = models.CharField(max_length=100, null=True, blank=True)
    numero_avis = models.CharField(max_length=100, null=True, blank=True)
    numero_ci = models.CharField(max_length=100, null=True, blank=True)
    numero_facture = models.CharField(max_length=100, null=True, blank=True)
    date_facture = models.DateField(null=True, blank=True)
    numero_bl = models.CharField(max_length=100, null=True, blank=True)
    date_bl = models.DateField(null=True, blank=True)
    email_data = models.JSONField(null=True, blank=True, help_text="Contient les détails complets de l'email: sujet, destinataires, corps, pièces jointes, etc.")
    date_avis = models.DateField(blank=True, null=True)
    bct = models.CharField(max_length=50, blank=True, null=True)
    date_bct = models.DateField(blank=True, null=True)
    date_bordereau = models.DateField(blank=True, null=True)
    date_email = models.DateField(blank=True, null=True)
    observation = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'suivi_dossier'
        # لا نستخدم unique_together لأن code_fourn ليس ضروريًا للتفرد
        # لكن نضيف فهرسًا لتحسين الأداء
        indexes = [
            models.Index(fields=['numero_com', 'dat_com', 'code_fourn']),
            models.Index(fields=['id_etape']),
        ]

    def __str__(self):
        return f"{self.numero_com} - {self.libelle_etape} ({self.date_etape})"

def etape_upload_to(instance, filename):
    # مسار: media/etapes/NUMERO_COM/FILENAME
    return f'etapes/{instance.etape.numero_com}/{filename}'

class PieceJointeEtape(models.Model):
    etape = models.ForeignKey(SuiviDossier, on_delete=models.CASCADE, related_name='pieces_jointes')
    fichier = models.FileField(upload_to=etape_upload_to)
    nom_original = models.CharField(max_length=255)
    date_upload = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.nom_original} - {self.etape.numero_com}"        
        
class EtatB1View(models.Model):
    doc_ref = models.CharField(max_length=255, blank=True, null=True)
    date_ref = models.DateField(blank=True, null=True)
    item = models.CharField(max_length=50, blank=True, null=True, db_column='item')
    cod_art = models.CharField(max_length=50, blank=True, null=True)
    lib_art = models.TextField(blank=True, null=True)
    qte_commande = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)
    nature_bon = models.CharField(max_length=100, blank=True, null=True)
    date_b = models.DateField()  # ← لا يمكن أن يكون null إذا كان جزءًا من PK
    numero_bon = models.CharField(max_length=100)  # ← لا يمكن أن يكون null
    qte_recept = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)
    lib_um_com = models.CharField(max_length=20, blank=True, null=True)
    lib_um = models.CharField(max_length=20, blank=True, null=True)
    valeur_tot = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    class_cout = models.CharField(max_length=50, blank=True, null=True)
    empl = models.CharField(max_length=100, blank=True, null=True)
    old_qte = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)
    val_art = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    num_facture = models.CharField(max_length=100, blank=True, null=True)
    numero_bp = models.TextField(blank=True, null=True)
    taux_change = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'etatb1view'
        # جعل (date_b, numero_bon) فريدًا عالميًا
        constraints = [
            models.UniqueConstraint(
                fields=['date_b', 'numero_bon'],
                name='etat_b1_primary_key'
            )
        ]
        
class AvisArrivee(models.Model):
    """
    نموذج لإشعار الاستلام (AVIS D'ARRIVÉE)
    مرتبط بطلبية واحدة (من قاعدة SQL Server) وقد يحتوي على عدة تفاصيل.
    """
    # معرف الطلبية من قاعدة SQL Server
    numero_com = models.CharField("N° Bon de Commande", max_length=50, blank=True, null=True)
    dat_com = models.DateField("Date Bon de Commande", blank=True, null=True)

    # معلومات إشعار الاستلام
    numero_avis = models.CharField("N° Avis d'Arrivée", max_length=100)
    date_avis = models.DateField("Date Avis")
    numero_bordereau = models.CharField("N° Bordereau", max_length=100, blank=True, null=True)
    bct = models.CharField("BCT", max_length=100, blank=True, null=True)
    numero_facture = models.CharField("N° Facture", max_length=100, blank=True, null=True)
    numero_bl = models.CharField("N° BL", max_length=100, blank=True, null=True)
    observation = models.TextField("Observation", blank=True, null=True)

    # تواريخ النظام
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'avis_arrivee'
        verbose_name = "Avis d'Arrivée"
        verbose_name_plural = "Avis d'Arrivée"
        ordering = ['-date_avis', 'numero_avis']

    def __str__(self):
        return f"Avis {self.numero_avis} pour BC {self.numero_com}"


class DetailAvis(models.Model):
    """
    نموذج لتفاصيل السلع في إشعار الاستلام
    """
    # الربط بإشعار الاستلام
    avis = models.ForeignKey(
        AvisArrivee,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name="Avis d'Arrivée"
    )

    # معلومات السلعة (من جدول LIGNECOM في SQL Server)
    item = models.CharField("Item", max_length=50)
    cod_art = models.CharField("Code Article", max_length=50)
    lib_art = models.TextField("Désignation", blank=True, null=True)

    # الكميات
    qte_commande = models.DecimalField(
        "Quantité Commandée",
        max_digits=15,
        decimal_places=3,
        blank=True,
        null=True
    )
    qte_receptionnee = models.DecimalField(
        "Quantité Réceptionnée",
        max_digits=15,
        decimal_places=3
    )

    # وحدات القياس
    um_commande = models.CharField("UM Commande", max_length=20, blank=True, null=True)
    um_reception = models.CharField("UM Réception", max_length=20, blank=True, null=True)

    # ملاحظات على البند
    observation = models.TextField("Observation sur le détail", blank=True, null=True)
    
    CONFORMITE_CHOICES = [
        ('en_attente_de_l_avis', 'En attente de l\'avis'),
        ('conforme', 'Conforme'),
        ('non_conforme', 'Non Conforme'),
        ('en_litige', 'En Litige'),
    ]
    conformite = models.CharField(
        "Conformité",
        max_length=20,
        choices=CONFORMITE_CHOICES,
        default='conforme',
        blank=True
    )
    
    class Meta:
        db_table = 'detail_avis'
        verbose_name = "Détail Avis"
        verbose_name_plural = "Détails Avis"
        # فهرس لتحسين الأداء
        indexes = [
            models.Index(fields=['avis', 'item']),
            models.Index(fields=['cod_art']),
        ]

    def __str__(self):
        return f"{self.item} - {self.qte_receptionnee} ({self.avis.numero_avis})"

class PieceJointeAvis(models.Model):
    avis = models.ForeignKey(AvisArrivee, on_delete=models.CASCADE, related_name='pieces_jointes')
    fichier = models.FileField(upload_to='avis_pieces/', verbose_name="Fichier")
    nom_original = models.CharField(max_length=255, verbose_name="Nom du fichier")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Description")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'piece_jointe_avis'
        verbose_name = "Pièce jointe"
        verbose_name_plural = "Pièces jointes"

    def __str__(self):
        return self.nom_original       

class PlanningTache(models.Model):
    # الحقل الجديد
    libelle = models.CharField("Libellé", max_length=255, blank=True)

    NATURE_CHOICES = [
        ('ponctuelle', 'Ponctuelle'),
        ('repetitive', 'Répétitive'),
    ]
    nature = models.CharField("Nature", max_length=20, choices=NATURE_CHOICES, default='ponctuelle')
    delai_repetition = models.PositiveIntegerField("Délai de répétition (jours)", default=0)
    observation = models.TextField("Observation", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'planning_tache'
        verbose_name = "Planning Référentiel"
        verbose_name_plural = "Planning Référentiel"

    def __str__(self):
        return self.libelle or f"Planning {self.get_nature_display()} - {self.delai_repetition} jours"  
        
class Tache(models.Model):
    libelle = models.CharField("Intitulé", max_length=255)
    description = models.TextField("Description", blank=True)
    date_prevue = models.DateField("Date prévue")
    observation = models.TextField("Observation", blank=True)
    delai_repetition = models.PositiveIntegerField(
        "Délai de répétition (jours)",
        default=0,
        help_text="Nombre de jours entre chaque répétition. Mettez 0 pour désactiver la répétition."
    )
    ETAT_CHOICES = [
        ('a_faire', 'À faire'),
        ('en_cours', 'En cours'),
        ('faite', 'Faite'),
        ('retardee', 'Retardée'),
    ]
    etat = models.CharField("État", max_length=20, choices=ETAT_CHOICES, default='a_faire')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # إذا كنت ستوفر نموذج PlanningTache لاحقًا، اترك هذا السطر مع تحذير
    planning = models.ForeignKey('PlanningTache', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'tache'
        verbose_name = "Tâche"
        verbose_name_plural = "Tâches"
        ordering = ['-date_prevue']

    def __str__(self):
        return f"{self.libelle} ({self.date_prevue})"

class Intervenant(models.Model):
    tache = models.ForeignKey(Tache, on_delete=models.CASCADE, related_name='intervenants')
    
    # روابط مرنة
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE, null=True, blank=True)
    tiers = models.ForeignKey(Tiers, on_delete=models.CASCADE, null=True, blank=True)
    
    role = models.CharField("Rôle", max_length=100, blank=True)

    class Meta:
        db_table = 'intervenant'
        verbose_name = "Intervenant"
        verbose_name_plural = "Intervenants"

    def __str__(self):
        if self.personnel:
            return f"{self.personnel.nom} {self.personnel.prenom} - {self.role}"
        elif self.tiers:
            return f"{self.tiers.raison_sociale} - {self.role}"
        return "Intervenant inconnu"

# =============================================
# نموذج محدث: Engin (للمركبات والمعدات المتنقلة)
# =============================================
class service(models.Model):
    """
    نموذج لإدارة الخدمات/الأقسام (مثل: TRANSPORT, FORAGE, SECURITE).
    """
    nom = models.CharField("Nom du service", max_length=100, unique=True)
    description = models.TextField("Description", blank=True)

    class Meta:
        db_table = 'service'
        verbose_name = "service"
        verbose_name_plural = "services"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Engin(models.Model):
    TYPE_ENGIN_CHOICES = [
        ('voiture', 'Voiture'),
        ('camion', 'Camion'),
        ('tractopelle', 'Tractopelle'),
        ('grue', 'Grue'),
        ('autre', 'Autre'),
    ]

    SITUATION_CHOICES = [
        ('en_service', 'En service'),
        ('en_panne', 'En panne'),
        ('hors_service', 'Hors service'),
        ('vendu', 'Vendu'),
    ]

    # --- الحقول الأساسية (الموجودة مسبقًا) ---
    libelle = models.CharField("Désignation", max_length=255)
    type_engin = models.CharField("Type d'engin", max_length=20, choices=TYPE_ENGIN_CHOICES, default='autre')
    numero_serie = models.CharField("N° de série / Châssis", max_length=100, blank=True)
    immatriculation = models.CharField("Immatriculation", max_length=50, blank=True)
    numero_bp = models.CharField("Numéro BP", max_length=100, blank=True, help_text="Bon de propriété")
    capacite_reservoir = models.DecimalField("Capacité réservoir (L)", max_digits=6, decimal_places=1, null=True, blank=True)
    type_carburant = models.CharField(
        "Type de carburant",
        max_length=50,
        blank=True,
        choices=[
            ('gasoil', 'Gasoil'),
            ('gasoilSS', 'Gasoil_SS'),
            ('essence', 'Essence'),
            ('electrique', 'Électrique'),
            ('autre', 'Autre'),
        ],
        default='gasoil'
    )
    index_initial = models.DecimalField(
        "Index initial (km)",
        max_digits=12,
        decimal_places=1,
        default=0,
        help_text="Kilométrage de départ"
    )
    actif = models.BooleanField("Actif", default=True)

    # --- الحقول الجديدة من ملف Excel ---
    marque = models.CharField("Marque", max_length=100, blank=True)
    genre = models.CharField("Genre", max_length=100, blank=True, help_text="Ex: AMBULANCE 5 PLACES")
    date_1ere_mise_en_circulation = models.DateField("Date de 1ère mise en circulation", null=True, blank=True)
    date_derniere_visite = models.DateField("Date de dernière visite", null=True, blank=True)
    puissance_fiscale = models.CharField("Puissance fiscale", max_length=50, blank=True, help_text="Ex: 11 CV GASOIL")
    
    # الربط مع نموذج Service الجديد
    service = models.ForeignKey(
        service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Service d'affectation"
    )
    
    situation = models.CharField("Situation actuelle", max_length=20, choices=SITUATION_CHOICES, default='en_service')
    observations = models.TextField("Observations", blank=True)

    # --- تواريخ النظام (اختياري) ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'engin'
        verbose_name = "Engin / Véhicule"
        verbose_name_plural = "Engins / Véhicules"

    def __str__(self):
        return f"{self.get_type_engin_display()} - {self.libelle} ({self.immatriculation or self.numero_serie})"

# =============================================
# نموذج جديد: Equipement (للمعدات الثابتة)
# =============================================
class Equipement(models.Model):
    TYPE_EQUIPEMENT_CHOICES = [
        ('pompe_distribution', 'Pompe de Distribution'),
        ('generateur', 'Générateur'),
        ('compresseur', 'Compresseur'),
        ('reservoir', 'Réservoir'),
        ('autre', 'Autre'),
    ]

    libelle = models.CharField("Désignation", max_length=255)
    type_equipement = models.CharField(
        "Type d'équipement",
        max_length=20,
        choices=TYPE_EQUIPEMENT_CHOICES,
        default='autre'
    )
    numero_serie = models.CharField("N° de série", max_length=100, blank=True)
    numero_bp = models.CharField("Numéro BP", max_length=100, blank=True, help_text="Bon de propriété ou référence interne")
    actif = models.BooleanField("Actif", default=True)

    class Meta:
        db_table = 'equipement'
        verbose_name = "Équipement"
        verbose_name_plural = "Équipements"

    def __str__(self):
        return f"{self.get_type_equipement_display()} - {self.libelle} ({self.numero_serie or '—'})"

        
class LectureIndex(models.Model):
    """
    لتسجيل القراءات اليومية (index) لكل معدة أو مركبة.
    """
    engin = models.ForeignKey(Engin, on_delete=models.CASCADE, related_name='lectures')
    date_lecture = models.DateField("Date de lecture", auto_now_add=True)
    index_courant = models.DecimalField(
        "Index courant (km ou L)",
        max_digits=12,
        decimal_places=1,
        help_text="Lecture actuelle de l'index"
    )
    # يمكن إضافة: qui a fait la lecture؟
    # personnel = models.ForeignKey(Personnel, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'lecture_index'
        verbose_name = "Lecture d'index"
        verbose_name_plural = "Lectures d'index"
        ordering = ['-date_lecture']
        unique_together = ('engin', 'date_lecture')  # قراءة واحدة في اليوم

    def __str__(self):
        return f"{self.engin.libelle} - {self.index_courant} le {self.date_lecture}"

    @property
    def consommation_depuis_derniere_lecture(self):
        """
        حساب الاستهلاك منذ آخر قراءة.
        """
        try:
            derniere = self.engin.lectures.filter(date_lecture__lt=self.date_lecture).order_by('-date_lecture').first()
            if derniere:
                return self.index_courant - derniere.index_courant
            else:
                return self.index_courant - self.engin.index_initial
        except Exception:
            return None


# (اختياري) لتتبع عمليات التعبئة بدلاً من الاعتماد فقط على الفرق في المؤشرات
class ConsommationCarburant(models.Model):
    """
    سجل التعبئة (Ravitaillement) لكل معدة.
    """
    engin = models.ForeignKey(Engin, on_delete=models.CASCADE, related_name='ravitaillements')
    date_ravitaillement = models.DateField("Date de ravitaillement")
    volume_l = models.DecimalField("Volume (L)", max_digits=8, decimal_places=2)
    type_carburant = models.CharField("Type de carburant", max_length=50, default='gasoil')
    # ملاحظات
    observation = models.TextField("Observation", blank=True)

    class Meta:
        db_table = 'consommation_carburant'
        verbose_name = "Consommation / Ravitaillement"
        verbose_name_plural = "Consommations / Ravitaillements"
        ordering = ['-date_ravitaillement']

    def __str__(self):
        return f"{self.engin.libelle} - {self.volume_l}L le {self.date_ravitaillement}"


class PieceJointeTache(models.Model):
    tache = models.ForeignKey(Tache, on_delete=models.CASCADE, related_name='pieces_jointes')
    fichier = models.FileField(upload_to='taches_pieces/', verbose_name="Fichier")
    nom_original = models.CharField(max_length=255, verbose_name="Nom du fichier")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Description")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'piece_jointe_tache'
        verbose_name = "Pièce jointe"
        verbose_name_plural = "Pièces jointes"

    def __str__(self):
        return self.nom_original        

class Citerne(models.Model):
    """
    نموذج لتمثيل خزان الوقود في المحطة.
    """
    # معرف فريد (يمكن أن يكون رقمًا أو كودًا)
    code_citerne = models.CharField(
        "Code Citerne",
        max_length=50,
        unique=True,
        help_text="مثال: CTN_GAS_01, CTN_DIESEL_02"
    )

    # اسم أو وصف الخزان
    nom = models.CharField("Nom / Désignation", max_length=255)

    # نوع الخزان
    TYPE_CHOICES = [
        ('sous_sol', 'Sous Sol'),
        ('sur_skid', 'Sur Skid'),
        ('autre', 'Autre')
    ]
    type_citerne = models.CharField(
        "Type de Citerne",
        max_length=20,
        choices=TYPE_CHOICES,
        default='autre'
    )

    # الأبعاد (اختيارية، قد تكون مفيدة للحسابات أو العرض)
    diametre_cm = models.DecimalField(
        "Diamètre (cm)",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    longueur_cm = models.DecimalField(
        "Longueur (cm)",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    epaisseur_cm = models.DecimalField(
        "Épaisseur (cm)",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    # السائل الذي يحتويه (مرتبط بـ COD_ART من SQL Server)
    # نستخدم حقلًا نصيًا لأنه لا يمكننا إنشاء ForeignKey مباشرة إلى جدول غير مُدار
    cod_art_fluide = models.CharField(
        "Code Article Fluide",
        max_length=50,
        blank=True,
        null=True,
        help_text="كود السائل (مثل: GASOIL, DIESEL) كما هو في قاعدة بيانات SQL Server"
    )

    # اسم السائل (للتوضيح فقط، سيتم تحديثه عند حفظ النموذج)
    libelle_fluide = models.CharField(
        "Libellé Fluide",
        max_length=255,
        blank=True,
        null=True
    )

    # حالة الخزان
    actif = models.BooleanField("Actif", default=True)

    # تواريخ النظام
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'citerne'
        verbose_name = "Citerne"
        verbose_name_plural = "Citernes"
        ordering = ['code_citerne']

    def __str__(self):
        return f"{self.code_citerne} - {self.nom} ({self.get_type_citerne_display()})"

    def save(self, *args, **kwargs):
        """
        تحسين: استرجاع libelle_fluide من SQL Server فقط إذا كان cod_art_fluide موجودًا.
        """
        if self.cod_art_fluide:
            # استرجاع الاسم من SQL Server
            libelle = self.get_libelle_fluide_from_sql_server()
            if libelle is not None:
                self.libelle_fluide = libelle
            else:
                # إذا فشل الاسترجاع، اترك الحقل كما هو أو ضع قيمة افتراضية
                self.libelle_fluide = "Fluide inconnu"
        else:
            self.libelle_fluide = ""

        super().save(*args, **kwargs)
    
    def get_libelle_fluide_from_sql_server(self):
        """
        دالة مساعدة لاسترجاع اسم السائل من SQL Server.
        تعيد الاسم أو None إذا فشلت العملية.
        """
        from django.db import connections
        try:
            with connections['sql_server'].cursor() as cursor:
                cursor.execute("SELECT LIB_ART FROM ARTICLE WHERE COD_ART = %s", [self.cod_art_fluide])
                row = cursor.fetchone()
                if row:
                    return row[0]
                else:
                    print(f"❌ لا يوجد سجل للكود {self.cod_art_fluide} في جدول ARTICLE")
                    return None
        except Exception as e:
            print(f"❌ خطأ في الاتصال بقاعدة SQL Server أو استعلام: {e}")
            return None    

class Barremage(models.Model):
    """
    نموذج لتخزين نقاط جدول التحويل (Barremage) لكل خزان.
    """
    citerne = models.ForeignKey(
        Citerne,
        on_delete=models.CASCADE,
        related_name='barremages',
        verbose_name="Citerne"
    )

    # ارتفاع السائل بالسنتيمتر
    hauteur_cm = models.DecimalField(
        "Hauteur (cm)",
        max_digits=6,
        decimal_places=2,
        help_text="ارتفاع السائل في الخزان (بالسنتيمتر)"
    )

    # الحجم المقابل باللترات
    volume_litres = models.DecimalField(
        "Volume (L)",
        max_digits=12,
        decimal_places=3,
        help_text="الحجم المقابل للارتفاع (باللترات)"
    )

    # تاريخ الإدخال (اختياري)
    date_enregistrement = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'barremage'
        verbose_name = "Point de Barremage"
        verbose_name_plural = "Points de Barremage"
        # جعل التركيبة (citerne, hauteur_cm) فريدة لتجنب التكرار
        unique_together = ('citerne', 'hauteur_cm')
        # فرز حسب الارتفاع
        ordering = ['hauteur_cm']

    def __str__(self):
        return f"{self.citerne.code_citerne} - H={self.hauteur_cm}cm → V={self.volume_litres}L"

class LectureJauge(models.Model):
    """
    لتسجيل قراءة اليومية لمستوى السائل في الخزان.
    """
    citerne = models.ForeignKey(Citerne, on_delete=models.CASCADE, related_name='lectures_jauge')
    date_lecture = models.DateField("Date de lecture", auto_now_add=True)
    hauteur_cm = models.DecimalField(
        "Hauteur (cm)",
        max_digits=6,
        decimal_places=2,
        help_text="Lecture du jauge en centimètres"
    )
    # يمكن حساب الحجم تلقائيًا من جدول barremage
    volume_litres = models.DecimalField(
        "Volume (L)",
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Volume calculé à partir du tableau de barremage"
    )

    class Meta:
        db_table = 'lecture_jauge'
        verbose_name = "Lecture de Jauge"
        verbose_name_plural = "Lectures de Jauge"
        ordering = ['-date_lecture']
        unique_together = ('citerne', 'date_lecture')  # قراءة واحدة فقط في اليوم لكل خزان

    def __str__(self):
        return f"{self.citerne.code_citerne} - H={self.hauteur_cm}cm le {self.date_lecture}"

    def save(self, *args, **kwargs):
        """
        عند الحفظ، احسب الحجم بناءً على جدول الـ Barremage.
        """
        if self.hauteur_cm is not None:
            # البحث عن أقرب نقطة في جدول barremage
            from django.db.models import Q
            barremages = self.citerne.barremages.filter(hauteur_cm__lte=self.hauteur_cm).order_by('-hauteur_cm')
            if barremages.exists():
                point_inferieur = barremages.first()
                point_superieur = self.citerne.barremages.filter(hauteur_cm__gt=self.hauteur_cm).order_by('hauteur_cm').first()

                if point_superieur:
                    # استيفاء خطي بين نقطتين
                    h1, v1 = point_inferieur.hauteur_cm, point_inferieur.volume_litres
                    h2, v2 = point_superieur.hauteur_cm, point_superieur.volume_litres
                    if h2 > h1:
                        self.volume_litres = v1 + ((v2 - v1) / (h2 - h1)) * (self.hauteur_cm - h1)
                else:
                    # إذا لم يكن هناك نقطة أعلى، استخدم أقل نقطة
                    self.volume_litres = point_inferieur.volume_litres
            else:
                # لا يوجد بيانات في جدول barremage
                self.volume_litres = 0
        super().save(*args, **kwargs)


class LecturePompe(models.Model):
    """
    لتسجيل قراءة اليومية لمؤشر المضخة.
    """
    pompe = models.ForeignKey(Engin, on_delete=models.CASCADE, related_name='lectures_pompe')
    date_lecture = models.DateField("Date de lecture", auto_now_add=True)
    index_courant = models.DecimalField(
        "Index courant",
        max_digits=12,
        decimal_places=1,
        help_text="Lecture actuelle de l'index de la pompe"
    )
    # يمكن حساب الاستهلاك منذ آخر قراءة
    consommation_depuis_derniere = models.DecimalField(
        "Consommation depuis dernière lecture (L)",
        max_digits=12,
        decimal_places=1,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'lecture_pompe'
        verbose_name = "Lecture de Pompe"
        verbose_name_plural = "Lectures de Pompe"
        ordering = ['-date_lecture']
        unique_together = ('pompe', 'date_lecture')  # قراءة واحدة فقط في اليوم لكل مضخة

    def __str__(self):
        return f"{self.pompe.libelle} - Index={self.index_courant} le {self.date_lecture}"

    def save(self, *args, **kwargs):
        """
        عند الحفظ، احسب الاستهلاك منذ آخر قراءة.
        """
        try:
            derniere = self.pompe.lectures_pompe.filter(date_lecture__lt=self.date_lecture).order_by('-date_lecture').first()
            if derniere:
                self.consommation_depuis_derniere = self.index_courant - derniere.index_courant
            else:
                # أول قراءة: استهلاك = المؤشر الحالي - المؤشر الأولي
                self.consommation_depuis_derniere = self.index_courant - self.pompe.index_initial
        except Exception as e:
            print(f"❌ خطأ في حساب الاستهلاك لـ {self.pompe}: {e}")
            self.consommation_depuis_derniere = None
        super().save(*args, **kwargs)    

# Notification
class Notification(models.Model):
    TYPE_CHOICES = [
        ('stock_faible', 'Stock Faible'),
        ('tache_retardee', 'Tâche Retardée'),
        ('autre', 'Autre'),
    ]

    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField("Type", max_length=20, choices=TYPE_CHOICES, default='autre')
    message = models.TextField("Message")
    is_read = models.BooleanField("Lu", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_tache = models.ForeignKey('Tache', on_delete=models.SET_NULL, null=True, blank=True)
    related_article = models.CharField("Code Article", max_length=50, blank=True)

    class Meta:
        db_table = 'notification'
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.user.username} - {self.message[:50]}..."        
       
User = get_user_model()

class ArticleAnalysisWorkflow(models.Model):
    """
    تتبع عمليات تحليل المقالات المرتبطة
    كل مستخدم له تحليلاته الخاصة حسب session
    """
    STATUS_CHOICES = [
        ('pending', '⏳ En attente'),
        ('processing', '🔄 En cours'),
        ('completed', '✅ Terminé'),
        ('failed', '❌ Échec'),
        ('expired', '⏰ Expiré'),
    ]
    
    ALGORITHM_CHOICES = [
        ('simple_window', 'Fenêtre temporelle simple (±2 jours)'),
        ('sequence_mining', 'Fouille de séquences avancée'),
        ('frequency_based', 'Basé sur la fréquence'),
        ('hybrid', 'Hybride (Sequence + Fréquence)'),
    ]
    
    # ✅ معرف فريد للتحليل
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # ✅ ربط بالمستخدم والجلسة
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_analyses')
    session_key = models.CharField(max_length=40, db_index=True, help_text="Session Django")
    
    # ✅ المقال المُحلَّل
    cod_art = models.CharField(max_length=50, db_index=True)
    lib_art = models.CharField(max_length=255, blank=True)
    
    # ✅ حالة المعالجة
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    algorithm = models.CharField(max_length=30, choices=ALGORITHM_CHOICES, default='hybrid')
    
    # ✅ معلمات التحليل
    window_days = models.IntegerField(default=2, help_text="Fenêtre temporelle en jours")
    min_support = models.DecimalField(max_digits=5, decimal_places=3, default=0.30, 
                                      help_text="Support minimum (30%)")
    min_confidence = models.DecimalField(max_digits=5, decimal_places=3, default=0.40,
                                        help_text="Confiance minimum (40%)")
    
    # ✅ تقدم المعالجة
    progress_percent = models.IntegerField(default=0)
    total_movements = models.IntegerField(default=0)
    processed_movements = models.IntegerField(default=0)
    
    # ✅ النتائج
    total_related = models.IntegerField(default=0)
    analysis_result = models.JSONField(default=dict, blank=True, 
                                          help_text="Résultats structurés")
    
    # ✅ التوقيت
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(help_text="Expiration des résultats")
    
    # ✅ سجل الأخطاء
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'article_analysis_workflow'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_key', 'status']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['cod_art', 'status']),
        ]
    
    def __str__(self):
        return f"Analysis {self.cod_art} - {self.status}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def mark_completed(self, results):
        """تعيين الحالة كمكتملة مع النتائج"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.analysis_result = results
        self.total_related = len(results.get('related_articles', []))
        self.progress_percent = 100
        self.save()
    
    def mark_failed(self, error):
        """تعيين الحالة كفاشلة مع رسالة الخطأ"""
        self.status = 'failed'
        self.error_message = str(error)[:1000]  # حد أقصى 1000 حرف
        self.save()
    
    def update_progress(self, processed, total):
        """تحديث تقدم المعالجة"""
        self.processed_movements = processed
        self.total_movements = total
        self.progress_percent = int((processed / total * 100) if total > 0 else 0)
        self.save()


class ArticleSequencePattern(models.Model):
    """
    أنماط التسلسل المكتشفة (لإعادة الاستخدام والتخزين المؤقت)
    """
    # المقال المرجعي
    cod_art_ref = models.CharField(max_length=50, db_index=True)
    
    # المقال المرتبط
    cod_art_related = models.CharField(max_length=50, db_index=True)
    
    # ✅ مقاييس القوة
    support_count = models.IntegerField(help_text="Nombre de co-occurrences")
    support_percent = models.DecimalField(max_digits=5, decimal_places=2)
    confidence_percent = models.DecimalField(max_digits=5, decimal_places=2)
    lift_ratio = models.DecimalField(max_digits=10, decimal_places=4, 
                                     help_text="Ratio de lift (>1 = correlation positive)")
    
    # ✅ معلومات التسلسل
    avg_time_gap_hours = models.DecimalField(max_digits=10, decimal_places=2,
                                             help_text="Délai moyen en heures")
    sequence_order = models.CharField(max_length=15, 
                                         choices=[
                                             ('before', 'Avant'),
                                             ('after', 'Après'),
                                             ('simultaneous', 'Simultané')
                                         ])
    
    # ✅ الفترة الزمنية للتحليل
    date_min = models.DateField()
    date_max = models.DateField()
    
    # ✅ مستوى الثقة
    confidence_level = models.CharField(max_length=10,
                                           choices=[
                                               ('high', 'Élevée (>70%)'),
                                               ('medium', 'Moyenne (40-70%)'),
                                               ('low', 'Faible (<40%)')
                                           ])
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'article_sequence_pattern'
        unique_together = ['cod_art_ref', 'cod_art_related', 'date_min', 'date_max']
        indexes = [
            models.Index(fields=['cod_art_ref', 'confidence_level']),
            models.Index(fields=['support_percent', '-confidence_percent']),
        ]
    
    def __str__(self):
        return f"{self.cod_art_ref} → {self.cod_art_related} ({self.confidence_level})"

class ArticleCorrelation(models.Model):
    """
    جدول إحصائي يخزن الارتباطات بين المقالات
    يُحدَّث تزايديًا فقط (incremental update)
    """
    # ✅ المقال المرجعي
    cod_art_ref = models.CharField(max_length=50, db_index=True)
    
    # ✅ المقال المرتبط
    cod_art_related = models.CharField(max_length=50, db_index=True)
    
    # ✅ مقاييس القوة الإحصائية
    support_count = models.IntegerField(
        default=0,
        help_text="عدد المرات التي ظهر فيها المقالان معًا"
    )
    support_percent = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=0.00,
        help_text="نسبة الدعم (support_count / total_movements_ref * 100)"
    )
    confidence_percent = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=0.00,
        help_text="الثقة (support_count / total_movements_related * 100)"
    )
    lift_ratio = models.DecimalField(
        max_digits=10, decimal_places=4,
        default=1.0000,
        help_text="نسبة الرفع (>1 = ارتباط إيجابي)"
    )
    
    # ✅ معلومات التسلسل الزمني
    avg_time_gap_hours = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0.00,
        help_text="متوسط الفاصل الزمني بالساعات بين الحركتين"
    )
    sequence_order = models.CharField(
        max_length=20,
        choices=[
            ('before', 'المقال المرتبط قبل المرجعي'),
            ('after', 'المقال المرتبط بعد المرجعي'),
            ('simultaneous', 'متزامن (نفس الطلبية)'),
            ('mixed', 'مختلط')
        ],
        default='mixed'
    )
    
    # ✅ الفترة الزمنية للتحليل
    date_min = models.DateField(help_text="تاريخ بداية فترة التحليل")
    date_max = models.DateField(help_text="تاريخ نهاية فترة التحليل")
    
    # ✅ آخر تحديث
    last_updated = models.DateTimeField(auto_now=True)
    last_movement_date = models.DateField(
        null=True, blank=True,
        help_text="آخر تاريخ حركة تم تحليلها"
    )
    
    # ✅ مستوى الثقة
    confidence_level = models.CharField(
        max_length=10,
        choices=[
            ('high', 'عالية (≥70%)'),
            ('medium', 'متوسطة (40-70%)'),
            ('low', 'ضعيفة (<40%)')
        ],
        default='low'
    )
    
    # ✅ حالة الصلاحية
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(
        default=False,
        help_text="تم التحقق من الارتباط يدويًا"
    )
    
    class Meta:
        db_table = 'article_correlation'
        unique_together = ['cod_art_ref', 'cod_art_related', 'date_min', 'date_max']
        indexes = [
            models.Index(fields=['cod_art_ref', 'confidence_level']),
            models.Index(fields=['support_percent', '-confidence_percent']),
            models.Index(fields=['last_updated']),
            models.Index(fields=['cod_art_ref', 'is_active']),
        ]
        ordering = ['cod_art_ref', '-support_percent']
    
    def __str__(self):
        return f"{self.cod_art_ref} → {self.cod_art_related} ({self.confidence_level})"
    
    def calculate_lift(self, total_movements_ref, total_movements_related, total_movements_all):
        """حساب نسبة الرفع (Lift Ratio)"""
        if total_movements_all == 0:
            return 1.0
        
        expected = (total_movements_ref / total_movements_all) * (total_movements_related / total_movements_all) * total_movements_all
        if expected == 0:
            return 1.0
        
        self.lift_ratio = round(self.support_count / expected, 4)
        return self.lift_ratio
    
    def update_confidence_level(self):
        """تحديث مستوى الثقة بناءً على النسبة"""
        confidence = float(self.confidence_percent)
        if confidence >= 70:
            self.confidence_level = 'high'
        elif confidence >= 40:
            self.confidence_level = 'medium'
        else:
            self.confidence_level = 'low'


class ArticleCorrelationWorkflow(models.Model):
    """
    تتبع عمليات تحديث الارتباطات لكل جلسة مستخدم
    """
    STATUS_CHOICES = [
        ('pending', '⏳ في الانتظار'),
        ('processing', '🔄 قيد المعالجة'),
        ('completed', '✅ مكتمل'),
        ('failed', '❌ فشل'),
        ('partial', '⚠️ جزئي'),
    ]
    
    # ✅ معرف فريد
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # ✅ ربط بالمستخدم والجلسة
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='correlation_workflows')
    session_key = models.CharField(max_length=40, db_index=True)
    
    # ✅ المقال المُحلَّل
    cod_art = models.CharField(max_length=50, db_index=True)
    
    # ✅ حالة المعالجة
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # ✅ نطاق التحديث
    date_from = models.DateField(help_text="من تاريخ")
    date_to = models.DateField(help_text="إلى تاريخ")
    
    # ✅ تقدم المعالجة
    progress_percent = models.IntegerField(default=0)
    movements_processed = models.IntegerField(default=0)
    movements_total = models.IntegerField(default=0)
    correlations_found = models.IntegerField(default=0)
    
    # ✅ التوقيت
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # ✅ سجل الأخطاء
    error_message = models.TextField(blank=True)
    
    # ✅ هل هذا تحديث تزايدي؟
    is_incremental = models.BooleanField(default=False)
    last_movement_date_processed = models.DateField(
        null=True, blank=True,
        help_text="آخر تاريخ حركة تم معالجته في التحليل السابق"
    )
    
    class Meta:
        db_table = 'article_correlation_workflow'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_key', 'status']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['cod_art', 'status']),
        ]
    
    def __str__(self):
        return f"Workflow {self.cod_art} - {self.status}"
    
    def is_expired(self):
        """التحقق من انتهاء الصلاحية (24 ساعة)"""
        from django.utils import timezone
        return timezone.now() > (self.created_at + timezone.timedelta(hours=24))
    
    def mark_completed(self, correlations_count):
        """تعيين الحالة كمكتملة"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.correlations_found = correlations_count
        self.progress_percent = 100
        self.save()
    
    def mark_failed(self, error):
        """تعيين الحالة كفاشلة"""
        self.status = 'failed'
        self.error_message = str(error)[:1000]
        self.save()
    
    def update_progress(self, processed, total):
        """تحديث تقدم المعالجة"""
        self.movements_processed = processed
        self.movements_total = total
        self.progress_percent = int((processed / total * 100) if total > 0 else 0)
        self.save()        

class NatureBon(models.Model):
    code_nature = models.CharField(max_length=10, primary_key=True, verbose_name="Code Nature")
    libelle = models.CharField(max_length=50, verbose_name="Libellé")
    type_mouvement = models.CharField(max_length=20, null=True, blank=True, verbose_name="Type Mouvement")
    sign = models.IntegerField(default=1, verbose_name="Signe (+1/-1)")

    class Meta:
        db_table = 'naturebon'
        verbose_name = "Nature Bon"

    def __str__(self):
        return f"{self.code_nature} - {self.libelle}"       

class StockEvolutionWorkflow(models.Model):
    """جدول مؤقت لتخزين نتائج stock_evolution للاختبار"""
    session_id = models.CharField(max_length=100, db_index=True)
    cod_art = models.CharField(max_length=50)
    date_b = models.DateField()
    stock_value = models.DecimalField(max_digits=15, decimal_places=2)
    movement_type = models.CharField(max_length=50, blank=True, null=True)
    movement_qty = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    nature_bon = models.CharField(max_length=50, blank=True, null=True)
    class_cout = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_evolution_workflow'
        ordering = ['-date_b']
        indexes = [
            models.Index(fields=['session_id', 'cod_art']),
        ]
    
    def __str__(self):
        return f"{self.cod_art} - {self.date_b} - {self.stock_value}"

class StockEvolution(models.Model):
    """جدول تطور المخزون لكل مقال"""
    id = models.AutoField(primary_key=True)
    cod_art = models.CharField(max_length=50, db_index=True)
    val_art = models.CharField(max_length=10, default='1')
    nat_stock = models.CharField(max_length=10, default='1')
    date_b = models.DateField(db_index=True)
    stock_value = models.DecimalField(max_digits=15, decimal_places=2)
    movement_type = models.CharField(max_length=50, blank=True, null=True)
    movement_qty = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    nature_bon = models.CharField(max_length=50, blank=True, null=True)
    class_cout = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_evolution'
        ordering = ['-date_b']
        indexes = [
            models.Index(fields=['cod_art', 'val_art', 'nat_stock']),
            models.Index(fields=['cod_art', 'date_b']),
        ]
    
    def __str__(self):
        return f"{self.cod_art} - {self.date_b} - {self.stock_value}"
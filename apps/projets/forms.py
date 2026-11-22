# apps/projets/forms.py
from django import forms
from . import models


# ============================================================
# SECTION 1: STRUCTURE DU PROJET
# ============================================================

class ProjetForm(forms.ModelForm):
    """نموذج إنشاء/تعديل مشروع"""
    class Meta:
        model = models.Projet
        fields = [
            'reference', 'nom', 'description', 'type_projet',
            'maitre_ouvrage', 'maitre_oeuvre', 'entreprise_principale',
            'date_debut_prevue', 'date_fin_prevue', 'delai_jours',
            'montant_initial', 'devise', 'statut', 'priorite',
            'lieu', 'chef_projet',
        ]
        widgets = {
            'reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: PRJ-2026-001'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du projet'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'type_projet': forms.Select(attrs={'class': 'form-select'}),
            'maitre_ouvrage': forms.Select(attrs={'class': 'form-select'}),
            'maitre_oeuvre': forms.Select(attrs={'class': 'form-select'}),
            'entreprise_principale': forms.Select(attrs={'class': 'form-select'}),
            'date_debut_prevue': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'date_fin_prevue': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'delai_jours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'montant_initial': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': 0
            }),
            'devise': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'TND'
            }),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'priorite': forms.Select(attrs={'class': 'form-select'}),
            'lieu': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lieu du projet'
            }),
            'chef_projet': forms.Select(attrs={'class': 'form-select'}),
        }


class LotForm(forms.ModelForm):
    """نموذج إنشاء/تعديل Lot"""
    class Meta:
        model = models.Lot
        fields = [
            'numero', 'designation', 'description', 'montant',
            'ordre_execution', 'date_debut', 'date_fin'
        ]
        widgets = {
            'numero': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'designation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Désignation du lot'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': 0
            }),
            'ordre_execution': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'date_debut': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'date_fin': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }


class OuvrageForm(forms.ModelForm):
    """نموذج إنشاء/تعديل Ouvrage"""
    class Meta:
        model = models.Ouvrage
        fields = [
            'code', 'designation', 'description', 'type_ouvrage',
            'quantite', 'unite', 'prix_unitaire', 'date_debut', 'date_fin'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: OV-001'
            }),
            'designation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Désignation de l\'ouvrage'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'type_ouvrage': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Génie civil, Structure...'
            }),
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': 0
            }),
            'unite': forms.Select(attrs={'class': 'form-select'}),
            'prix_unitaire': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': 0
            }),
            'date_debut': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'date_fin': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }


class TacheProjetForm(forms.ModelForm):
    """نموذج إنشاء/تعديل Tâche Projet"""
    class Meta:
        model = models.TacheProjet
        fields = [
            'tache_parente', 'code', 'designation', 'description',
            'responsable', 'personnel_responsable',
            'date_debut_prevue', 'date_fin_prevue',
            'statut', 'priorite', 'heures_prevues',
        ]
        widgets = {
            'tache_parente': forms.Select(attrs={'class': 'form-select'}),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: T-001'
            }),
            'designation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Désignation de la tâche'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'personnel_responsable': forms.Select(attrs={'class': 'form-select'}),
            'date_debut_prevue': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'date_fin_prevue': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'priorite': forms.Select(attrs={'class': 'form-select'}),
            'heures_prevues': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
        }


class ArticleBordereauForm(forms.ModelForm):
    """نموذج إنشاء/تعديل Article de bordereau"""
    class Meta:
        model = models.ArticleBordereau
        fields = [
            'code_bordereau', 'designation', 'description',
            'type_article', 'unite', 'quantite_prevue', 'prix_unitaire'
        ]
        widgets = {
            'code_bordereau': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: BPU-001'
            }),
            'designation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Désignation de l\'article'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
            'type_article': forms.Select(attrs={'class': 'form-select'}),
            'unite': forms.Select(attrs={'class': 'form-select'}),
            'quantite_prevue': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': 0
            }),
            'prix_unitaire': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': 0
            }),
        }


# ============================================================
# SECTION 2: GESTION FINANCIÈRE
# ============================================================

class ContratForm(forms.ModelForm):
    """نموذج إنشاء/تعديل Contrat"""
    class Meta:
        model = models.Contrat
        fields = [
            'numero', 'type_contrat', 'objet', 'montant_initial',
            'delai_jours', 'delai_mois', 'date_signature', 'date_notification',
            'conditions_paiement', 'conditions_revision',
            'retenue_garantie_pourcentage', 'penalites_retard_pourcentage',
            'document',
        ]
        widgets = {
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: M-2026-001'
            }),
            'type_contrat': forms.Select(attrs={'class': 'form-select'}),
            'objet': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'montant_initial': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': 0
            }),
            'delai_jours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'delai_mois': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'date_signature': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'date_notification': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'conditions_paiement': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
            'conditions_revision': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
            'retenue_garantie_pourcentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'max': 100
            }),
            'penalites_retard_pourcentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001',
                'min': 0
            }),
        }


class AvenantForm(forms.ModelForm):
    """نموذج إنشاء/تعديل Avenant"""
    class Meta:
        model = models.Avenant
        fields = [
            'numero', 'objet', 'motif', 'motif_detail',
            'montant_avenant', 'delai_supplementaire',
            'date_signature', 'document'
        ]
        widgets = {
            'numero': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'objet': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'motif': forms.Select(attrs={'class': 'form-select'}),
            'motif_detail': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
            'montant_avenant': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001'
            }),
            'delai_supplementaire': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'date_signature': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }


class DecompteForm(forms.ModelForm):
    """نموذج إنشاء/تعديل Décompte"""
    class Meta:
        model = models.Decompte
        fields = [
            'numero', 'type_decompte', 'date_decompte',
            'montant_brut', 'retenue_garantie', 'penalites',
            'tva_taux', 'observations', 'document'
        ]
        widgets = {
            'numero': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'type_decompte': forms.Select(attrs={'class': 'form-select'}),
            'date_decompte': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'montant_brut': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': 0
            }),
            'retenue_garantie': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': 0
            }),
            'penalites': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': 0
            }),
            'tva_taux': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'max': 100
            }),
            'observations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


class FactureExtraForm(forms.ModelForm):
    """نموذج إنشاء/تعديل Facture Extra"""
    class Meta:
        model = models.FactureExtra
        fields = [
            'numero', 'reference_os', 'description', 'justification',
            'montant_ht', 'tva_taux', 'date_facture', 'document'
        ]
        widgets = {
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: FE-2026-001'
            }),
            'reference_os': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Référence OS'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'justification': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'montant_ht': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': 0
            }),
            'tva_taux': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'max': 100
            }),
            'date_facture': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }


class GarantieForm(forms.ModelForm):
    """نموذج إنشاء/تعديل Garantie"""
    class Meta:
        model = models.Garantie
        fields = [
            'type_garantie', 'reference', 'organisme_garant',
            'montant', 'date_emission', 'date_expiration',
            'observations', 'document'
        ]
        widgets = {
            'type_garantie': forms.Select(attrs={'class': 'form-select'}),
            'reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Référence de la garantie'
            }),
            'organisme_garant': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Banque de Tunisie'
            }),
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': 0
            }),
            'date_emission': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'date_expiration': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'observations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


# ============================================================
# SECTION 3: GESTION ADMINISTRATIVE
# ============================================================

class ReunionForm(forms.ModelForm):
    """نموذج إنشاء/تعديل Réunion"""
    class Meta:
        model = models.Reunion
        fields = [
            'numero', 'type_reunion', 'objet', 'date_reunion',
            'lieu', 'duree_heures', 'animateur',
            'ordre_jour', 'decisions', 'document'
        ]
        widgets = {
            'numero': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'type_reunion': forms.Select(attrs={'class': 'form-select'}),
            'objet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Objet de la réunion'
            }),
            'date_reunion': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'lieu': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lieu'
            }),
            'duree_heures': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'min': 0.5
            }),
            'animateur': forms.Select(attrs={'class': 'form-select'}),
            'ordre_jour': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'decisions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


class CorrespondanceForm(forms.ModelForm):
    """نموذج إنشاء/تعديل Correspondance"""
    class Meta:
        model = models.Correspondance
        fields = [
            'reference', 'type_correspondance', 'direction',
            'date_document', 'date_reception_envoi',
            'expediteur', 'destinataire', 'objet',
            'contenu', 'correspondance_parente', 'document'
        ]
        widgets = {
            'reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Référence'
            }),
            'type_correspondance': forms.Select(attrs={'class': 'form-select'}),
            'direction': forms.Select(attrs={'class': 'form-select'}),
            'date_document': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'date_reception_envoi': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'expediteur': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Expéditeur'
            }),
            'destinataire': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Destinataire'
            }),
            'objet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Objet'
            }),
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'correspondance_parente': forms.Select(attrs={'class': 'form-select'}),
        }


class CompteRenduForm(forms.ModelForm):
    """نموذج إنشاء/تعديل Compte Rendu"""
    class Meta:
        model = models.CompteRendu
        fields = [
            'reunion', 'numero', 'type_cr', 'date_cr',
            'periode_du', 'periode_au', 'objet', 'contenu', 'document'
        ]
        widgets = {
            'reunion': forms.Select(attrs={'class': 'form-select'}),
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: CR-2026-001'
            }),
            'type_cr': forms.Select(attrs={'class': 'form-select'}),
            'date_cr': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'periode_du': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'periode_au': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'objet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Objet du compte rendu'
            }),
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6
            }),
        }


class SuspensionForm(forms.ModelForm):
    """نموذج إنشاء/تعديل Suspension"""
    class Meta:
        model = models.Suspension
        fields = [
            'motif', 'motif_detail', 'date_debut',
            'date_fin_prevue', 'delai_accorde', 'reference_os', 'document'
        ]
        widgets = {
            'motif': forms.Select(attrs={'class': 'form-select'}),
            'motif_detail': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'date_debut': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'date_fin_prevue': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'delai_accorde': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'reference_os': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Référence OS'
            }),
        }


class LivrableForm(forms.ModelForm):
    """نموذج إنشاء/تعديل Livrable"""
    class Meta:
        model = models.Livrable
        fields = [
            'designation', 'description', 'type_livrable',
            'date_echeance', 'version', 'document'
        ]
        widgets = {
            'designation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Désignation du livrable'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'type_livrable': forms.Select(attrs={'class': 'form-select'}),
            'date_echeance': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'version': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
        }


# ============================================================
# SECTION 4: GED
# ============================================================

class GedDocumentForm(forms.ModelForm):
    """نموذج رفع وثيقة GED"""
    class Meta:
        model = models.GedDocument
        fields = ['titre', 'reference', 'categorie', 'description', 'fichier']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre du document'
            }),
            'reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Référence'
            }),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'fichier': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.png,.tif'
            }),
        }

    def clean_fichier(self):
        """التحقق من حجم الملف (max 10 MB)"""
        fichier = self.cleaned_data.get('fichier')
        if fichier and fichier.size > 10 * 1024 * 1024:
            raise forms.ValidationError(
                "La taille du fichier ne doit pas dépasser 10 MB."
            )
        return fichier


# ============================================================
# SECTION 5: INTÉGRATIONS (RH & MATÉRIEL)
# ============================================================

class AffectationRhForm(forms.ModelForm):
    """نموذج تعيين RH على مشروع"""
    class Meta:
        model = models.AffectationRh
        fields = [
            'personnel', 'tache', 'role',
            'date_debut', 'date_fin', 'pourcentage_temps', 'heures_prevues'
        ]
        widgets = {
            'personnel': forms.Select(attrs={'class': 'form-select'}),
            'tache': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Chef d\'équipe, Ingénieur...'
            }),
            'date_debut': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'date_fin': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'pourcentage_temps': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'max': 100
            }),
            'heures_prevues': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
        }


class MobilisationMaterielForm(forms.ModelForm):
    """نموذج تعبئة matériel sur projet"""
    class Meta:
        model = models.MobilisationMateriel
        fields = [
            'engin', 'equipement', 'tache', 'type_mobilisation',
            'date_debut', 'date_fin', 'heures_utilisees', 'cout'
        ]
        widgets = {
            'engin': forms.Select(attrs={'class': 'form-select'}),
            'equipement': forms.Select(attrs={'class': 'form-select'}),
            'tache': forms.Select(attrs={'class': 'form-select'}),
            'type_mobilisation': forms.Select(attrs={'class': 'form-select'}),
            'date_debut': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'date_fin': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'heures_utilisees': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'cout': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                                'min': 0
            }),
        }

    def clean(self):
        """التحقق من أن Engin أو Equipement محدد على الأقل"""
        cleaned_data = super().clean()
        engin = cleaned_data.get('engin')
        equipement = cleaned_data.get('equipement')

        if not engin and not equipement:
            raise forms.ValidationError(
                "Vous devez sélectionner au moins un engin ou un équipement."
            )
        if engin and equipement:
            raise forms.ValidationError(
                "Vous ne pouvez sélectionner qu'un engin OU un équipement, pas les deux."
            )
        return cleaned_data
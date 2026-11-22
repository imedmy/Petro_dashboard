# core/forms.py

from django import forms
from .models import ArticleFamily, Caracteristique, NatureStock, ValeurArticle, EtapeDossier, Citerne, Barremage, Engin, Equipement, LectureIndex, ConsommationCarburant, LectureJauge, LecturePompe, service

class serviceForm(forms.ModelForm):
    class Meta:
        model = service
        fields = ['nom', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: TRANSPORT, FORAGE'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'nom': "Nom du service",
            'description': "Description (facultatif)"
        }
        
class ArticleFamilyForm(forms.ModelForm):
    """
    نموذج لإضافة أو تعديل عائلة ترميز السلع.
    يدعم اختيار العائلة الأم عبر حقل نصي فقط للقراءة + حقل مخفي لـ ID.
    """
    parent_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput(),
        label="Famille parente (ID)"
    )
    parent_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control-plaintext',
            'placeholder': 'Choisissez une famille parente...'
        }),
        label="Famille parente"
    )

    class Meta:
        model = ArticleFamily
        fields = ['name', 'code_segment', 'description', 'parent_id', 'parent_name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la famille'}),
            'code_segment': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '5',
                'pattern': '[0-9]*',
                'title': 'Entrez 1 à 5 chiffres'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description optionnelle...'
            })
        }
        labels = {
            'name': 'Nom de la famille *',
            'code_segment': 'Segment de code (1-5 chiffres) *',
            'description': 'Description',
        }
        help_texts = {
            'code_segment': 'Utilisez uniquement des chiffres (ex: 001).',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تعبئة القيم عند التعديل
        if self.instance and self.instance.pk and self.instance.parent:
            self.fields['parent_id'].initial = self.instance.parent.id
            self.fields['parent_name'].initial = f"{self.instance.parent.full_code} - {self.instance.parent.name}"

    def clean(self):
        cleaned_data = super().clean()
        parent_id = cleaned_data.get('parent_id')

        # ربط الكائن الأب إن وُجد
        if parent_id:
            try:
                parent_obj = ArticleFamily.objects.get(id=parent_id)
                cleaned_data['parent'] = parent_obj
            except ArticleFamily.DoesNotExist:
                raise forms.ValidationError({
                    'parent_id': "La famille parente sélectionnée n'existe pas."
                })
        else:
            cleaned_data['parent'] = None

        return cleaned_data

    def save(self, commit=True):
        # تأكد من تعيين parent قبل الحفظ
        self.instance.parent = self.cleaned_data.get('parent')
        return super().save(commit=commit)


class CaracteristiqueForm(forms.ModelForm):
    """
    نموذج لإدارة الخصائص التقنية.
    يدعم اختيار الخاصية الأم عبر نافذة بحث (Lookup Panel).
    """
    parent_name = forms.CharField(
        label="Caractéristique parente",
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',
            'placeholder': 'Sélectionnez une caractéristique parente...'
        })
    )
    parent_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Caracteristique
        fields = ['nom', 'type_valeur', 'unite', 'utilisable_dans_recherche', 'parent_id']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Diamètre, Puissance, Matériau...'
            }),
            'type_valeur': forms.Select(attrs={'class': 'form-control'}),
            'unite': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: mm, kg, kW...'
            }),
            'utilisable_dans_recherche': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nom': 'Nom de la caractéristique *',
            'type_valeur': 'Type de valeur *',
            'unite': 'Unité (optionnel)',
            'utilisable_dans_recherche': 'Utilisable dans les filtres'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تعبئة اسم الخاصية الأم عند التعديل
        if self.instance.pk and self.instance.parent:
            self.fields['parent_name'].initial = self.instance.parent.nom

    def clean(self):
        cleaned_data = super().clean()
        parent_id = cleaned_data.get('parent_id')

        if parent_id:
            try:
                parent_obj = Caracteristique.objects.get(id=parent_id)
                cleaned_data['parent'] = parent_obj
            except Caracteristique.DoesNotExist:
                raise forms.ValidationError({
                    'parent_id': "La caractéristique parente sélectionnée est introuvable."
                })
        else:
            cleaned_data['parent'] = None

        return cleaned_data

    def save(self, commit=True):
        # تعيين الخاصية الأم قبل الحفظ
        self.instance.parent = self.cleaned_data.get('parent')
        return super().save(commit=commit)

class NatureStockForm(forms.ModelForm):
    class Meta:
        model = NatureStock
        fields = ['code_nature', 'libelle_nature']
        widgets = {
            'code_nature': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Ex: 1, 2, 3...'
            }),
            'libelle_nature': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Stock physique, En transit...'
            })
        }
        labels = {
            'code_nature': 'Code Nature',
            'libelle_nature': 'Libellé de la Nature'
        }        
        
class ValeurArticleForm(forms.ModelForm):
    class Meta:
        model = ValeurArticle
        fields = ['code_valeur', 'libelle_valeur']
        widgets = {
            'code_valeur': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Ex: 1, 2, 3...'
            }),
            'libelle_valeur': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 100%, 75%, En bon état...'
            })
        }
        labels = {
            'code_valeur': 'Code Valeur',
            'libelle_valeur': 'Libellé de la Valeur'
        }        

class EtapeDossierForm(forms.ModelForm):
    class Meta:
        model = EtapeDossier
        fields = ['code_etape', 'libelle_etape', 'influence']
        widgets = {
            'code_etape': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Ex: 1, 2, 3...'
            }),
            'libelle_etape': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Création, Validation...'
            }),
            'influence': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'code_etape': 'Code Étape',
            'libelle_etape': 'Libellé de l\'Étape',
            'influence': 'Influence sur le dossier'
        }

class CiterneForm(forms.ModelForm):
    class Meta:
        model = Citerne
        fields = [
            'code_citerne',
            'nom',
            'type_citerne',
            'diametre_cm',
            'longueur_cm',
            'epaisseur_cm',
            'cod_art_fluide',
            'actif'
        ]
        widgets = {
            'code_citerne': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'type_citerne': forms.Select(attrs={'class': 'form-select'}),
            'diametre_cm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'longueur_cm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'epaisseur_cm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cod_art_fluide': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: GASOIL, DIESEL'
            }),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'cod_art_fluide': "Code Article du Fluide"
        }     

class BarremageForm(forms.ModelForm):
    class Meta:
        model = Barremage
        fields = ['hauteur_cm', 'volume_litres']
        widgets = {
            'hauteur_cm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'volume_litres': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
        }        

class EnginForm(forms.ModelForm):
    class Meta:
        model = Engin
        fields = '__all__'
        widgets = {
            'libelle': forms.TextInput(attrs={'class': 'form-control'}),
            'type_engin': forms.Select(attrs={'class': 'form-select'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control'}),
            'immatriculation': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_bp': forms.TextInput(attrs={'class': 'form-control'}),
            'capacite_reservoir': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'type_carburant': forms.TextInput(attrs={'class': 'form-control'}),
            'index_initial': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'marque': forms.TextInput(attrs={'class': 'form-control'}),
            'genre': forms.TextInput(attrs={'class': 'form-control'}),
            'date_1ere_mise_en_circulation': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_derniere_visite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'puissance_fiscale': forms.TextInput(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-select'}),
            'situation': forms.Select(attrs={'class': 'form-select'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EquipementForm(forms.ModelForm):
    class Meta:
        model = Equipement
        fields = '__all__'
        widgets = {
            'libelle': forms.TextInput(attrs={'class': 'form-control'}),
            'type_equipement': forms.Select(attrs={'class': 'form-select'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_bp': forms.TextInput(attrs={'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class LectureIndexForm(forms.ModelForm):
    class Meta:
        model = LectureIndex
        fields = ['engin', 'index_courant']
        widgets = {
            'engin': forms.Select(attrs={'class': 'form-select'}),
            'index_courant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }

class ConsommationCarburantForm(forms.ModelForm):
    class Meta:
        model = ConsommationCarburant
        fields = ['engin', 'date_ravitaillement', 'volume_l', 'type_carburant', 'observation']
        widgets = {
            'engin': forms.Select(attrs={'class': 'form-select'}),
            'date_ravitaillement': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'volume_l': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'type_carburant': forms.Select(attrs={'class': 'form-select'}),
            'observation': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }        

class LectureJaugeForm(forms.ModelForm):
    class Meta:
        model = LectureJauge
        fields = ['citerne', 'hauteur_cm']
        widgets = {
            'citerne': forms.Select(attrs={'class': 'form-select'}),
            'hauteur_cm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class LecturePompeForm(forms.ModelForm):
    class Meta:
        model = LecturePompe
        fields = ['pompe', 'index_courant']
        widgets = {
            'pompe': forms.Select(attrs={'class': 'form-select'}),
            'index_courant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }        
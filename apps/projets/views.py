# apps/projets/views.py
# ============================================================
# IMPORTS
# ============================================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, Avg, F
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator

from . import models, forms


# ============================================================
# SECTION 1: DASHBOARD
# ============================================================

@login_required
def dashboard_projets(request):
    """لوحة التحكم الرئيسية للمشاريع"""
    projets = models.Projet.objects.filter(actif=True)

    context = {
        'stats': {
            'total': projets.count(),
            'en_cours': projets.filter(statut='EN_COURS').count(),
            'planifie': projets.filter(statut='PLANIFIE').count(),
            'suspendus': projets.filter(statut='SUSPENDU').count(),
            'termines': projets.filter(statut='ACHEVE').count(),
            'resilies': projets.filter(statut='RESILIE').count(),
            'montant_total': projets.aggregate(
                total=Sum('montant_final')
            )['total'] or 0,
            'avancement_moyen': projets.aggregate(
                avg=Avg('pourcentage_avancement')
            )['avg'] or 0,
        },
        'projets_en_cours': projets.filter(
            statut='EN_COURS'
        ).select_related(
            'type_projet', 'maitre_ouvrage', 'chef_projet'
        ).order_by('-pourcentage_avancement')[:10],
        'projets_en_retard': projets.filter(
            statut='EN_COURS',
            date_fin_prevue__lt=timezone.now().date()
        ).select_related(
            'type_projet', 'maitre_ouvrage', 'chef_projet'
        ),
        'repartition_par_type': projets.values(
            'type_projet__libelle'
        ).annotate(
            total=Count('id')
        ).order_by('-total'),
        'repartition_par_statut': projets.values(
            'statut'
        ).annotate(
            total=Count('id')
        ),
    }
    return render(request, 'projets/dashboard.html', context)


# ============================================================
# SECTION 2: PROJETS (CRUD)
# ============================================================

@login_required
def projet_list(request):
    """قائمة المشاريع مع الفلترة والبحث"""
    projets = models.Projet.objects.filter(actif=True).select_related(
        'type_projet', 'maitre_ouvrage', 'chef_projet'
    )

    # --- الفلترة ---
    statut = request.GET.get('statut')
    if statut:
        projets = projets.filter(statut=statut)

    type_projet = request.GET.get('type_projet')
    if type_projet:
        projets = projets.filter(type_projet_id=type_projet)

    search = request.GET.get('search')
    if search:
        projets = projets.filter(
            Q(reference__icontains=search) |
            Q(nom__icontains=search) |
            Q(description__icontains=search) |
            Q(lieu__icontains=search)
        )

    # --- Pagination ---
    paginator = Paginator(projets, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- الإحصائيات (لجميع المشاريع بدون فلترة) ---
    all_projets = models.Projet.objects.filter(actif=True)
    stats = {
        'total': all_projets.count(),
        'en_cours': all_projets.filter(statut='EN_COURS').count(),
        'termines': all_projets.filter(statut='ACHEVE').count(),
        'montant_total': all_projets.aggregate(
            total=Sum('montant_final')
        )['total'] or 0,
    }

    context = {
        'page_obj': page_obj,
        'projets': page_obj,
        'stats': stats,
        'types_projets': models.TypeProjet.objects.filter(actif=True),
        'statuts': models.Projet.STATUTS,
    }
    return render(request, 'projets/projets_list.html', context)


@login_required
def projet_create(request):
    """إنشاء مشروع جديد"""
    if request.method == 'POST':
        form = forms.ProjetForm(request.POST)
        if form.is_valid():
            projet = form.save(commit=False)
            projet.created_by = request.user
            projet.montant_final = projet.montant_initial
            projet.save()
            messages.success(
                request,
                f'Projet {projet.reference} créé avec succès.'
            )
            return redirect('projets:projet_detail', pk=projet.pk)
    else:
        form = forms.ProjetForm()

    return render(request, 'projets/projet_form.html', {
        'form': form,
        'title': 'Nouveau projet',
        'action': 'Créer'
    })


@login_required
def projet_detail(request, pk):
    """عرض تفاصيل المشروع"""
    projet = get_object_or_404(
        models.Projet.objects.select_related(
            'type_projet', 'maitre_ouvrage', 'maitre_oeuvre',
            'entreprise_principale', 'chef_projet'
        ),
        pk=pk
    )
    lots = projet.lots.all().prefetch_related('ouvrages__taches')

    # --- الإحصائيات ---
    stats = {
        'lots_count': lots.count(),
        'ouvrages_count': models.Ouvrage.objects.filter(
            lot__projet=projet
        ).count(),
        'taches_count': models.TacheProjet.objects.filter(
            ouvrage__lot__projet=projet
        ).count(),
        'taches_terminees': models.TacheProjet.objects.filter(
            ouvrage__lot__projet=projet,
            statut='TERMINEE'
        ).count(),
        'realisations_count': projet.realisations.count(),
        'realisations_en_cours': projet.realisations.filter(statut='EN_COURS').count(),
        'realisations_terminees': projet.realisations.filter(statut='TERMINE').count(),
        'realisations_cout_total': projet.realisations.aggregate(total=Sum('details__cout_total'))['total'] or 0,
    
        'decomptes_count': projet.decomptes.count(),
        'avenants_count': (
            projet.contrat.avenants.count()
            if hasattr(projet, 'contrat') and projet.contrat
            else 0
        ),
        'reunions_count': projet.reunions.count(),
        'documents_count': projet.ged_documents.count(),
        'correspondances_count': projet.correspondances.count(),
        'garanties_count': projet.garanties.count(),
    }

    # --- آخر 5 وثائق مرفوعة ---
    activites_recentes = projet.ged_documents.order_by('-created_at')[:5]

    context = {
        'projet': projet,
        'lots': lots,
        'stats': stats,
        'activites_recentes': activites_recentes,
    }
    return render(request, 'projets/projet_detail.html', context)


@login_required
def projet_update(request, pk):
    """تعديل مشروع"""
    projet = get_object_or_404(models.Projet, pk=pk)

    if request.method == 'POST':
        form = forms.ProjetForm(request.POST, instance=projet)
        if form.is_valid():
            form.save()
            messages.success(request, 'Projet mis à jour avec succès.')
            return redirect('projets:projet_detail', pk=projet.pk)
    else:
        form = forms.ProjetForm(instance=projet)

    return render(request, 'projets/projet_form.html', {
        'form': form,
        'projet': projet,
        'title': f'Modifier le projet {projet.reference}',
        'action': 'Enregistrer'
    })


@login_required
def projet_delete(request, pk):
    """حذف مشروع (soft delete)"""
    projet = get_object_or_404(models.Projet, pk=pk)

    if request.method == 'POST':
        projet.actif = False
        projet.save()
        messages.success(request, 'Projet désactivé avec succès.')
        return redirect('projets:projet_list')

    return render(request, 'projets/projet_confirm_delete.html', {
        'projet': projet
    })


# ============================================================
# SECTION 3: LOTS (CRUD)
# ============================================================

@login_required
def lot_create(request, projet_id):
    """إنشاء Lot جديد"""
    projet = get_object_or_404(models.Projet, pk=projet_id)

    if request.method == 'POST':
        form = forms.LotForm(request.POST)
        if form.is_valid():
            lot = form.save(commit=False)
            lot.projet = projet
            lot.save()
            messages.success(
                request,
                f'Lot {lot.numero} créé avec succès.'
            )
            return redirect('projets:projet_detail', pk=projet.pk)
    else:
        # حساب الرقم التالي تلقائياً
        dernier_numero = projet.lots.order_by('-numero').values_list(
            'numero', flat=True
        ).first() or 0
        form = forms.LotForm(initial={
            'numero': dernier_numero + 1
        })

    return render(request, 'projets/lot_form.html', {
        'form': form,
        'projet': projet,
        'title': f'Nouveau lot - {projet.reference}'
    })


@login_required
def lot_detail(request, pk):
    """عرض تفاصيل Lot"""
    lot = get_object_or_404(
        models.Lot.objects.select_related('projet'),
        pk=pk
    )
    ouvrages = lot.ouvrages.all().prefetch_related('taches', 'articles')

    context = {
        'lot': lot,
        'ouvrages': ouvrages,
    }
    return render(request, 'projets/lot_detail.html', context)


@login_required
def lot_update(request, pk):
    """تعديل Lot"""
    lot = get_object_or_404(models.Lot, pk=pk)

    if request.method == 'POST':
        form = forms.LotForm(request.POST, instance=lot)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lot mis à jour avec succès.')
            return redirect('projets:lot_detail', pk=lot.pk)
    else:
        form = forms.LotForm(instance=lot)

    return render(request, 'projets/lot_form.html', {
        'form': form,
        'lot': lot,
        'projet': lot.projet,
        'title': f'Modifier lot {lot.numero}'
    })


# ============================================================
# SECTION 4: OUVRAGES (CRUD)
# ============================================================

@login_required
def ouvrage_create(request, lot_id):
    """إنشاء Ouvrage جديد"""
    lot = get_object_or_404(models.Lot, pk=lot_id)

    if request.method == 'POST':
        form = forms.OuvrageForm(request.POST)
        if form.is_valid():
            ouvrage = form.save(commit=False)
            ouvrage.lot = lot
            ouvrage.save()
            messages.success(
                request,
                f'Ouvrage {ouvrage.code} créé avec succès.'
            )
            return redirect('projets:lot_detail', pk=lot.pk)
    else:
        form = forms.OuvrageForm()

    return render(request, 'projets/ouvrage_form.html', {
        'form': form,
        'lot': lot,
        'projet': lot.projet,
        'title': f'Nouvel ouvrage - {lot.designation}'
    })


@login_required
def ouvrage_detail(request, pk):
    """عرض تفاصيل Ouvrage"""
    ouvrage = get_object_or_404(
        models.Ouvrage.objects.select_related('lot__projet'),
        pk=pk
    )
    taches = ouvrage.taches.all().prefetch_related('articles')
    articles = ouvrage.articles.all()

    context = {
        'ouvrage': ouvrage,
        'taches': taches,
        'articles': articles,
    }
    return render(request, 'projets/ouvrage_detail.html', context)


# ============================================================
# SECTION 5: TÂCHES PROJET (CRUD)
# ============================================================

@login_required
def tache_create(request, ouvrage_id):
    """إنشاء Tâche Projet جديدة"""
    ouvrage = get_object_or_404(
        models.Ouvrage.objects.select_related('lot__projet'),
        pk=ouvrage_id
    )

    if request.method == 'POST':
        form = forms.TacheProjetForm(request.POST)
        if form.is_valid():
            tache = form.save(commit=False)
            tache.ouvrage = ouvrage
            tache.save()
            form.save_m2m()  # لحفظ التبعيات (ManyToMany)
            messages.success(
                request,
                f'Tâche {tache.code} créée avec succès.'
            )
            return redirect('projets:ouvrage_detail', pk=ouvrage.pk)
    else:
        form = forms.TacheProjetForm()

    return render(request, 'projets/tache_form.html', {
        'form': form,
        'ouvrage': ouvrage,
        'projet': ouvrage.lot.projet,
        'title': f'Nouvelle tâche - {ouvrage.designation}'
    })


@login_required
def tache_detail(request, pk):
    """عرض تفاصيل Tâche"""
    tache = get_object_or_404(
        models.TacheProjet.objects.select_related(
            'ouvrage__lot__projet',
            'responsable',
            'personnel_responsable'
        ),
        pk=pk
    )
    sous_taches = tache.sous_taches.all()
    articles = tache.articles.all()

    context = {
        'tache': tache,
        'sous_taches': sous_taches,
        'articles': articles,
    }
    return render(request, 'projets/tache_detail.html', context)


# ============================================================
# SECTION 6: ARTICLES DE BORDEREAU
# ============================================================

@login_required
def article_create(request, ouvrage_id):
    """إنشاء Article de bordereau جديد"""
    ouvrage = get_object_or_404(models.Ouvrage, pk=ouvrage_id)

    if request.method == 'POST':
        form = forms.ArticleBordereauForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.ouvrage = ouvrage
            article.save()
            messages.success(
                request,
                f'Article {article.code_bordereau} créé avec succès.'
            )
            return redirect('projets:ouvrage_detail', pk=ouvrage.pk)
    else:
        form = forms.ArticleBordereauForm()

    return render(request, 'projets/article_form.html', {
        'form': form,
        'ouvrage': ouvrage,
        'projet': ouvrage.lot.projet,
        'title': 'Nouvel article de bordereau'
    })

# ============================================================
# SECTION 7: CONTRATS & AVENANTS
# ============================================================

@login_required
def contrat_create(request, projet_id):
    """إنشاء/تعديل Contrat (OneToOne مع Projet)"""
    projet = get_object_or_404(models.Projet, pk=projet_id)

    # التحقق من وجود contrat سابق
    try:
        contrat = projet.contrat
    except models.Contrat.DoesNotExist:
        contrat = None

    if request.method == 'POST':
        form = forms.ContratForm(
            request.POST, request.FILES, instance=contrat
        )
        if form.is_valid():
            contrat = form.save(commit=False)
            contrat.projet = projet
            contrat.save()

            # تحديث montant_initial du projet
            projet.montant_initial = contrat.montant_initial
            projet.delai_jours = contrat.delai_jours
            projet.save(update_fields=['montant_initial', 'delai_jours'])

            messages.success(request, 'Contrat enregistré avec succès.')
            return redirect('projets:projet_detail', pk=projet.pk)
    else:
        form = forms.ContratForm(
            instance=contrat,
            initial={
                'montant_initial': projet.montant_initial,
                'delai_jours': projet.delai_jours,
            }
        )

    return render(request, 'projets/contrat_form.html', {
        'form': form,
        'projet': projet,
        'contrat': contrat,
        'title': 'Modifier contrat' if contrat else 'Nouveau contrat'
    })


@login_required
def avenant_create(request, projet_id):
    """إنشاء Avenant (ملحق)"""
    projet = get_object_or_404(models.Projet, pk=projet_id)

    # التحقق من وجود contrat
    try:
        contrat = projet.contrat
    except models.Contrat.DoesNotExist:
        messages.error(
            request,
            'Veuillez d\'abord créer un contrat pour ce projet.'
        )
        return redirect('projets:projet_detail', pk=projet.pk)

    if request.method == 'POST':
        form = forms.AvenantForm(request.POST, request.FILES)
        if form.is_valid():
            avenant = form.save(commit=False)
            avenant.contrat = contrat
            avenant.save()

            # إعادة حساب montant_final du projet
            projet.calculer_montant_final()

            messages.success(
                request,
                f'Avenant n°{avenant.numero} créé avec succès.'
            )
            return redirect('projets:projet_detail', pk=projet.pk)
    else:
        # حساب الرقم التالي تلقائياً
        dernier_numero = contrat.avenants.order_by('-numero').values_list(
            'numero', flat=True
        ).first() or 0
        form = forms.AvenantForm(initial={
            'numero': dernier_numero + 1
        })

    return render(request, 'projets/avenant_form.html', {
        'form': form,
        'projet': projet,
        'contrat': contrat,
        'title': 'Nouvel avenant'
    })


# ============================================================
# SECTION 8: DÉCOMPTES
# ============================================================

@login_required
def decompte_list(request, projet_id):
    """قائمة Décomptes لمشروع معين"""
    projet = get_object_or_404(models.Projet, pk=projet_id)
    decomptes = projet.decomptes.all().order_by('-numero')

    # إحصائيات
    stats = {
        'total': decomptes.count(),
        'montant_total': decomptes.aggregate(
            total=Sum('montant_net')
        )['total'] or 0,
        'paye': decomptes.filter(statut='PAYE').count(),
        'en_cours': decomptes.filter(
            statut__in=['PREPARE', 'SOUMIS', 'VALIDE']
        ).count(),
    }

    context = {
        'projet': projet,
        'decomptes': decomptes,
        'stats': stats,
    }
    return render(request, 'projets/decompte_list.html', context)


@login_required
def decompte_create(request, projet_id):
    """إنشاء Décompte جديد"""
    projet = get_object_or_404(models.Projet, pk=projet_id)

    if request.method == 'POST':
        form = forms.DecompteForm(request.POST, request.FILES)
        if form.is_valid():
            decompte = form.save(commit=False)
            decompte.projet = projet
            decompte.save()

            # حساب TVA والمبلغ الصافي
            decompte.calculer_montants()

            messages.success(
                request,
                f'Décompte n°{decompte.numero} créé avec succès.'
            )
            return redirect('projets:decompte_list', projet_id=projet.pk)
    else:
        # حساب الرقم التالي تلقائياً
        dernier_numero = projet.decomptes.order_by('-numero').values_list(
            'numero', flat=True
        ).first() or 0
        form = forms.DecompteForm(initial={
            'numero': dernier_numero + 1,
            'tva_taux': 19,  # TVA التونسية
        })

    return render(request, 'projets/decompte_form.html', {
        'form': form,
        'projet': projet,
        'title': 'Nouveau décompte'
    })


# ============================================================
# SECTION 9: FACTURES EXTRA & GARANTIES
# ============================================================

@login_required
def facture_extra_create(request, projet_id):
    """إنشاء Facture Extra (أشغال إضافية)"""
    projet = get_object_or_404(models.Projet, pk=projet_id)

    if request.method == 'POST':
        form = forms.FactureExtraForm(request.POST, request.FILES)
        if form.is_valid():
            facture = form.save(commit=False)
            facture.projet = projet

            # حساب TVA و TTC تلقائياً
            facture.tva_montant = facture.montant_ht * (facture.tva_taux / 100)
            facture.montant_ttc = facture.montant_ht + facture.tva_montant
            facture.save()

            messages.success(
                request,
                f'Facture extra {facture.numero} créée avec succès.'
            )
            return redirect('projets:projet_detail', pk=projet.pk)
    else:
        form = forms.FactureExtraForm(initial={'tva_taux': 19})

    return render(request, 'projets/facture_extra_form.html', {
        'form': form,
        'projet': projet,
        'title': 'Nouvelle facture extra'
    })


@login_required
def garantie_create(request, projet_id):
    """إنشاء Garantie (ضمان)"""
    projet = get_object_or_404(models.Projet, pk=projet_id)

    if request.method == 'POST':
        form = forms.GarantieForm(request.POST, request.FILES)
        if form.is_valid():
            garantie = form.save(commit=False)
            garantie.projet = projet
            garantie.save()
            messages.success(request, 'Garantie enregistrée avec succès.')
            return redirect('projets:projet_detail', pk=projet.pk)
    else:
        form = forms.GarantieForm()

    return render(request, 'projets/garantie_form.html', {
        'form': form,
        'projet': projet,
        'title': 'Nouvelle garantie'
    })


# ============================================================
# SECTION 10: RÉUNIONS
# ============================================================

@login_required
def reunion_list(request, projet_id):
    """قائمة Réunions لمشروع معين"""
    projet = get_object_or_404(models.Projet, pk=projet_id)
    reunions = projet.reunions.all().order_by('-date_reunion')

    context = {
        'projet': projet,
        'reunions': reunions,
    }
    return render(request, 'projets/reunion_list.html', context)


@login_required
def reunion_create(request, projet_id):
    """إنشاء Réunion جديدة"""
    projet = get_object_or_404(models.Projet, pk=projet_id)

    if request.method == 'POST':
        form = forms.ReunionForm(request.POST, request.FILES)
        if form.is_valid():
            reunion = form.save(commit=False)
            reunion.projet = projet
            reunion.save()
            messages.success(
                request,
                f'Réunion n°{reunion.numero} créée avec succès.'
            )
            return redirect('projets:reunion_list', projet_id=projet.pk)
    else:
        # حساب الرقم التالي تلقائياً
        dernier_numero = projet.reunions.order_by('-numero').values_list(
            'numero', flat=True
        ).first() or 0
        form = forms.ReunionForm(initial={
            'numero': dernier_numero + 1
        })

    return render(request, 'projets/reunion_form.html', {
        'form': form,
        'projet': projet,
        'title': 'Nouvelle réunion'
    })


# ============================================================
# SECTION 11: CORRESPONDANCES
# ============================================================

@login_required
def correspondance_list(request, projet_id):
    """قائمة Correspondances لمشروع معين"""
    projet = get_object_or_404(models.Projet, pk=projet_id)

    # فلترة حسب الاتجاه
    direction = request.GET.get('direction')
    correspondances = projet.correspondances.all().order_by('-date_document')
    if direction:
        correspondances = correspondances.filter(direction=direction)

    context = {
        'projet': projet,
        'correspondances': correspondances,
        'directions': models.Correspondance.DIRECTIONS,
    }
    return render(request, 'projets/correspondance_list.html', context)


@login_required
def correspondance_create(request, projet_id):
    """إنشاء Correspondance جديدة"""
    projet = get_object_or_404(models.Projet, pk=projet_id)

    if request.method == 'POST':
        form = forms.CorrespondanceForm(request.POST, request.FILES)
        if form.is_valid():
            correspondance = form.save(commit=False)
            correspondance.projet = projet
            correspondance.created_by = request.user
            correspondance.save()
            messages.success(request, 'Correspondance enregistrée avec succès.')
            return redirect('projets:correspondance_list', projet_id=projet.pk)
    else:
        form = forms.CorrespondanceForm()

    return render(request, 'projets/correspondance_form.html', {
        'form': form,
        'projet': projet,
        'title': 'Nouvelle correspondance'
    })


# ============================================================
# SECTION 12: COMPTES RENDUS, SUSPENSIONS, LIVRABLES
# ============================================================

@login_required
def compte_rendu_create(request, projet_id):
    """إنشاء Compte Rendu جديد"""
    projet = get_object_or_404(models.Projet, pk=projet_id)

    if request.method == 'POST':
        form = forms.CompteRenduForm(request.POST, request.FILES)
        if form.is_valid():
            cr = form.save(commit=False)
            cr.projet = projet
            cr.redige_par = request.user
            cr.save()
            messages.success(
                request,
                f'Compte rendu {cr.numero} créé avec succès.'
            )
            return redirect('projets:projet_detail', pk=projet.pk)
    else:
        form = forms.CompteRenduForm()

    return render(request, 'projets/compte_rendu_form.html', {
        'form': form,
        'projet': projet,
        'title': 'Nouveau compte rendu'
    })


@login_required
def suspension_create(request, projet_id):
    """إنشاء Suspension (تعليق المشروع)"""
    projet = get_object_or_404(models.Projet, pk=projet_id)

    if request.method == 'POST':
        form = forms.SuspensionForm(request.POST, request.FILES)
        if form.is_valid():
            suspension = form.save(commit=False)
            suspension.projet = projet
            suspension.save()

            # تغيير حالة المشروع إلى SUSPENDU
            projet.statut = 'SUSPENDU'
            projet.save(update_fields=['statut'])

            messages.success(request, 'Suspension enregistrée avec succès.')
            return redirect('projets:projet_detail', pk=projet.pk)
    else:
        form = forms.SuspensionForm()

    return render(request, 'projets/suspension_form.html', {
        'form': form,
        'projet': projet,
        'title': 'Nouvelle suspension'
    })


@login_required
def livrable_create(request, projet_id):
    """إنشاء Livrable جديد"""
    projet = get_object_or_404(models.Projet, pk=projet_id)

    if request.method == 'POST':
        form = forms.LivrableForm(request.POST, request.FILES)
        if form.is_valid():
            livrable = form.save(commit=False)
            livrable.projet = projet
            livrable.save()
            messages.success(
                request,
                f'Livrable "{livrable.designation}" créé avec succès.'
            )
            return redirect('projets:projet_detail', pk=projet.pk)
    else:
        form = forms.LivrableForm()

    return render(request, 'projets/livrable_form.html', {
        'form': form,
        'projet': projet,
        'title': 'Nouveau livrable'
    })


# ============================================================
# SECTION 13: GED (GESTION ÉLECTRONIQUE DES DOCUMENTS)
# ============================================================

@login_required
def ged_list(request, projet_id):
    """قائمة Documents GED لمشروع معين"""
    projet = get_object_or_404(models.Projet, pk=projet_id)
    documents = projet.ged_documents.all().order_by('-created_at')

    # فلترة حسب الفئة
    categorie = request.GET.get('categorie')
    if categorie:
        documents = documents.filter(categorie=categorie)

    # فلترة حسب البحث
    search = request.GET.get('search')
    if search:
        documents = documents.filter(
            Q(titre__icontains=search) |
            Q(reference__icontains=search) |
            Q(description__icontains=search)
        )

    # إحصائيات حسب الفئة
    stats_par_categorie = projet.ged_documents.values(
        'categorie'
    ).annotate(
        total=Count('id')
    ).order_by('-total')

    context = {
        'projet': projet,
        'documents': documents,
        'categories': models.GedDocument.CATEGORIES,
        'stats_par_categorie': stats_par_categorie,
    }
    return render(request, 'projets/ged_list.html', context)


@login_required
def ged_upload(request, projet_id):
    """رفع وثيقة GED جديدة"""
    projet = get_object_or_404(models.Projet, pk=projet_id)

    if request.method == 'POST':
        form = forms.GedDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.projet = projet
            doc.uploaded_by = request.user

            # حفظ معلومات الملف
            if doc.fichier:
                doc.taille = doc.fichier.size
                doc.type_mime = doc.fichier.content_type or ''

            doc.save()

            messages.success(
                request,
                f'Document "{doc.titre}" uploadé avec succès.'
            )
            return redirect('projets:ged_list', projet_id=projet.pk)
    else:
        form = forms.GedDocumentForm()

    return render(request, 'projets/ged_upload.html', {
        'form': form,
        'projet': projet,
        'title': 'Nouveau document'
    })


@login_required
def ged_document_detail(request, pk):
    """عرض تفاصيل وثيقة GED"""
    doc = get_object_or_404(
        models.GedDocument.objects.select_related('projet', 'uploaded_by'),
        pk=pk
    )
    versions = doc.versions.all().order_by('-numero_version')

    context = {
        'doc': doc,
        'versions': versions,
    }
    return render(request, 'projets/ged_document_detail.html', context)


# ============================================================
# SECTION 14: INTÉGRATIONS (RH & MATÉRIEL)
# ============================================================

@login_required
def affectation_rh_create(request, projet_id):
    """تعيين Personnel على مشروع"""
    projet = get_object_or_404(models.Projet, pk=projet_id)

    if request.method == 'POST':
        form = forms.AffectationRhForm(request.POST)
        if form.is_valid():
            affectation = form.save(commit=False)
            affectation.projet = projet
            affectation.save()
            messages.success(
                request,
                'Affectation RH enregistrée avec succès.'
            )
            return redirect('projets:projet_detail', pk=projet.pk)
    else:
        form = forms.AffectationRhForm()

    return render(request, 'projets/affectation_rh_form.html', {
        'form': form,
        'projet': projet,
        'title': 'Nouvelle affectation RH'
    })


@login_required
def affectation_rh_list(request, projet_id):
    """قائمة affectations RH لمشروع معين"""
    projet = get_object_or_404(models.Projet, pk=projet_id)
    affectations = projet.affectations_rh.select_related(
        'personnel', 'tache'
    ).order_by('-date_debut')

    context = {
        'projet': projet,
        'affectations': affectations,
    }
    return render(request, 'projets/affectation_rh_list.html', context)


@login_required
def mobilisation_materiel_create(request, projet_id):
    """تعبئة matériel (Engin/Equipement) sur projet"""
    projet = get_object_or_404(models.Projet, pk=projet_id)

    if request.method == 'POST':
        form = forms.MobilisationMaterielForm(request.POST)
        if form.is_valid():
            mob = form.save(commit=False)
            mob.projet = projet
            mob.save()
            messages.success(
                request,
                'Mobilisation matériel enregistrée avec succès.'
            )
            return redirect('projets:projet_detail', pk=projet.pk)
    else:
        form = forms.MobilisationMaterielForm()

    return render(request, 'projets/mobilisation_materiel_form.html', {
        'form': form,
        'projet': projet,
        'title': 'Nouvelle mobilisation matériel'
    })


@login_required
def mobilisation_materiel_list(request, projet_id):
    """قائمة mobilisations matériel لمشروع معين"""
    projet = get_object_or_404(models.Projet, pk=projet_id)
    mobilisations = projet.mobilisations_materiel.select_related(
        'engin', 'equipement', 'tache'
    ).order_by('-date_debut')

    # إحصائيات التكلفة
    stats = {
        'total_cout': mobilisations.aggregate(
            total=Sum('cout')
        )['cout'] or 0,
        'propres': mobilisations.filter(type_mobilisation='PROPRE').count(),
        'location': mobilisations.filter(type_mobilisation='LOCATION').count(),
    }

    context = {
        'projet': projet,
        'mobilisations': mobilisations,
        'stats': stats,
    }
    return render(request, 'projets/mobilisation_materiel_list.html', context)


# ============================================================
# SECTION 15: APIs (JSON)
# ============================================================

@login_required
def projet_gantt_data(request, pk):
    """
    API pour données Gantt
    يُستخدم لعرض مخطط Gantt في الواجهة الأمامية
    """
    projet = get_object_or_404(models.Projet, pk=pk)

    taches = models.TacheProjet.objects.filter(
        ouvrage__lot__projet=projet
    ).select_related('ouvrage', 'responsable').values(
        'id', 'code', 'designation',
        'date_debut_prevue', 'date_fin_prevue',
        'date_debut_reelle', 'date_fin_reelle',
        'pourcentage_avancement', 'statut',
        'ouvrage__code', 'ouvrage__designation'
    )

    data = []
    for t in taches:
        start = t['date_debut_reelle'] or t['date_debut_prevue']
        end = t['date_fin_reelle'] or t['date_fin_prevue']

        # تخطي المهام بدون تواريخ
        if not start or not end:
            continue

        data.append({
            'id': t['id'],
            'name': f"{t['code']} - {t['designation']}",
            'ouvrage': f"{t['ouvrage__code']} - {t['ouvrage__designation']}",
            'start': start.isoformat(),
            'end': end.isoformat(),
            'progress': float(t['pourcentage_avancement']),
            'status': t['statut'],
            'dependencies': [],  # يمكن إضافة التبعيات لاحقاً
        })

    return JsonResponse({
        'success': True,
        'data': data,
        'projet': {
            'reference': projet.reference,
            'nom': projet.nom,
            'date_debut': projet.date_debut_prevue.isoformat() if projet.date_debut_prevue else None,
            'date_fin': projet.date_fin_prevue.isoformat() if projet.date_fin_prevue else None,
        }
    })


@login_required
def projet_stats_api(request, pk):
    """
    API pour statistiques projet
    يُستخدم لعرض الإحصائيات في Dashboard
    """
    projet = get_object_or_404(models.Projet, pk=pk)

    # إحصائيات هيكلية
    lots_count = projet.lots.count()
    ouvrages_count = models.Ouvrage.objects.filter(lot__projet=projet).count()
    taches_qs = models.TacheProjet.objects.filter(ouvrage__lot__projet=projet)
    taches_count = taches_qs.count()
    taches_terminees = taches_qs.filter(statut='TERMINEE').count()

    # إحصائيات مالية
    decomptes_stats = projet.decomptes.aggregate(
        total_brut=Sum('montant_brut'),
        total_net=Sum('montant_net'),
        total_retenue=Sum('retenue_garantie'),
        total_tva=Sum('tva_montant'),
    )

    # إحصائيات RH
    affectations_count = projet.affectations_rh.count()
    personnel_uniques = projet.affectations_rh.values(
        'personnel'
    ).distinct().count()

    # إحصائيات Matériel
    mobilisations_count = projet.mobilisations_materiel.count()
    cout_materiel = projet.mobilisations_materiel.aggregate(
        total=Sum('cout')
    )['cout'] or 0

    stats = {
        'structure': {
            'lots': lots_count,
            'ouvrages': ouvrages_count,
            'taches': {
                'total': taches_count,
                'terminees': taches_terminees,
                'en_cours': taches_qs.filter(statut='EN_COURS').count(),
                'a_faire': taches_qs.filter(statut='A_FAIRE').count(),
                'bloquees': taches_qs.filter(statut='BLOQUEE').count(),
            },
        },
        'finances': {
            'montant_initial': float(projet.montant_initial),
            'montant_avenants': float(projet.montant_avenants),
            'montant_final': float(projet.montant_final),
            'decomptes': {
                'count': projet.decomptes.count(),
                'total_brut': float(decomptes_stats['total_brut'] or 0),
                'total_net': float(decomptes_stats['total_net'] or 0),
                'total_retenue': float(decomptes_stats['total_retenue'] or 0),
                'total_tva': float(decomptes_stats['total_tva'] or 0),
            },
            'garanties_count': projet.garanties.count(),
            'factures_extra_count': projet.factures_extra.count(),
        },
        'ressources': {
            'affectations': affectations_count,
            'personnel_uniques': personnel_uniques,
            'mobilisations': mobilisations_count,
            'cout_materiel': float(cout_materiel),
        },
        'administratif': {
            'reunions': projet.reunions.count(),
            'correspondances': projet.correspondances.count(),
            'comptes_rendus': projet.comptes_rendus.count(),
            'livrables': projet.livrables.count(),
            'documents_ged': projet.ged_documents.count(),
        },
        'avancement': {
            'global': float(projet.pourcentage_avancement),
            'priorite': projet.priorite,
            'statut': projet.statut,
        },
    }

    return JsonResponse({
        'success': True,
        'projet': {
            'id': projet.id,
            'reference': projet.reference,
            'nom': projet.nom,
        },
        'stats': stats,
    })


@login_required
def projet_kanban_data(request, pk):
    """
    API pour données Kanban Board
    يُستخدم لعرض المهام في شكل Kanban
    """
    projet = get_object_or_404(models.Projet, pk=pk)

    taches = models.TacheProjet.objects.filter(
        ouvrage__lot__projet=projet
    ).select_related(
        'ouvrage', 'responsable', 'personnel_responsable'
    ).values(
        'id', 'code', 'designation', 'statut', 'priorite',
        'pourcentage_avancement', 'date_fin_prevue',
        'responsable__username',
        'personnel_responsable__nom',
        'personnel_responsable__prenom',
        'ouvrage__code',
    )

    # تنظيم حسب الحالة
    kanban = {
        'A_FAIRE': [],
        'EN_COURS': [],
        'EN_REVIEW': [],
        'BLOQUEE': [],
        'TERMINEE': [],
    }

    for t in taches:
        responsable = (
            t['responsable__username'] or
            f"{t['personnel_responsable__nom']} {t['personnel_responsable__prenom']}"
            if t['personnel_responsable__nom'] else '-'
        )

        kanban[t['statut']].append({
            'id': t['id'],
            'code': t['code'],
            'designation': t['designation'],
            'priorite': t['priorite'],
            'progress': float(t['pourcentage_avancement']),
            'deadline': t['date_fin_prevue'].isoformat() if t['date_fin_prevue'] else None,
            'responsable': responsable,
            'ouvrage': t['ouvrage__code'],
        })

    return JsonResponse({
        'success': True,
        'kanban': kanban,
    })


@login_required
def recherche_globale(request):
    """
    بحث شامل في جميع الكيانات
    يُستخدم في شريط البحث العلوي
    """
    query = request.GET.get('q', '').strip()

    if not query or len(query) < 2:
        return JsonResponse({
            'success': True,
            'results': [],
            'message': 'Veuillez saisir au moins 2 caractères.'
        })

    results = []

    # البحث في Projets
    projets = models.Projet.objects.filter(
        Q(reference__icontains=query) |
        Q(nom__icontains=query) |
        Q(description__icontains=query),
        actif=True
    )[:5]

    for p in projets:
        results.append({
            'type': 'projet',
            'icon': 'bi-folder2-open',
            'title': p.reference,
            'subtitle': p.nom,
            'url': p.get_absolute_url(),
        })

    # البحث في Lots
    lots = models.Lot.objects.filter(
        Q(designation__icontains=query) |
        Q(projet__reference__icontains=query)
    ).select_related('projet')[:5]

    for l in lots:
        results.append({
            'type': 'lot',
            'icon': 'bi-box-seam',
            'title': f"Lot {l.numero}",
            'subtitle': f"{l.designation} ({l.projet.reference})",
            'url': l.get_absolute_url(),
        })

    # البحث في Tâches
    taches = models.TacheProjet.objects.filter(
        Q(code__icontains=query) |
        Q(designation__icontains=query)
    ).select_related('ouvrage__lot__projet')[:5]

    for t in taches:
        results.append({
            'type': 'tache',
            'icon': 'bi-check2-square',
            'title': t.code,
            'subtitle': f"{t.designation} ({t.ouvrage.lot.projet.reference})",
            'url': t.get_absolute_url(),
        })

    # البحث في Documents GED
    documents = models.GedDocument.objects.filter(
        Q(titre__icontains=query) |
        Q(reference__icontains=query)
    ).select_related('projet')[:5]

    for d in documents:
        results.append({
            'type': 'document',
            'icon': 'bi-file-earmark',
            'title': d.titre,
            'subtitle': f"{d.get_categorie_display()} ({d.projet.reference})",
            'url': f"/projets/projet/{d.projet.pk}/ged/",
        })

    return JsonResponse({
        'success': True,
        'results': results,
        'total': len(results),
    })    
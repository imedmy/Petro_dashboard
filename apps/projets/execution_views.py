# =============================================================================
# ✅ Views لتتبع التنفيذ الفعلي (Réalisations)
# =============================================================================
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from core.models import Engin
from .models import (
    Projet, Lot, Ouvrage, TacheProjet,
    ReferenceProcedure, Realisation, DetailsRealisation,
    EvenementLogistique, LienAchat, Consommation, Resultat,
)


# =============================================================================
# 🎯 RÉALISATIONS
# =============================================================================

@login_required
def realisation_list(request, projet_id):
    """قائمة التنفيذات في مشروع"""
    projet = get_object_or_404(Projet, pk=projet_id)
    statut = request.GET.get('statut', '')
    lot_id = request.GET.get('lot', '')

    qs = Realisation.objects.filter(projet=projet).select_related(
        'lot', 'ouvrage', 'tache', 'responsable'
    ).annotate(
        nb_details=Count('details'),
        nb_evenements=Count('evenements_logistiques'),
        total_cout=Sum('details__cout_total'),
    )

    if statut:
        qs = qs.filter(statut=statut)
    if lot_id:
        qs = qs.filter(lot_id=lot_id)

    lots = projet.lots.all()

    stats = {
        'total': qs.count(),
        'en_cours': qs.filter(statut='EN_COURS').count(),
        'termine': qs.filter(statut='TERMINE').count(),
        'suspendu': qs.filter(statut='SUSPENDU').count(),
        'cout_total': qs.aggregate(total=Sum('details__cout_total'))['total'] or 0,
    }

    return render(request, 'projets/execution/realisation_list.html', {
        'projet': projet,
        'realisations': qs,
        'lots': lots,
        'stats': stats,
        'statut': statut,
        'lot_id': lot_id,
    })


@login_required
def realisation_create(request, projet_id):
    """إنشاء تنفيذ جديد"""
    projet = get_object_or_404(Projet, pk=projet_id)

    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        description = request.POST.get('description', '').strip()
        lot_id = request.POST.get('lot') or None
        ouvrage_id = request.POST.get('ouvrage') or None
        tache_id = request.POST.get('tache') or None
        date_debut = request.POST.get('date_debut_reelle') or None
        date_fin = request.POST.get('date_fin_reelle') or None
        statut = request.POST.get('statut', 'PLANIFIE')
        responsable_id = request.POST.get('responsable') or None

        if not nom:
            messages.error(request, 'Le nom est obligatoire.')
            return redirect('projets:realisation_create', projet_id=projet.pk)

        realisation = Realisation.objects.create(
            projet=projet,
            lot_id=lot_id,
            ouvrage_id=ouvrage_id,
            tache_id=tache_id,
            nom=nom,
            description=description,
            date_debut_reelle=date_debut,
            date_fin_reelle=date_fin,
            statut=statut,
            responsable_id=responsable_id,
        )
        messages.success(request, f'Réalisation "{nom}" créée.')
        return redirect('projets:realisation_detail', pk=realisation.pk)

    lots = projet.lots.all()
    ouvrages = Ouvrage.objects.filter(lot__projet=projet)
    taches = TacheProjet.objects.filter(ouvrage__lot__projet=projet)

    return render(request, 'projets/execution/realisation_form.html', {
        'projet': projet,
        'lots': lots,
        'ouvrages': ouvrages,
        'taches': taches,
        'title': 'Nouvelle Réalisation',
    })


@login_required
def realisation_detail(request, pk):
    """تفاصيل تنفيذ مع جميع التفاصيل المرتبطة"""
    realisation = get_object_or_404(
        Realisation.objects.select_related('projet', 'lot', 'ouvrage', 'tache'),
        pk=pk
    )

    details = realisation.details.select_related('reference_procedure').all()
    evenements = realisation.evenements_logistiques.select_related('engin').order_by('-date_evenement')[:20]
    liens_achat = realisation.liens_achat.all()
    consommations = realisation.consommations.all()
    resultats = realisation.resultats.all()

    stats = {
        'cout_total': details.aggregate(total=Sum('cout_total'))['total'] or 0,
        'nb_details': details.count(),
        'nb_evenements': evenements.count(),
        'impact_delai_total': evenements.aggregate(total=Sum('impact_delai_jours'))['total'] or 0,
        'consommation_total': consommations.aggregate(total=Sum('cout_total'))['total'] or 0,
        'nb_resultats': resultats.count(),
        'nb_non_conformes': resultats.filter(conforme=False).count(),
    }

    return render(request, 'projets/execution/realisation_detail.html', {
        'realisation': realisation,
        'details': details,
        'evenements': evenements,
        'liens_achat': liens_achat,
        'consommations': consommations,
        'resultats': resultats,
        'stats': stats,
    })


# =============================================================================
# 📝 DETAILS RÉALISATION
# =============================================================================

@login_required
def detail_realisation_create(request, realisation_id):
    """إضافة تفصيل تنفيذ"""
    realisation = get_object_or_404(Realisation, pk=realisation_id)

    if request.method == 'POST':
        type_detail = request.POST.get('type_detail', 'TRAVAUX')
        description = request.POST.get('description', '').strip()
        reference_id = request.POST.get('reference_procedure') or None
        quantite = request.POST.get('quantite', 0)
        unite = request.POST.get('unite', '').strip()
        prix_unitaire = request.POST.get('prix_unitaire', 0)
        fournisseur = request.POST.get('fournisseur', '').strip()
        observation = request.POST.get('observation', '').strip()

        if not description:
            messages.error(request, 'La description est obligatoire.')
            return redirect('projets:detail_realisation_create', realisation_id=realisation.pk)

        try:
            quantite = float(quantite)
            prix_unitaire = float(prix_unitaire)
        except (ValueError, TypeError):
            quantite = 0
            prix_unitaire = 0

        DetailsRealisation.objects.create(
            realisation=realisation,
            reference_procedure_id=reference_id,
            type_detail=type_detail,
            description=description,
            quantite=quantite,
            unite=unite,
            prix_unitaire=prix_unitaire,
            cout_total=quantite * prix_unitaire,
            fournisseur=fournisseur,
            observation=observation,
        )
        messages.success(request, 'Détail ajouté avec succès.')
        return redirect('projets:realisation_detail', pk=realisation.pk)

    references = ReferenceProcedure.objects.filter(actif=True)
    return render(request, 'projets/execution/detail_realisation_form.html', {
        'realisation': realisation,
        'references': references,
        'title': 'Ajouter un Détail',
    })


# =============================================================================
# 🚚 ÉVÉNEMENTS LOGISTIQUES
# =============================================================================

@login_required
def evenement_logistique_create(request, realisation_id):
    """تسجيل حدث لوجستي"""
    realisation = get_object_or_404(Realisation, pk=realisation_id)

    if request.method == 'POST':
        type_evenement = request.POST.get('type_evenement', 'AUTRE')
        description = request.POST.get('description', '').strip()
        impact = request.POST.get('impact_delai_jours', 0)
        engin_id = request.POST.get('engin') or None
        document = request.FILES.get('document_joint')

        if not description:
            messages.error(request, 'La description est obligatoire.')
            return redirect('projets:evenement_create', realisation_id=realisation.pk)

        try:
            impact = float(impact)
        except (ValueError, TypeError):
            impact = 0.0

        EvenementLogistique.objects.create(
            realisation=realisation,
            projet=realisation.projet,
            type_evenement=type_evenement,
            description=description,
            impact_delai_jours=impact,
            engin_id=engin_id,
            document_joint=document,
            declare_par=request.user,
        )
        messages.success(request, 'Événement logistique enregistré.')
        return redirect('projets:realisation_detail', pk=realisation.pk)

    engins = Engin.objects.filter(actif=True)
    return render(request, 'projets/execution/evenement_form.html', {
        'realisation': realisation,
        'engins': engins,
        'title': 'Nouvel Événement Logistique',
    })


# =============================================================================
# ⛽ CONSOMMATIONS
# =============================================================================

@login_required
def consommation_create(request, realisation_id):
    """تسجيل استهلاك"""
    realisation = get_object_or_404(Realisation, pk=realisation_id)

    if request.method == 'POST':
        type_conso = request.POST.get('type_consommation', 'MATERIAU')
        designation = request.POST.get('designation', '').strip()
        quantite = request.POST.get('quantite', 0)
        unite = request.POST.get('unite', '').strip()
        cout_unitaire = request.POST.get('cout_unitaire', 0)
        cod_art = request.POST.get('cod_art', '').strip()
        observation = request.POST.get('observation', '').strip()

        if not designation:
            messages.error(request, 'La désignation est obligatoire.')
            return redirect('projets:consommation_create', realisation_id=realisation.pk)

        try:
            quantite = float(quantite)
            cout_unitaire = float(cout_unitaire)
        except (ValueError, TypeError):
            quantite = 0
            cout_unitaire = 0

        Consommation.objects.create(
            realisation=realisation,
            type_consommation=type_conso,
            designation=designation,
            quantite=quantite,
            unite=unite,
            cout_unitaire=cout_unitaire,
            cout_total=quantite * cout_unitaire,
            cod_art=cod_art,
            observation=observation,
        )
        messages.success(request, 'Consommation enregistrée.')
        return redirect('projets:realisation_detail', pk=realisation.pk)

    return render(request, 'projets/execution/consommation_form.html', {
        'realisation': realisation,
        'title': 'Nouvelle Consommation',
    })


# =============================================================================
# 📊 RÉSULTATS
# =============================================================================

@login_required
def resultat_create(request, realisation_id):
    """تسجيل نتيجة / تحكم"""
    realisation = get_object_or_404(Realisation, pk=realisation_id)

    if request.method == 'POST':
        type_resultat = request.POST.get('type_resultat', 'CONTROLE_QUALITE')
        titre = request.POST.get('titre', '').strip()
        description = request.POST.get('description', '').strip()
        conforme = request.POST.get('conforme') == 'on'
        ecart = request.POST.get('ecart_constate', '').strip()
        laboratoire = request.POST.get('laboratoire', '').strip()
        valeurs_mesurees = request.POST.get('valeurs_mesurees', '{}').strip()
        valeurs_reference = request.POST.get('valeurs_reference', '{}').strip()
        document = request.FILES.get('document_joint')

        if not titre:
            messages.error(request, 'Le titre est obligatoire.')
            return redirect('projets:resultat_create', realisation_id=realisation.pk)

        try:
            vm = json.loads(valeurs_mesurees) if valeurs_mesurees else {}
        except json.JSONDecodeError:
            vm = {}

        try:
            vr = json.loads(valeurs_reference) if valeurs_reference else {}
        except json.JSONDecodeError:
            vr = {}

        Resultat.objects.create(
            realisation=realisation,
            type_resultat=type_resultat,
            titre=titre,
            description=description,
            valeurs_mesurees=vm,
            valeurs_reference=vr,
            conforme=conforme,
            ecart_constate=ecart,
            laboratoire=laboratoire,
            document_joint=document,
            realise_par=request.user,
        )
        messages.success(request, 'Résultat enregistré.')
        return redirect('projets:realisation_detail', pk=realisation.pk)

    return render(request, 'projets/execution/resultat_form.html', {
        'realisation': realisation,
        'title': 'Nouveau Résultat',
    })


# =============================================================================
# 🛒 LIENS ACHAT
# =============================================================================

@login_required
def lien_achat_create(request, realisation_id):
    """ربط بطلب شراء"""
    realisation = get_object_or_404(Realisation, pk=realisation_id)

    if request.method == 'POST':
        numero_bc = request.POST.get('numero_bc', '').strip()
        fournisseur = request.POST.get('fournisseur', '').strip()
        date_bc = request.POST.get('date_bc') or None
        montant_prevu = request.POST.get('montant_prevu', 0)
        statut = request.POST.get('statut_livraison', 'COMMANDE')
        date_prevue = request.POST.get('date_livraison_prevue') or None
        observation = request.POST.get('observation', '').strip()

        if not numero_bc:
            messages.error(request, 'Le numéro BC est obligatoire.')
            return redirect('projets:lien_achat_create', realisation_id=realisation.pk)

        try:
            montant_prevu = float(montant_prevu)
        except (ValueError, TypeError):
            montant_prevu = 0

        LienAchat.objects.create(
            realisation=realisation,
            numero_bc=numero_bc,
            fournisseur=fournisseur,
            date_bc=date_bc,
            montant_prevu=montant_prevu,
            statut_livraison=statut,
            date_livraison_prevue=date_prevue,
            observation=observation,
        )
        messages.success(request, 'Lien achat créé.')
        return redirect('projets:realisation_detail', pk=realisation.pk)

    return render(request, 'projets/execution/lien_achat_form.html', {
        'realisation': realisation,
        'title': 'Nouveau Lien Achat',
    })
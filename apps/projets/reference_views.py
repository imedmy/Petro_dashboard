# =============================================================================
# ✅ Views لإدارة المراجع القياسية (ReferenceProcedure)
# =============================================================================
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import ReferenceProcedure, DomaineCompetence


@login_required
def reference_list(request):
    """قائمة الإجراءات المرجعية مع الفلترة والبحث"""
    domaine_id = request.GET.get('domaine')
    search = request.GET.get('q', '').strip()
    actif = request.GET.get('actif', '1')

    qs = ReferenceProcedure.objects.select_related('domaine').all()

    if domaine_id:
        qs = qs.filter(domaine_id=domaine_id)
    if search:
        qs = qs.filter(Q(code__icontains=search) | Q(nom__icontains=search))
    if actif == '1':
        qs = qs.filter(actif=True)

    domaines = DomaineCompetence.objects.filter(actif=True)

    context = {
        'references': qs,
        'domaines': domaines,
        'domaine_id': domaine_id,
        'search': search,
        'actif': actif,
        'total': qs.count(),
    }
    return render(request, 'projets/reference/reference_list.html', context)


@login_required
def reference_create(request):
    """إنشاء إجراء مرجعي جديد"""
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        nom = request.POST.get('nom', '').strip()
        domaine_id = request.POST.get('domaine') or None
        description = request.POST.get('description', '').strip()

        criteres = request.POST.get('criteres_qualite', '').strip()
        ressources = request.POST.get('ressources_typiques', '').strip()
        documents = request.POST.get('documents_reference', '').strip()
        details = request.POST.get('details_attendus', '').strip()

        if not code or not nom:
            messages.error(request, 'Code et nom sont obligatoires.')
            return redirect('projets:reference_create')

        if ReferenceProcedure.objects.filter(code=code).exists():
            messages.error(request, f'Le code "{code}" existe déjà.')
            return redirect('projets:reference_create')

        def parse_json_list(text):
            """تحويل النص إلى قائمة JSON"""
            if not text:
                return []
            try:
                result = json.loads(text)
                return result if isinstance(result, list) else [text]
            except json.JSONDecodeError:
                return [line.strip() for line in text.split('\n') if line.strip()]

        ref = ReferenceProcedure.objects.create(
            code=code,
            nom=nom,
            domaine_id=domaine_id,
            description_standard=description,
            criteres_qualite=parse_json_list(criteres),
            ressources_typiques=parse_json_list(ressources),
            documents_reference=parse_json_list(documents),
            details_attendus=parse_json_list(details),
        )
        messages.success(request, f'Procédure "{ref.nom}" créée avec succès.')
        return redirect('projets:reference_list')

    domaines = DomaineCompetence.objects.filter(actif=True)
    return render(request, 'projets/reference/reference_form.html', {
        'domaines': domaines,
        'title': 'Nouvelle Procédure de Référence',
    })


@login_required
def reference_detail(request, pk):
    """تفاصيل إجراء مرجعي"""
    ref = get_object_or_404(ReferenceProcedure, pk=pk)
    instances_count = ref.details_realisation.count()
    return render(request, 'projets/reference/reference_detail.html', {
        'ref': ref,
        'instances_count': instances_count,
    })
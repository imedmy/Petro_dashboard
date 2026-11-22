# apps/projets/services.py
"""
Services d'intégration avec les autres modules du Petro Dashboard
خدمات التكامل مع بقية Modules في المشروع
"""
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from core import models as core_models
from . import models as projets_models


# ============================================================
# SECTION 1: STOCK INTEGRATION SERVICE
# ============================================================

class StockIntegrationService:
    """
    التكامل مع Module Stock
    يسمح بالربط مع المخزون المحلي (MySQL) والمخزون المركزي (SQL Server)
    """

    @staticmethod
    def get_article_info(cod_art):
        """
        استرجاع معلومات مادة من المخزون
        """
        try:
            # البحث في ArticleFamily
            family = core_models.ArticleFamily.objects.filter(
                full_code=cod_art[:9]
            ).first()

            # البحث في SerialUnit
            serial_units = core_models.SerialUnit.objects.filter(
                cod_art=cod_art
            )

            return {
                'cod_art': cod_art,
                'family': family.name if family else None,
                'family_code': family.full_code if family else None,
                'serial_units_count': serial_units.count(),
                'serial_units': list(
                    serial_units.values(
                        'numero_serie', 'statut', 'emplacement'
                    )[:10]
                ),
            }
        except Exception as e:
            print(f"❌ Erreur Stock Integration: {e}")
            return None

    @staticmethod
    def get_articles_by_family(family_code):
        """
        استرجاع جميع المواد التابعة لعائلة معينة
        """
        try:
            family = core_models.ArticleFamily.objects.filter(
                full_code=family_code
            ).first()

            if not family:
                return []

            # البحث عن المواد التي تبدأ بهذا الكود
            articles = core_models.SerialUnit.objects.filter(
                cod_art__startswith=family_code
            ).values(
                'cod_art', 'val_art', 'numero_serie', 'statut'
            )

            return list(articles)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return []

    @staticmethod
    def enregistrer_sortie_stock(cod_art, val_art, numero_serie,
                                  quantite, projet_id, motif):
        """
        تسجيل سحب من المخزون
        TODO: Implémenter selon votre logique de mouvement de stock
        """
        try:
            # التحقق من وجود الوحدة
            serial_unit = core_models.SerialUnit.objects.filter(
                cod_art=cod_art,
                val_art=val_art,
                numero_serie=numero_serie
            ).first()

            if not serial_unit:
                return {
                    'success': False,
                    'message': f'Unité {numero_serie} non trouvée'
                }

            # TODO: إنشاء حركة خروج في المخزون
            # حسب منطق المخزون الموجود لديكم

            return {
                'success': True,
                'message': 'Sortie enregistrée avec succès'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erreur: {str(e)}'
            }


# ============================================================
# SECTION 2: TIERS INTEGRATION SERVICE
# ============================================================

class TiersIntegrationService:
    """
    التكامل مع core.Tiers
    يوفر خدمات للتعامل مع الأطراف (Fournisseurs, Prestataires, etc.)
    """

    @staticmethod
    def get_all_tiers():
        """الحصول على جميع الأطراف النشطة"""
        return core_models.Tiers.objects.filter(actif=True)

    @staticmethod
    def get_fournisseurs():
        """الحصول على الموردين"""
        return core_models.Tiers.objects.filter(
            type_tiers='fournisseur',
            actif=True
        )

    @staticmethod
    def get_prestataires():
        """الحصول على المقاولين"""
        return core_models.Tiers.objects.filter(
            type_tiers='prestataire',
            actif=True
        )

    @staticmethod
    def get_autres():
        """الحصول على الأطراف الأخرى"""
        return core_models.Tiers.objects.filter(
            type_tiers='autre',
            actif=True
        )

    @staticmethod
    def get_tiers_choices():
        """
        الحصول على قائمة الأطراف كـ choices للنماذج
        يُستخدم في Forms
        """
        tiers = core_models.Tiers.objects.filter(actif=True).order_by('raison_sociale')
        return [(t.id, f"{t.raison_sociale} ({t.code_tiers})") for t in tiers]

    @staticmethod
    def get_tiers_by_type(type_tiers):
        """الحصول على الأطراف حسب النوع"""
        return core_models.Tiers.objects.filter(
            type_tiers=type_tiers,
            actif=True
        ).order_by('raison_sociale')

    @staticmethod
    def search_tiers(query):
        """البحث في الأطراف"""
        return core_models.Tiers.objects.filter(
            Q(raison_sociale__icontains=query) |
            Q(code_tiers__icontains=query) |
            Q(contact__icontains=query),
            actif=True
        )


# ============================================================
# SECTION 3: PERSONNEL INTEGRATION SERVICE
# ============================================================

class PersonnelIntegrationService:
    """
    التكامل مع core.Personnel
    يوفر خدمات للتعامل مع الأفراد
    """

    @staticmethod
    def get_all_personnel():
        """الحصول على جميع الأفراد النشطين"""
        return core_models.Personnel.objects.filter(actif=True)

    @staticmethod
    def get_personnel_by_matricule(matricule):
        """الحصول على فرد بالرقم الوظيفي"""
        return core_models.Personnel.objects.filter(
            matricule=matricule,
            actif=True
        ).first()

    @staticmethod
    def get_personnel_choices():
        """
        الحصول على قائمة الأفراد كـ choices للنماذج
        """
        personnel = core_models.Personnel.objects.filter(
            actif=True
        ).order_by('nom', 'prenom')

        return [
            (p.id, f"{p.nom} {p.prenom} ({p.matricule})")
            for p in personnel
        ]

    @staticmethod
    def get_personnel_by_service(service_id):
        """الحصول على الأفراد حسب القسم"""
        # TODO: إضافة service_id في core.Personnel إذا لزم الأمر
        return core_models.Personnel.objects.filter(actif=True)

    @staticmethod
    def search_personnel(query):
        """البحث في الأفراد"""
        return core_models.Personnel.objects.filter(
            Q(nom__icontains=query) |
            Q(prenom__icontains=query) |
            Q(matricule__icontains=query) |
            Q(poste__icontains=query),
            actif=True
        )


# ============================================================
# SECTION 4: MATERIEL INTEGRATION SERVICE
# ============================================================

class MaterielIntegrationService:
    """
    التكامل مع core.Engin et core.Equipement
    يوفر خدمات للتعامل مع الآليات والمعدات
    """

    @staticmethod
    def get_engins_actifs():
        """الحصول على الآليات النشطة"""
        return core_models.Engin.objects.filter(actif=True)

    @staticmethod
    def get_equipements_actifs():
        """الحصول على المعدات النشطة"""
        return core_models.Equipement.objects.filter(actif=True)

    @staticmethod
    def get_engins_choices():
        """
        الحصول على قائمة الآليات كـ choices
        """
        engins = core_models.Engin.objects.filter(
            actif=True
        ).order_by('libelle')

        return [
            (e.id, f"{e.get_type_engin_display()} - {e.libelle} ({e.immatriculation or e.numero_serie})")
            for e in engins
        ]

    @staticmethod
    def get_equipements_choices():
        """
        الحصول على قائمة المعدات كـ choices
        """
        equipements = core_models.Equipement.objects.filter(
            actif=True
        ).order_by('libelle')

        return [
            (e.id, f"{e.get_type_equipement_display()} - {e.libelle} ({e.numero_serie or '—'})")
            for e in equipements
        ]

    @staticmethod
    def get_engins_by_service(service_id):
        """الحصول على آليات قسم معين"""
        return core_models.Engin.objects.filter(
            service_id=service_id,
            actif=True
        )

    @staticmethod
    def get_engins_by_type(type_engin):
        """الحصول على آليات حسب النوع"""
        return core_models.Engin.objects.filter(
            type_engin=type_engin,
            actif=True
        )

    @staticmethod
    def get_engin_stats(engin_id):
        """
        إحصائيات معدة معينة
        """
        try:
            engin = core_models.Engin.objects.get(id=engin_id)

            # عدد مرات الاستخدام في المشاريع
            mobilisations = projets_models.MobilisationMateriel.objects.filter(
                engin=engin
            )

            return {
                'engin': engin,
                'mobilisations_count': mobilisations.count(),
                'heures_totales': mobilisations.aggregate(
                    total=Sum('heures_utilisees')
                )['total'] or 0,
                'cout_total': mobilisations.aggregate(
                    total=Sum('cout')
                )['cout'] or 0,
            }
        except core_models.Engin.DoesNotExist:
            return None


# ============================================================
# SECTION 5: WORKFLOW ENGINE SERVICE
# ============================================================

class WorkflowService:
    """
    محرك Workflow Engine
    يوفر خدمات لإدارة مسارات العمل
    """

    @staticmethod
    def demarrer_workflow(workflow_code, projet, entity_type, entity_id):
        """
        بدء workflow جديد على كيان معين
        
        Args:
            workflow_code: كود مسار العمل (ex: 'APPRO_DECOMPTE')
            projet: مشروع مرتبط
            entity_type: نوع الكيان (ex: 'Decompte', 'Avenant')
            entity_id: معرف الكيان
            
        Returns:
            WorkflowInstance أو None
        """
        try:
            workflow = projets_models.Workflow.objects.get(
                code=workflow_code,
                actif=True
            )

            premiere_etape = workflow.etapes.order_by('ordre').first()

            if not premiere_etape:
                print(f"❌ Aucune étape définie pour le workflow {workflow_code}")
                return None

            instance = projets_models.WorkflowInstance.objects.create(
                workflow=workflow,
                projet=projet,
                entity_type=entity_type,
                entity_id=entity_id,
                etape_courante=premiere_etape,
                statut='EN_COURS'
            )

            return instance

        except projets_models.Workflow.DoesNotExist:
            print(f"❌ Workflow {workflow_code} non trouvé")
            return None
        except Exception as e:
            print(f"❌ Erreur démarrage workflow: {e}")
            return None

    @staticmethod
    def valider_etape(instance_id, utilisateur, action, commentaire=''):
        """
        التحقق من مرحلة والانتقال إلى المرحلة التالية
        
        Args:
            instance_id: معرف instance الـ workflow
            utilisateur: المستخدم الذي قام بالإجراء
            action: الإجراء (approuvé, rejeté, commenté)
            commentaire: تعليق اختياري
            
        Returns:
            WorkflowInstance محدّث أو None
        """
        try:
            instance = projets_models.WorkflowInstance.objects.get(id=instance_id)
            etape_courante = instance.etape_courante

            if not etape_courante:
                print("❌ Aucune étape courante")
                return None

            # تسجيل الإجراء
            projets_models.WorkflowAction.objects.create(
                instance=instance,
                etape=etape_courante,
                utilisateur=utilisateur,
                action_effectuee=action,
                commentaire=commentaire
            )

            # الانتقال إلى المرحلة التالية
            etape_suivante = instance.workflow.etapes.filter(
                ordre__gt=etape_courante.ordre
            ).order_by('ordre').first()

            if etape_suivante:
                instance.etape_courante = etape_suivante
                instance.save()
            else:
                # Workflow terminé
                instance.etape_courante = None
                instance.statut = 'TERMINE'
                instance.date_fin = timezone.now()
                instance.save()

            return instance

        except projets_models.WorkflowInstance.DoesNotExist:
            print(f"❌ Instance {instance_id} non trouvée")
            return None
        except Exception as e:
            print(f"❌ Erreur validation étape: {e}")
            return None

    @staticmethod
    def rejeter_workflow(instance_id, utilisateur, motif=''):
        """
        رفض workflow
        
        Args:
            instance_id: معرف instance
            utilisateur: المستخدم الرافض
            motif: سبب الرفض
        """
        try:
            instance = projets_models.WorkflowInstance.objects.get(id=instance_id)

            # تسجيل الإجراء
            projets_models.WorkflowAction.objects.create(
                instance=instance,
                etape=instance.etape_courante,
                utilisateur=utilisateur,
                action_effectuee='rejeté',
                commentaire=motif
            )

            # تحديث الحالة
            instance.statut = 'REJETE'
            instance.date_fin = timezone.now()
            instance.save()

            return instance

        except Exception as e:
            print(f"❌ Erreur rejet workflow: {e}")
            return None

    @staticmethod
    def annuler_workflow(instance_id, utilisateur, motif=''):
        """
        إلغاء workflow
        """
        try:
            instance = projets_models.WorkflowInstance.objects.get(id=instance_id)

            # تسجيل الإجراء
            projets_models.WorkflowAction.objects.create(
                instance=instance,
                etape=instance.etape_courante,
                utilisateur=utilisateur,
                action_effectuee='annulé',
                commentaire=motif
            )

            # تحديث الحالة
            instance.statut = 'ANNULE'
            instance.date_fin = timezone.now()
            instance.save()

            return instance

        except Exception as e:
            print(f"❌ Erreur annulation workflow: {e}")
            return None

    @staticmethod
    def get_historique_instance(instance_id):
        """
        استرجاع تاريخ الإجراءات لـ instance معين
        """
        try:
            instance = projets_models.WorkflowInstance.objects.get(id=instance_id)
            actions = instance.actions.select_related(
                'etape', 'utilisateur'
            ).order_by('date_action')

            return list(actions.values(
                'etape__nom',
                'etape__ordre',
                'utilisateur__username',
                'action_effectuee',
                'commentaire',
                'date_action'
            ))
        except Exception as e:
            print(f"❌ Erreur historique: {e}")
            return []

    @staticmethod
    def get_instances_en_retard():
        """
        الحصول على instances المتأخرة (تجاوزت delai_max_jours)
        """
        instances = projets_models.WorkflowInstance.objects.filter(
            statut='EN_COURS',
            etape_courante__delai_max_jours__gt=0
        ).select_related('etape_courante', 'projet')

        instances_retard = []
        now = timezone.now()

        for instance in instances:
            # حساب تاريخ البداية من آخر action
            dernier_action = instance.actions.order_by('-date_action').first()
            if not dernier_action:
                date_debut_etape = instance.date_debut
            else:
                date_debut_etape = dernier_action.date_action

            # حساب التأخير
            delai_ecoule = (now - date_debut_etape).days
            delai_max = instance.etape_courante.delai_max_jours

            if delai_ecoule > delai_max:
                instances_retard.append({
                    'instance': instance,
                    'delai_ecoule': delai_ecoule,
                    'delai_max': delai_max,
                    'retard_jours': delai_ecoule - delai_max,
                })

        return instances_retard


# ============================================================
# SECTION 6: PROJET STATISTICS SERVICE
# ============================================================

class ProjetStatisticsService:
    """
    خدمات الإحصائيات للمشاريع
    """

    @staticmethod
    def get_projet_stats(projet_id):
        """
        إحصائيات شاملة لمشروع معين
        """
        try:
            projet = projets_models.Projet.objects.get(id=projet_id)

            # إحصائيات هيكلية
            lots_count = projet.lots.count()
            ouvrages_count = projets_models.Ouvrage.objects.filter(
                lot__projet=projet
            ).count()
            taches_qs = projets_models.TacheProjet.objects.filter(
                ouvrage__lot__projet=projet
            )

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

            return {
                'projet': projet,
                'structure': {
                    'lots': lots_count,
                    'ouvrages': ouvrages_count,
                    'taches': {
                        'total': taches_qs.count(),
                        'terminees': taches_qs.filter(statut='TERMINEE').count(),
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
                    },
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
            }
        except Exception as e:
            print(f"❌ Erreur stats: {e}")
            return None

    @staticmethod
    def get_dashboard_stats():
        """
        إحصائيات عامة للوحة التحكم
        """
        projets = projets_models.Projet.objects.filter(actif=True)

        return {
            'total': projets.count(),
            'en_cours': projets.filter(statut='EN_COURS').count(),
            'planifie': projets.filter(statut='PLANIFIE').count(),
            'suspendu': projets.filter(statut='SUSPENDU').count(),
            'acheve': projets.filter(statut='ACHEVE').count(),
            'resilie': projets.filter(statut='RESILIE').count(),
            'montant_total': float(
                projets.aggregate(total=Sum('montant_final'))['total'] or 0
            ),
        }


# ============================================================
# SECTION 7: NOTIFICATION SERVICE
# ============================================================

class NotificationService:
    """
    خدمة الإشعارات
    """

    @staticmethod
    def notifier_echeance_livrable(livrable_id):
        """
        إشعار بقرب موعد تسليم livrable
        """
        try:
            livrable = projets_models.Livrable.objects.get(id=livrable_id)

            # التحقق من أن الموعد قريب (7 أيام)
            jours_restants = (livrable.date_echeance - timezone.now().date()).days

            if jours_restants <= 7 and jours_restants >= 0:
                # إنشاء إشعار
                core_models.Notification.objects.create(
                    user=livrable.projet.chef_projet,
                    type='autre',
                    message=f"Livrable '{livrable.designation}' à échéance dans {jours_restants} jours",
                )
                return True

            return False
        except Exception as e:
            print(f"❌ Erreur notification: {e}")
            return False

    @staticmethod
    def notifier_retard_tache(tache_id):
        """
        إشعار بتأخر tâche
        """
        try:
            tache = projets_models.TacheProjet.objects.get(id=tache_id)

            # التحقق من أن المهمة متأخرة
            if tache.date_fin_prevue and tache.date_fin_prevue < timezone.now().date():
                if tache.statut not in ['TERMINEE', 'ANNULEE']:
                    # إنشاء إشعار
                    if tache.responsable:
                        core_models.Notification.objects.create(
                            user=tache.responsable,
                            type='tache_retardee',
                            message=f"Tâche '{tache.designation}' en retard",
                        )
                    return True

            return False
        except Exception as e:
            print(f"❌ Erreur notification: {e}")
            return False

    @staticmethod
    def notifier_expiration_garantie(garantie_id):
        """
        إشعار بقرب انتهاء ضمان
        """
        try:
            garantie = projets_models.Garantie.objects.get(id=garantie_id)

            # التحقق من أن الضمان ينتهي قريباً (30 يوم)
            jours_restants = (garantie.date_expiration - timezone.now().date()).days

            if jours_restants <= 30 and jours_restants >= 0:
                # إنشاء إشعار لمدير المشروع
                if garantie.projet.chef_projet:
                    core_models.Notification.objects.create(
                        user=garantie.projet.chef_projet,
                        type='autre',
                        message=f"Garantie '{garantie.reference}' expire dans {jours_restants} jours",
                    )
                return True

            return False
        except Exception as e:
            print(f"❌ Erreur notification: {e}")
            return False


# ============================================================
# SECTION 8: REPORT GENERATION SERVICE
# ============================================================

class ReportGenerationService:
    """
    خدمة إنشاء التقارير
    """

    @staticmethod
    def generer_rapport_avancement(projet_id):
        """
        إنشاء تقرير تقدم المشروع
        """
        try:
            projet = projets_models.Projet.objects.get(id=projet_id)

            rapport = {
                'projet': {
                    'reference': projet.reference,
                    'nom': projet.nom,
                    'statut': projet.get_statut_display(),
                    'avancement': float(projet.pourcentage_avancement),
                },
                'lots': [],
            }

            for lot in projet.lots.all():
                lot_data = {
                    'numero': lot.numero,
                    'designation': lot.designation,
                    'avancement': float(lot.pourcentage_avancement),
                    'ouvrages': [],
                }

                for ouvrage in lot.ouvrages.all():
                    lot_data['ouvrages'].append({
                        'code': ouvrage.code,
                        'designation': ouvrage.designation,
                        'avancement': float(ouvrage.pourcentage_avancement),
                    })

                rapport['lots'].append(lot_data)

            return rapport

        except Exception as e:
            print(f"❌ Erreur génération rapport: {e}")
            return None

    @staticmethod
    def generer_rapport_financier(projet_id):
        """
        إنشاء تقرير مالي للمشروع
        """
        try:
            projet = projets_models.Projet.objects.get(id=projet_id)

            # حساب المجاميع
            decomptes = projet.decomptes.all()
            total_decomptes = decomptes.aggregate(
                total=Sum('montant_net')
            )['total'] or 0

            factures_extra = projet.factures_extra.filter(
                statut='PAYEE'
            )
            total_factures = factures_extra.aggregate(
                total=Sum('montant_ttc')
            )['total'] or 0

            return {
                'projet': {
                    'reference': projet.reference,
                    'nom': projet.nom,
                },
                'budget': {
                    'initial': float(projet.montant_initial),
                    'avenants': float(projet.montant_avenants),
                    'final': float(projet.montant_final),
                },
                'consommation': {
                    'decomptes': float(total_decomptes),
                    'factures_extra': float(total_factures),
                    'total': float(total_decomptes + total_factures),
                },
                'reste_a_payer': float(
                    projet.montant_final - (total_decomptes + total_factures)
                ),
                'pourcentage_consomme': float(
                    ((total_decomptes + total_factures) / projet.montant_final * 100)
                    if projet.montant_final > 0 else 0
                ),
            }

        except Exception as e:
            print(f"❌ Erreur rapport financier: {e}")
            return None                       
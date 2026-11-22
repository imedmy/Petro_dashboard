# apps/projets/management/commands/init_projets_data.py
"""
Commande de management pour initialiser les données de référence
du module Gestion des Projets.

Usage:
    python manage.py init_projets_data
    python manage.py init_projets_data --reset    # Supprimer et recréer
    python manage.py init_projets_data --verbose  # Afficher plus de détails
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.projets.models import (
    TypeProjet,
    Unite,
    DomaineCompetence,
    Workflow,
    WorkflowEtape,
)


class Command(BaseCommand):
    help = '🚀 Initialise les données de référence pour le module Gestion des Projets'

    def add_arguments(self, parser):
        """Ajouter des arguments optionnels à la commande"""
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Supprimer toutes les données de référence avant de les recréer',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Afficher plus de détails lors de l\'exécution',
        )
        parser.add_argument(
            '--skip-workflows',
            action='store_true',
            help='Ne pas initialiser les workflows',
        )

    def handle(self, *args, **options):
        reset = options['reset']
        verbose = options['verbose']
        skip_workflows = options['skip_workflows']

        self.stdout.write('')
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🚀 Initialisation des données de référence'))
        self.stdout.write(self.style.SUCCESS('   Module: Gestion des Projets & Marchés'))
        self.stdout.write('=' * 70)
        self.stdout.write('')

        if reset:
            self.stdout.write(self.style.WARNING('⚠️  Mode RESET activé'))
            self.stdout.write(self.style.WARNING('   Toutes les données de référence seront supprimées...'))
            self.stdout.write('')
            self._reset_data(verbose)

        # Statistiques
        stats = {
            'types_projets': {'created': 0, 'existing': 0},
            'unites': {'created': 0, 'existing': 0},
            'domaines': {'created': 0, 'existing': 0},
            'workflows': {'created': 0, 'existing': 0},
        }

        try:
            with transaction.atomic():
                # 1. Types de projets
                stats['types_projets'] = self._init_types_projets(verbose)

                # 2. Unités de mesure
                stats['unites'] = self._init_unites(verbose)

                # 3. Domaines de compétence
                stats['domaines'] = self._init_domaines_competence(verbose)

                # 4. Workflows (optionnel)
                if not skip_workflows:
                    stats['workflows'] = self._init_workflows(verbose)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur lors de l\'initialisation: {e}'))
            raise CommandError(f'Échec de l\'initialisation: {e}')

        # Résumé final
        self.stdout.write('')
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('✅ Résumé de l\'initialisation'))
        self.stdout.write('=' * 70)
        self.stdout.write(f'  📋 Types de projets:      {stats["types_projets"]["created"]} créés, {stats["types_projets"]["existing"]} existants')
        self.stdout.write(f'  📏 Unités de mesure:      {stats["unites"]["created"]} créées, {stats["unites"]["existing"]} existantes')
        self.stdout.write(f'  🎯 Domaines compétence:   {stats["domaines"]["created"]} créés, {stats["domaines"]["existing"]} existants')
        if not skip_workflows:
            self.stdout.write(f'  🔄 Workflows:             {stats["workflows"]["created"]} créés, {stats["workflows"]["existing"]} existants')
        self.stdout.write('=' * 70)
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Initialisation terminée avec succès!'))
        self.stdout.write('')
        self.stdout.write(self.style.NOTICE('💡 Prochaines étapes:'))
        self.stdout.write('   1. python manage.py makemigrations projets')
        self.stdout.write('   2. python manage.py migrate')
        self.stdout.write('   3. Accédez à http://localhost:8000/projets/')
        self.stdout.write('')

    def _reset_data(self, verbose):
        """Supprimer toutes les données de référence"""
        if verbose:
            self.stdout.write('  Suppression des workflows...')
        Workflow.objects.all().delete()

        if verbose:
            self.stdout.write('  Suppression des domaines de compétence...')
        DomaineCompetence.objects.all().delete()

        if verbose:
            self.stdout.write('  Suppression des unités...')
        Unite.objects.all().delete()

        if verbose:
            self.stdout.write('  Suppression des types de projets...')
        TypeProjet.objects.all().delete()

        self.stdout.write(self.style.WARNING('  ✅ Toutes les données ont été supprimées'))
        self.stdout.write('')

    def _init_types_projets(self, verbose):
        """Initialiser les types de projets"""
        self.stdout.write(self.style.HTTP_INFO('📋 Initialisation des types de projets...'))

        types_projets = [
            # Secteur Énergie (Pétrolier)
            ('PETROLIER', 'Secteur pétrolier', 'Énergie', 'Projets liés à l\'exploration et production pétrolière'),
            ('FORAGE', 'Forage', 'Énergie', 'Forage de puits de pétrole ou de gaz'),
            ('WORKOVER', 'Work Over', 'Énergie', 'Interventions de maintenance sur puits'),
            ('STATION', 'Stations pétrolières', 'Énergie', 'Construction/réhabilitation de stations'),
            ('PIPELINE', 'Pipelines', 'Énergie', 'Construction de pipelines et réseaux'),
            ('MAINTENANCE_IND', 'Maintenance industrielle', 'Énergie', 'Maintenance des installations'),

            # Secteur BTP
            ('TP', 'Travaux Publics', 'BTP', 'Routes, ponts, ouvrages d\'art'),
            ('BATIMENT', 'Construction de bâtiment', 'BTP', 'Bâtiments résidentiels, commerciaux'),
            ('GENIE_CIVIL', 'Génie Civil', 'BTP', 'Ouvrages de génie civil'),

            # Secteur Industrie
            ('INDUSTRIEL', 'Industriel', 'Industrie', 'Projets industriels divers'),
            ('ENGINS', 'Construction d\'engins', 'Industrie', 'Fabrication d\'engins et machines'),

            # Secteur Technique
            ('TECHNIQUE', 'Technique', 'Technique', 'Projets techniques divers'),
            ('ELECTRICITE', 'Électricité', 'Technique', 'Installations électriques'),
            ('INSTRUMENTATION', 'Instrumentation & Contrôle', 'Technique', 'Systèmes de mesure et contrôle'),

            # Secteur IT & Télécoms
            ('TELECOM', 'Télécommunications', 'Télécoms', 'Réseaux et infrastructures télécom'),
            ('INFORMATIQUE', 'Informatique', 'IT', 'Projets informatiques et logiciels'),

            # Autres secteurs
            ('AGRICOLE', 'Agricole', 'Agriculture', 'Projets agricoles'),
            ('HSE', 'HSE & Environnement', 'Support', 'Hygiène Sécurité Environnement'),
            ('LOGISTIQUE', 'Logistique', 'Support', 'Projets logistiques'),
            ('AUTRE', 'Autre', 'Autre', 'Autres types de projets'),
        ]

        created_count = 0
        existing_count = 0

        for code, libelle, categorie, description in types_projets:
            obj, created = TypeProjet.objects.get_or_create(
                code=code,
                defaults={
                    'libelle': libelle,
                    'categorie': categorie,
                    'description': description,
                    'actif': True,
                }
            )
            if created:
                created_count += 1
                if verbose:
                    self.stdout.write(f'    ✅ Créé: {libelle}')
            else:
                existing_count += 1
                if verbose:
                    self.stdout.write(f'    ⏭️  Existe déjà: {libelle}')

        self.stdout.write(self.style.SUCCESS(
            f'    ✅ {created_count} types créés, {existing_count} existants'
        ))
        self.stdout.write('')

        return {'created': created_count, 'existing': existing_count}

    def _init_unites(self, verbose):
        """Initialiser les unités de mesure"""
        self.stdout.write(self.style.HTTP_INFO('📏 Initialisation des unités de mesure...'))

        unites = [
            # Unités de longueur
            ('mm', 'Millimètre', 'mm'),
            ('cm', 'Centimètre', 'cm'),
            ('m', 'Mètre', 'm'),
            ('km', 'Kilomètre', 'km'),
            ('ml', 'Mètre linéaire', 'ml'),

            # Unités de surface
            ('m2', 'Mètre carré', 'm²'),
            ('ha', 'Hectare', 'ha'),

            # Unités de volume
            ('m3', 'Mètre cube', 'm³'),
            ('L', 'Litre', 'L'),
            ('m3h', 'Mètre cube heure', 'm³/h'),

            # Unités de masse
            ('g', 'Gramme', 'g'),
            ('kg', 'Kilogramme', 'kg'),
            ('T', 'Tonne', 'T'),

            # Unités de quantité
            ('U', 'Unité', 'U'),
            ('pce', 'Pièce', 'pce'),
            ('lot', 'Lot', 'lot'),
            ('ens', 'Ensemble', 'ens'),

            # Unités de temps
            ('h', 'Heure', 'h'),
            ('j', 'Jour', 'j'),
            ('mois', 'Mois', 'mois'),
            ('an', 'Année', 'an'),

            # Unités spécifiques pétrolier
            ('bbl', 'Baril', 'bbl'),
            ('tbf', 'Pieds de tube', 'tbf'),
            ('ppg', 'Livres par gallon', 'ppg'),

            # Unités financières
            ('Forfait', 'Forfait', 'F'),
            ('ENS', 'Ensemble', 'ENS'),
        ]

        created_count = 0
        existing_count = 0

        for code, libelle, symbole in unites:
            obj, created = Unite.objects.get_or_create(
                code=code,
                defaults={
                    'libelle': libelle,
                    'symbole': symbole,
                }
            )
            if created:
                created_count += 1
                if verbose:
                    self.stdout.write(f'    ✅ Créé: {libelle} ({symbole})')
            else:
                existing_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'    ✅ {created_count} unités créées, {existing_count} existantes'
        ))
        self.stdout.write('')

        return {'created': created_count, 'existing': existing_count}

    def _init_domaines_competence(self, verbose):
        """Initialiser les domaines de compétence"""
        self.stdout.write(self.style.HTTP_INFO('🎯 Initialisation des domaines de compétence...'))

        domaines = [
            # Secteur Énergie
            ('FORAGE', 'Forage', 'Énergie', 'Techniques de forage et complétion de puits', '#dc3545'),
            ('WO', 'Work Over', 'Énergie', 'Interventions sur puits existants', '#fd7e14'),
            ('STATION', 'Stations', 'Énergie', 'Stations de traitement et séparation', '#ffc107'),
            ('PIPELINE', 'Pipelines', 'Énergie', 'Transport de fluides par conduites', '#198754'),
            ('PRODUCTION', 'Production', 'Énergie', 'Exploitation et production', '#0dcaf0'),
            ('RESERVOIR', 'Réservoir', 'Énergie', 'Études de réservoir et simulation', '#6f42c1'),

            # Secteur BTP & Génie Civil
            ('GENIE_CIVIL', 'Génie Civil', 'BTP', 'Ouvrages en béton, fondations', '#0d6efd'),
            ('CHARPENTE', 'Charpente métallique', 'BTP', 'Structures métalliques', '#6610f2'),
            ('VRD', 'Voirie & Réseaux Divers', 'BTP', 'Routes, réseaux, assainissement', '#20c997'),

            # Secteur Technique
            ('ELECTRICITE', 'Électricité', 'Technique', 'Installations électriques HT/BT', '#6f42c1'),
            ('INSTRUMENTATION', 'Instrumentation & Contrôle', 'Technique', 'Capteurs, DCS, SCADA', '#20c997'),
            ('MECANIQUE', 'Mécanique', 'Industrie', 'Équipements tournants et statiques', '#6c757d'),
            ('SOUDURE', 'Soudure & Chaudronnerie', 'Industrie', 'Travaux de soudure', '#adb5bd'),
            (' TUYAUTERIE', 'Tuyauterie', 'Industrie', 'Fabrication et pose de tuyauteries', '#343a40'),

            # HSE & Support
            ('HSE', 'Hygiène Sécurité Environnement', 'Support', 'Sécurité et protection environnementale', '#d63384'),
            ('QUALITE', 'Qualité', 'Support', 'Contrôle qualité et assurance', '#0dcaf0'),
            ('LOGISTIQUE', 'Logistique', 'Support', 'Transport et approvisionnement', '#adb5bd'),
            ('ADMIN', 'Administratif & Financier', 'Support', 'Gestion administrative', '#343a40'),

            # IT & Télécoms
            ('IT', 'Informatique', 'IT', 'Développement et systèmes', '#0dcaf0'),
            ('TELECOM', 'Télécommunications', 'Télécoms', 'Réseaux et transmissions', '#6610f2'),
        ]

        created_count = 0
        existing_count = 0

        for code, libelle, categorie, description, couleur in domaines:
            obj, created = DomaineCompetence.objects.get_or_create(
                code=code.strip(),  # Enlever les espaces accidentels
                defaults={
                    'libelle': libelle,
                    'categorie': categorie,
                    'description': description,
                    'couleur': couleur,
                }
            )
            if created:
                created_count += 1
                if verbose:
                    self.stdout.write(f'    ✅ Créé: {libelle} ({categorie})')
            else:
                existing_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'    ✅ {created_count} domaines créés, {existing_count} existants'
        ))
        self.stdout.write('')

        return {'created': created_count, 'existing': existing_count}

    def _init_workflows(self, verbose):
        """Initialiser les workflows par défaut"""
        self.stdout.write(self.style.HTTP_INFO('🔄 Initialisation des workflows...'))

        workflows_data = [
            {
                'code': 'APPRO_DECOMPTE',
                'nom': 'Approbation Décompte',
                'description': 'Workflow d\'approbation des décomptes provisoires et définitifs',
                'etapes': [
                    {
                        'ordre': 1,
                        'nom': 'Préparation',
                        'action': 'CREATION',
                        'role_requis': 'chef_projet',
                        'delai_max_jours': 5,
                    },
                    {
                        'ordre': 2,
                        'nom': 'Vérification technique',
                        'action': 'VALIDATION',
                        'role_requis': 'directeur_technique',
                        'delai_max_jours': 3,
                    },
                    {
                        'ordre': 3,
                        'nom': 'Validation financière',
                        'action': 'VALIDATION',
                        'role_requis': 'directeur_financier',
                        'delai_max_jours': 5,
                    },
                    {
                        'ordre': 4,
                        'nom': 'Signature',
                        'action': 'SIGNATURE',
                        'role_requis': 'directeur_general',
                        'delai_max_jours': 2,
                    },
                ],
            },
            {
                'code': 'APPRO_AVENANT',
                'nom': 'Approbation Avenant',
                'description': 'Workflow d\'approbation des avenants au contrat',
                'etapes': [
                    {
                        'ordre': 1,
                        'nom': 'Rédaction',
                        'action': 'CREATION',
                        'role_requis': 'chef_projet',
                        'delai_max_jours': 7,
                    },
                    {
                        'ordre': 2,
                        'nom': 'Vérification juridique',
                        'action': 'VALIDATION',
                        'role_requis': 'juriste',
                        'delai_max_jours': 5,
                    },
                    {
                        'ordre': 3,
                        'nom': 'Approbation direction',
                        'action': 'VALIDATION',
                        'role_requis': 'directeur_general',
                        'delai_max_jours': 3,
                    },
                    {
                        'ordre': 4,
                        'nom': 'Signature client',
                        'action': 'SIGNATURE',
                        'role_requis': 'maitre_ouvrage',
                        'delai_max_jours': 15,
                    },
                ],
            },
            {
                'code': 'VALIDATION_LIVRABLE',
                'nom': 'Validation Livrable',
                'description': 'Workflow de validation des livrables du projet',
                'etapes': [
                    {
                        'ordre': 1,
                        'nom': 'Soumission',
                        'action': 'CREATION',
                        'role_requis': 'chef_projet',
                        'delai_max_jours': 0,
                    },
                    {
                        'ordre': 2,
                        'nom': 'Revue technique',
                        'action': 'VALIDATION',
                        'role_requis': 'responsable_technique',
                        'delai_max_jours': 5,
                    },
                    {
                        'ordre': 3,
                        'nom': 'Approbation client',
                        'action': 'VALIDATION',
                        'role_requis': 'maitre_ouvrage',
                        'delai_max_jours': 10,
                    },
                ],
            },
            {
                'code': 'APPRO_FACTURE_EXTRA',
                'nom': 'Approbation Facture Extra',
                'description': 'Workflow d\'approbation des factures pour travaux supplémentaires',
                'etapes': [
                    {
                        'ordre': 1,
                        'nom': 'Justification',
                        'action': 'CREATION',
                        'role_requis': 'chef_projet',
                        'delai_max_jours': 3,
                    },
                    {
                        'ordre': 2,
                        'nom': 'Vérification',
                        'action': 'VALIDATION',
                        'role_requis': 'directeur_technique',
                        'delai_max_jours': 5,
                    },
                    {
                        'ordre': 3,
                        'nom': 'Approbation',
                        'action': 'VALIDATION',
                        'role_requis': 'directeur_general',
                        'delai_max_jours': 3,
                    },
                ],
            },
        ]

        created_count = 0
        existing_count = 0

        for wf_data in workflows_data:
            workflow, created = Workflow.objects.get_or_create(
                code=wf_data['code'],
                defaults={
                    'nom': wf_data['nom'],
                    'description': wf_data['description'],
                    'actif': True,
                }
            )

            if created:
                created_count += 1
                # Créer les étapes
                for etape_data in wf_data['etapes']:
                    WorkflowEtape.objects.create(
                        workflow=workflow,
                        ordre=etape_data['ordre'],
                        nom=etape_data['nom'],
                        action=etape_data['action'],
                        role_requis=etape_data['role_requis'],
                        delai_max_jours=etape_data['delai_max_jours'],
                    )
                if verbose:
                    self.stdout.write(f'    ✅ Créé: {wf_data["nom"]} ({len(wf_data["etapes"])} étapes)')
            else:
                existing_count += 1
                if verbose:
                    self.stdout.write(f'    ⏭️  Existe déjà: {wf_data["nom"]}')

        self.stdout.write(self.style.SUCCESS(
            f'    ✅ {created_count} workflows créés, {existing_count} existants'
        ))
        self.stdout.write('')

        return {'created': created_count, 'existing': existing_count}
# core/management/commands/load_initial_data.py
from django.core.management.base import BaseCommand
from core.models import CompanyInfo, Page

class Command(BaseCommand):
    help = 'تحميل البيانات الأولية للشركة والصفحات'

    def handle(self, *args, **options):
        # 1. معلومات الشركة
        company, created = CompanyInfo.objects.get_or_create(
            name="شركة البترول الوطنية",
            defaults={
                'address': 'شارع النفط، الجزائر العاصمة',
                'phone': '+213 21 123 456',
                'email': 'contact@nationalpetro.dz',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✅ تم إنشاء معلومات الشركة'))

        # 2. الصفحات
        pages_data = [
            {'name_fr': 'Tableau de bord', 'name_ar': 'لوحة القيادة', 'url_name': 'dashboard', 'order': 1, 'is_active': True},
            {'name_fr': 'Gestion des Utilisateurs', 'name_ar': 'إدارة المستخدمين', 'url_name': 'users', 'order': 2, 'is_active': True},
            {'name_fr': 'Rapports', 'name_ar': 'التقارير', 'url_name': 'reports', 'order': 3, 'is_active': True},
            {'name_fr': 'Maintenance', 'name_ar': 'الصيانة', 'url_name': 'maintenance', 'order': 4, 'is_active': True},
            {'name_fr': 'Paramètres', 'name_ar': 'الإعدادات', 'url_name': 'settings', 'order': 5, 'is_active': True},
        ]

        for data in pages_data:
            page, created = Page.objects.get_or_create(
                url_name=data['url_name'],
                defaults=data
            )
            if created:
                self.stdout.write(f"✅ تم إنشاء الصفحة: {data['name_fr']}")

        self.stdout.write(self.style.SUCCESS('✅ تم تحميل جميع البيانات الأولية بنجاح'))
# core/management/commands/grant_all_permissions.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Page, PermissionMatrix

User = get_user_model()

class Command(BaseCommand):
    help = 'منح جميع الصلاحيات لجميع المستخدمين المتميزين (superusers)'

    def handle(self, *args, **options):
        # جلب جميع المستخدمين المتميزين
        superusers = User.objects.filter(is_superuser=True)
        
        if not superusers.exists():
            self.stdout.write(
                self.style.WARNING('❌ لا يوجد مستخدمون متميزون (superuser)')
            )
            return

        # جلب جميع الصفحات
        pages = Page.objects.all()
        
        if not pages.exists():
            self.stdout.write(
                self.style.WARNING('❌ لا توجد صفحات معرفة في قاعدة البيانات')
            )
            return

        # منح الصلاحيات الكاملة لكل superuser
        for user in superusers:
            for page in pages:
                perm, created = PermissionMatrix.objects.get_or_create(
                    user=user,
                    page=page,
                    defaults={
                        'can_consulte': True,
                        'can_insert': True,
                        'can_update': True,
                        'can_delete': True,
                    }
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ منحت جميع الصلاحيات للصفحة "{page.name_fr}" للمستخدم "{user.username}"'
                        )
                    )
                else:
                    # إذا كانت الصلاحية موجودة، نحدّثها
                    if not (perm.can_consulte and perm.can_insert and perm.can_update and perm.can_delete):
                        perm.can_consulte = True
                        perm.can_insert = True
                        perm.can_update = True
                        perm.can_delete = True
                        perm.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'🔄 تم تحديث الصلاحيات للصفحة "{page.name_fr}" للمستخدم "{user.username}"'
                            )
                        )

        self.stdout.write(
            self.style.SUCCESS('✅ تم منح جميع الصلاحيات لجميع المستخدمين المتميزين بنجاح.')
        )
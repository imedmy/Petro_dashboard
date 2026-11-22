# core/management/commands/populate_full_code.py
from django.core.management.base import BaseCommand
from core.models import ArticleFamily

def calculate_full_code(family):
    if family.parent:
        return f"{calculate_full_code(family.parent)}{family.code_segment}"
    return family.code_segment

class Command(BaseCommand):
    help = "ملء حقل full_code لجميع العائلات"

    def handle(self, *args, **options):
        families = ArticleFamily.objects.all().order_by('id')  # الجذر أولًا
        updated = 0

        for family in families:
            expected_code = calculate_full_code(family)
            if family.full_code != expected_code:
                family.full_code = expected_code
                family.save()
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(f'تم تحديث full_code لـ {updated} عائلة')
        )
# core/management/commands/cleanup_correlations.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import ArticleCorrelation, ArticleCorrelationWorkflow


class Command(BaseCommand):
    help = 'تنظيف الارتباطات والـ workflows منتهية الصلاحية'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='احتفاظ بالبيانات لمدة N يوم (افتراضي: 90)'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        cutoff_date = timezone.now().date() - timedelta(days=days)
        
        self.stdout.write(self.style.SUCCESS(f'بدء التنظيف...'))
        self.stdout.write(f'  📅 الاحتفاظ بالبيانات حتى: {cutoff_date}')
        
        # 1. تنظيف الارتباطات القديمة
        old_correlations = ArticleCorrelation.objects.filter(
            last_movement_date__lt=cutoff_date,
            is_verified=False  # لا نحذف المرتبطات المُتحقق منها يدويًا
        )
        correlations_count = old_correlations.count()
        old_correlations.delete()
        
        # 2. تنظيف workflows القديمة
        old_workflows = ArticleCorrelationWorkflow.objects.filter(
            created_at__lt=timezone.now() - timedelta(days=30)
        )
        workflows_count = old_workflows.count()
        old_workflows.delete()
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✅ اكتمل التنظيف!'))
        self.stdout.write(f'  🗑️ ارتباطات محذوفة: {correlations_count}')
        self.stdout.write(f'  🗑️ workflows محذوفة: {workflows_count}')
        self.stdout.write('='*60)
# core/management/commands/update_correlations_incremental.py

from django.core.management.base import BaseCommand
from django.db import connections
from django.utils import timezone
from datetime import timedelta, date
from core.models import ArticleCorrelation
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'تحديث تزايدي لجدول الارتباطات (فقط الحركات الجديدة)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--cod-art',
            type=str,
            help='كود مقال محدد للتحديث (اختياري)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='عدد الأيام منذ آخر تحديث (افتراضي: 7)'
        )
    
    def handle(self, *args, **options):
        cod_art_filter = options.get('cod_art')
        days = options['days']
        
        self.stdout.write(self.style.SUCCESS('بدء التحديث التزايدي للارتباطات...'))
        
        # === 1. تحديد فترة التحديث ===
        date_to = date.today()
        date_from = date_to - timedelta(days=days)
        
        self.stdout.write(f'  📅 الفترة: {date_from} إلى {date_to}')
        
        # === 2. جلب آخر تاريخ معالجة لكل مقال ===
        if cod_art_filter:
            articles_to_update = [cod_art_filter]
            last_dates = {cod_art_filter: date_from}
        else:
            # جلب جميع المقالات التي لها ارتباطات
            last_dates = {}
            for corr in ArticleCorrelation.objects.values('cod_art_ref').distinct():
                cod_art = corr['cod_art_ref']
                last_date = ArticleCorrelation.objects.filter(
                    cod_art_ref=cod_art
                ).aggregate(max_date=models.Max('last_movement_date'))['max_date']
                
                last_dates[cod_art] = last_date if last_date else date_from
                articles_to_update = list(last_dates.keys())
        
        self.stdout.write(self.style.SUCCESS(f'  📊 مقالات للتحديث: {len(articles_to_update)}'))
        
        # === 3. تحديث كل مقال ===
        total_new_correlations = 0
        
        for cod_art_ref in articles_to_update:
            last_date = last_dates[cod_art_ref]
            
            # تخطي إذا لم تكن هناك حركات جديدة
            if last_date >= date_to:
                continue
            
            try:
                new_correlations = self._analyze_new_movements(
                    cod_art_ref, last_date, date_to
                )
                
                # تحديث الارتباطات الموجودة أو إضافة جديدة
                for corr in new_correlations:
                    obj, created = ArticleCorrelation.objects.update_or_create(
                        cod_art_ref=corr['cod_art_ref'],
                        cod_art_related=corr['cod_art_related'],
                        date_min=corr['date_min'],
                        date_max=corr['date_max'],
                        defaults=corr
                    )
                    
                    if created:
                        total_new_correlations += 1
                    else:
                        # تحديث الارتباط الموجود
                        obj.support_count += corr['support_count']
                        obj.last_movement_date = corr['last_movement_date']
                        obj.update_confidence_level()
                        obj.save()
                
                self.stdout.write(f'  ✓ {cod_art_ref}: +{len(new_correlations)} ارتباطات')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ خطأ في {cod_art_ref}: {str(e)}'))
                logger.error(f"Erreur mise à jour {cod_art_ref}: {e}")
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✅ اكتمل التحديث التزايدي!'))
        self.stdout.write(f'  🆕 ارتباطات جديدة: {total_new_correlations}')
        self.stdout.write(f'  📅 تاريخ الانتهاء: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write('='*60)
    
    def _analyze_new_movements(self, cod_art_ref, date_from, date_to):
        """
        تحليل الحركات الجديدة فقط
        """
        correlations = []
        
        with connections['sql_server'].cursor() as cursor:
            # جلب الحركات الجديدة للمقال المرجعي
            cursor.execute("""
                SELECT COD_ART, DATE_B, NUMERO_BON, QTE_MVT
                FROM (
                    SELECT COD_ART, DATE_B, NUMERO_BON, QTE_MVT FROM bon_b1_ebc
                    WHERE COD_ART = %s AND DATE_B > %s AND DATE_B <= %s
                    
                    UNION ALL
                    
                    SELECT COD_ART, DATE_B, NUMERO_BON, QTE_MVT FROM bon_b2_ebc
                    WHERE COD_ART = %s AND DATE_B > %s AND DATE_B <= %s
                ) AS new_movements
                ORDER BY DATE_B
            """, [cod_art_ref, date_from, date_to, cod_art_ref, date_from, date_to])
            
            new_movements = cursor.fetchall()
            
            if not new_movements:
                return []
            
            # تحليل الارتباطات الجديدة
            related_map = {}
            
            for mov in new_movements:
                mov_date = mov[1]
                window_min = mov_date - timedelta(days=2)
                window_max = mov_date + timedelta(days=2)
                
                cursor.execute("""
                    SELECT COD_ART, DATE_B
                    FROM (
                        SELECT COD_ART, DATE_B FROM bon_b1_ebc
                        WHERE DATE_B >= %s AND DATE_B <= %s AND COD_ART != %s
                        
                        UNION ALL
                        
                        SELECT COD_ART, DATE_B FROM bon_b2_ebc
                        WHERE DATE_B >= %s AND DATE_B <= %s AND COD_ART != %s
                    ) AS related
                """, [window_min, window_max, cod_art_ref, window_min, window_max, cod_art_ref])
                
                for related_row in cursor.fetchall():
                    related_cod = related_row[0]
                    related_date = related_row[1]
                    
                    if related_cod not in related_map:
                        related_map[related_cod] = {'count': 0, 'time_gaps': []}
                    
                    related_map[related_cod]['count'] += 1
                    time_gap = (related_date - mov_date).total_seconds() / 3600
                    related_map[related_cod]['time_gaps'].append(time_gap)
            
            # بناء الارتباطات
            for related_cod, data in related_map.items():
                if data['count'] < 3:  # حد أدنى أقل للتحديث التزايدي
                    continue
                
                avg_time_gap = sum(data['time_gaps']) / len(data['time_gaps']) if data['time_gaps'] else 0
                
                correlations.append({
                    'cod_art_ref': cod_art_ref,
                    'cod_art_related': related_cod,
                    'support_count': data['count'],
                    'support_percent': 0,  # سيتم حسابه لاحقًا
                    'confidence_percent': 0,
                    'lift_ratio': 1.0,
                    'avg_time_gap_hours': round(avg_time_gap, 2),
                    'sequence_order': 'mixed',
                    'date_min': date_from,
                    'date_max': date_to,
                    'last_movement_date': date_to,
                    'confidence_level': 'low',
                    'is_active': True,
                    'is_verified': False
                })
        
        return correlations
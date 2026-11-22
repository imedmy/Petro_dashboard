# core/management/commands/populate_correlations.py

from django.core.management.base import BaseCommand
from django.db import connections
from django.utils import timezone
from datetime import timedelta, date
from core.models import ArticleCorrelation
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'ملء جدول الارتباطات بين المقالات (Initial Population)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='عدد الأيام للتحليل الخلفي (افتراضي: 365 يوم)'
        )
        parser.add_argument(
            '--min-support',
            type=int,
            default=5,
            help='الحد الأدنى لعدد التكرارات (افتراضي: 5)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='حجم الدفعة للمعالجة (افتراضي: 1000)'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        min_support = options['min_support']
        batch_size = options['batch_size']
        
        date_to = date.today()
        date_from = date_to - timedelta(days=days)
        
        self.stdout.write(self.style.SUCCESS(f'بدء تحليل الارتباطات...'))
        self.stdout.write(f'  📅 الفترة: {date_from} إلى {date_to}')
        self.stdout.write(f'  📊 الحد الأدنى للدعم: {min_support}')
        self.stdout.write(f'  📦 حجم الدفعة: {batch_size}')
        
        total_correlations = 0
        total_articles = 0
        
        # === 1. جلب جميع المقالات الفريدة من الحركات ===
        self.stdout.write('\n🔍 جاري جلب قائمة المقالات...')
        
        with connections['sql_server'].cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT COD_ART 
                FROM (
                    SELECT COD_ART FROM bon_b1_ebc WHERE DATE_B >= %s AND DATE_B <= %s
                    UNION
                    SELECT COD_ART FROM bon_b2_ebc WHERE DATE_B >= %s AND DATE_B <= %s
                ) AS all_articles
                ORDER BY COD_ART
            """, [date_from, date_to, date_from, date_to])
            
            articles = [row[0] for row in cursor.fetchall()]
            total_articles = len(articles)
        
        self.stdout.write(self.style.SUCCESS(f'✓ تم العثور على {total_articles} مقال'))
        
        # === 2. معالجة كل مقال ===
        for i, cod_art_ref in enumerate(articles, 1):
            if i % 100 == 0:
                self.stdout.write(f'  📌 المعالجة: {i}/{total_articles} ({i/total_articles*100:.1f}%)')
            
            try:
                # جلب حركات هذا المقال
                correlations = self._analyze_article_correlations(
                    cod_art_ref, date_from, date_to, min_support, batch_size
                )
                
                # حفظ الارتباطات في قاعدة البيانات
                for corr in correlations:
                    ArticleCorrelation.objects.update_or_create(
                        cod_art_ref=corr['cod_art_ref'],
                        cod_art_related=corr['cod_art_related'],
                        date_min=date_from,
                        date_max=date_to,
                        defaults=corr
                    )
                    total_correlations += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ خطأ في {cod_art_ref}: {str(e)}'))
                logger.error(f"Erreur analyse {cod_art_ref}: {e}")
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✅ اكتمل التحليل!'))
        self.stdout.write(f'  📊 إجمالي الارتباطات: {total_correlations}')
        self.stdout.write(f'  📦 إجمالي المقالات: {total_articles}')
        self.stdout.write(f'  📅 تاريخ الانتهاء: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write('='*60)
    
    def _analyze_article_correlations(self, cod_art_ref, date_from, date_to, min_support, batch_size):
        """
        تحليل الارتباطات لمقال معين
        """
        correlations = []
        
        with connections['sql_server'].cursor() as cursor:
            # 1. جلب حركات المقال المرجعي
            cursor.execute("""
                SELECT COD_ART, DATE_B, NUMERO_BON, QTE_MVT, 'b1' AS SOURCE
                FROM bon_b1_ebc
                WHERE COD_ART = %s AND DATE_B >= %s AND DATE_B <= %s
                
                UNION ALL
                
                SELECT COD_ART, DATE_B, NUMERO_BON, QTE_MVT, 'b2' AS SOURCE
                FROM bon_b2_ebc
                WHERE COD_ART = %s AND DATE_B >= %s AND DATE_B <= %s
                
                ORDER BY DATE_B
            """, [cod_art_ref, date_from, date_to, cod_art_ref, date_from, date_to])
            
            ref_movements = cursor.fetchall()
            total_ref_movements = len(ref_movements)
            
            if total_ref_movements == 0:
                return []
            
            # 2. لكل حركة، البحث عن مقالات أخرى في نفس الفترة (±2 يوم)
            related_map = {}
            
            for mov in ref_movements:
                mov_date = mov[1]
                window_min = mov_date - timedelta(days=2)
                window_max = mov_date + timedelta(days=2)
                
                # جلب المقالات الأخرى في نفس النافذة
                cursor.execute("""
                    SELECT COD_ART, DATE_B, NUMERO_BON
                    FROM (
                        SELECT COD_ART, DATE_B, NUMERO_BON FROM bon_b1_ebc
                        WHERE DATE_B >= %s AND DATE_B <= %s AND COD_ART != %s
                        
                        UNION ALL
                        
                        SELECT COD_ART, DATE_B, NUMERO_BON FROM bon_b2_ebc
                        WHERE DATE_B >= %s AND DATE_B <= %s AND COD_ART != %s
                    ) AS all_movements
                """, [window_min, window_max, cod_art_ref, window_min, window_max, cod_art_ref])
                
                for related_row in cursor.fetchall():
                    related_cod = related_row[0]
                    related_date = related_row[1]
                    
                    if related_cod not in related_map:
                        related_map[related_cod] = {
                            'count': 0,
                            'time_gaps': [],
                            'orders': []
                        }
                    
                    related_map[related_cod]['count'] += 1
                    
                    # حساب الفاصل الزمني
                    time_gap = (related_date - mov_date).total_seconds() / 3600  # بالساعات
                    related_map[related_cod]['time_gaps'].append(time_gap)
                    
                    # تحديد التسلسل
                    if related_date == mov_date:
                        related_map[related_cod]['orders'].append('simultaneous')
                    elif related_date < mov_date:
                        related_map[related_cod]['orders'].append('before')
                    else:
                        related_map[related_cod]['orders'].append('after')
            
            # 3. تصفية وحساب المقاييس
            for related_cod, data in related_map.items():
                if data['count'] < min_support:
                    continue
                
                support_count = data['count']
                support_percent = round((support_count / total_ref_movements) * 100, 2)
                
                # متوسط الفاصل الزمني
                avg_time_gap = sum(data['time_gaps']) / len(data['time_gaps']) if data['time_gaps'] else 0
                
                # تحديد نوع التسلسل
                order_counts = {
                    'before': data['orders'].count('before'),
                    'after': data['orders'].count('after'),
                    'simultaneous': data['orders'].count('simultaneous')
                }
                dominant_order = max(order_counts, key=order_counts.get)
                if order_counts['before'] > 0 and order_counts['after'] > 0:
                    sequence_order = 'mixed'
                else:
                    sequence_order = dominant_order
                
                # مستوى الثقة
                if support_percent >= 70:
                    confidence_level = 'high'
                elif support_percent >= 40:
                    confidence_level = 'medium'
                else:
                    confidence_level = 'low'
                
                correlations.append({
                    'cod_art_ref': cod_art_ref,
                    'cod_art_related': related_cod,
                    'support_count': support_count,
                    'support_percent': support_percent,
                    'confidence_percent': support_percent,  # مبسط للبدء
                    'lift_ratio': 1.0,  # يمكن حسابه لاحقًا
                    'avg_time_gap_hours': round(avg_time_gap, 2),
                    'sequence_order': sequence_order,
                    'date_min': date_from,
                    'date_max': date_to,
                    'last_movement_date': date_to,
                    'confidence_level': confidence_level,
                    'is_active': True,
                    'is_verified': False
                })
        
        return correlations
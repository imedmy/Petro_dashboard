# apps/articles/services.py

from django.db import connections
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
import logging
from typing import Dict, List, Optional
from core.models import ArticleAnalysisWorkflow, ArticleSequencePattern

logger = logging.getLogger(__name__)


class ArticleSequenceAnalyzer:
    """
    محلل تسلسلي متقدم للمقالات المرتبطة
    يدعم خوارزميات متعددة مع تتبع التقدم
    """
    
    def __init__(self, workflow: ArticleAnalysisWorkflow):
        self.workflow = workflow
        self.cod_art = workflow.cod_art
        self.window_days = workflow.window_days
        self.min_support = float(workflow.min_support)
        self.min_confidence = float(workflow.min_confidence)
    
    def analyze(self) -> Dict:
        """
        تشغيل التحليل حسب الخوارزمية المحددة
        """
        self.workflow.status = 'processing'
        self.workflow.started_at = timezone.now()
        self.workflow.save()
        
        try:
            algorithm = self.workflow.algorithm
            
            if algorithm == 'simple_window':
                result = self._simple_window_analysis()
            elif algorithm == 'sequence_mining':
                result = self._sequence_mining_analysis()
            elif algorithm == 'frequency_based':
                result = self._frequency_based_analysis()
            else:  # hybrid
                result = self._hybrid_analysis()
            
            self.workflow.mark_completed(result)
            return result
            
        except Exception as e:
            logger.error(f"Erreur analyse: {str(e)}")
            self.workflow.mark_failed(str(e))
            raise
    
    def _get_movements(self) -> List[Dict]:
        """جلب جميع حركات المقال"""
        sql = """
        SELECT 
            COD_ART, DATE_B, NUMERO_BON, QTE_MVT, 'b1' AS SOURCE
        FROM bon_b1_ebc
        WHERE COD_ART = %s AND DATE_B >= DATEADD(YEAR, -2, GETDATE())
        
        UNION ALL
        
        SELECT 
            COD_ART, DATE_B, NUMERO_BON, QTE_MVT, 'b2' AS SOURCE
        FROM bon_b2_ebc
        WHERE COD_ART = %s AND DATE_B >= DATEADD(YEAR, -2, GETDATE())
        
        ORDER BY DATE_B DESC
        """
        
        with connections['sql_server'].cursor() as cursor:
            cursor.execute(sql, [self.cod_art, self.cod_art])
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def _simple_window_analysis(self) -> Dict:
        """
        الخوارزمية البسيطة: نافذة زمنية ±N يوم
        """
        movements = self._get_movements()
        total_movements = len(movements)
        
        if total_movements == 0:
            return {
                'cod_art': self.cod_art,
                'total_movements': 0,
                'algorithm': 'simple_window',
                'related_articles': []
            }
        
        related_map = {}
        
        for i, mov in enumerate(movements):
            # تحديث التقدم كل 100 حركة
            if i % 100 == 0:
                self.workflow.update_progress(i, total_movements)
            
            mov_date = mov['DATE_B']
            date_min = mov_date - timedelta(days=self.window_days)
            date_max = mov_date + timedelta(days=self.window_days)
            
            # جلب المقالات الأخرى في نفس الفترة
            related = self._find_related_in_window(mov_date, date_min, date_max)
            
            for related_cod, count in related.items():
                if related_cod not in related_map:
                    related_map[related_cod] = 0
                related_map[related_cod] += count
        
        # حساب المقاييس
        related_articles = self._calculate_metrics(related_map, total_movements)
        
        return {
            'cod_art': self.cod_art,
            'total_movements': total_movements,
            'analysis_window_days': self.window_days,
            'algorithm': 'simple_window',
            'related_articles': related_articles[:20]  # أفضل 20 نتيجة
        }
    
    def _sequence_mining_analysis(self) -> Dict:
        """
        خوارزمية متقدمة: اكتشاف أنماط التسلسل
        - Apriori-like algorithm للـ itemsets
        - حساب التسلسل الزمني (قبل/بعد)
        """
        movements = self._get_movements()
        total_movements = len(movements)
        
        if total_movements == 0:
            return {
                'cod_art': self.cod_art,
                'total_movements': 0,
                'algorithm': 'sequence_mining',
                'related_articles': []
            }
        
        # تجميع الحركات حسب رقم الطلبية
        orders_map = self._group_by_order(movements)
        
        # اكتشاف الأنماط المتكررة
        patterns = self._mine_sequences(orders_map)
        
        # حساب مقاييس القوة
        related_articles = self._calculate_sequence_metrics(patterns, total_movements)
        
        return {
            'cod_art': self.cod_art,
            'total_movements': total_movements,
            'algorithm': 'sequence_mining',
            'patterns_found': len(patterns),
            'related_articles': related_articles[:20]
        }
    
    def _hybrid_analysis(self) -> Dict:
        """
        خوارزمية هجينة: تجمع بين النافذة الزمنية والتسلسل
        """
        # تشغيل التحليل البسيط
        simple_result = self._simple_window_analysis()
        
        # تشغيل تحليل التسلسل
        sequence_result = self._sequence_mining_analysis()
        
        # دمج النتائج مع ترجيح
        combined = self._combine_results(simple_result, sequence_result)
        
        return {
            'cod_art': self.cod_art,
            'total_movements': simple_result['total_movements'],
            'algorithm': 'hybrid',
            'simple_count': len(simple_result['related_articles']),
            'sequence_count': len(sequence_result['related_articles']),
            'related_articles': combined[:20]
        }
    
    def _find_related_in_window(self, ref_date: datetime, 
                                 date_min: datetime, 
                                 date_max: datetime) -> Dict[str, int]:
        """
        جلب المقالات المرتبطة في نافذة زمنية
        باستخدام SQL Server مباشرة للأداء
        """
        sql = """
        SELECT COD_ART, COUNT(*) as co_occurrence
        FROM (
            SELECT COD_ART, DATE_B, NUMERO_BON FROM bon_b1_ebc
            WHERE DATE_B >= %s AND DATE_B <= %s AND COD_ART != %s
            
            UNION ALL
            
            SELECT COD_ART, DATE_B, NUMERO_BON FROM bon_b2_ebc
            WHERE DATE_B >= %s AND DATE_B <= %s AND COD_ART != %s
        ) AS all_movements
        GROUP BY COD_ART
        """
        
        with connections['sql_server'].cursor() as cursor:
            cursor.execute(sql, [
                date_min, date_max, self.cod_art,
                date_min, date_max, self.cod_art
            ])
            
            return {row[0]: row[1] for row in cursor.fetchall()}
    
    def _group_by_order(self, movements: List[Dict]) -> Dict[str, List[Dict]]:
        """تجميع الحركات حسب رقم الطلبية"""
        orders = {}
        for mov in movements:
            order_num = mov.get('NUMERO_BON')
            if order_num:
                if order_num not in orders:
                    orders[order_num] = []
                orders[order_num].append(mov)
        return orders
    
    def _mine_sequences(self, orders_map: Dict) -> List[Dict]:
        """
        استخراج أنماط التسلسل من الطلبات
        """
        patterns = []
        
        for order_num, items in orders_map.items():
            # تحليل العناصر في نفس الطلبية
            for item in items:
                if item['COD_ART'] != self.cod_art:
                    patterns.append({
                        'related_cod': item['COD_ART'],
                        'type': 'simultaneous',
                        'order': order_num
                    })
        
        return patterns
    
    def _calculate_metrics(self, related_map: Dict[str, int], 
                          total_movements: int) -> List[Dict]:
        """
        حساب مقاييس القوة للارتباط
        """
        results = []
        
        for related_cod, co_occurrence in related_map.items():
            rate = co_occurrence / total_movements if total_movements > 0 else 0
            
            # تحديد مستوى الثقة
            if rate >= 0.70:
                confidence_level = 'high'
            elif rate >= 0.40:
                confidence_level = 'medium'
            else:
                confidence_level = 'low'
            
            # جلب معلومات المقال المرتبط
            lib_art = self._get_article_info(related_cod)
            
            results.append({
                'cod_art': related_cod,
                'lib_art': lib_art,
                'co_occurrence': co_occurrence,
                'co_occurrence_rate': round(rate * 100, 2),
                'confidence_level': confidence_level,
                'support_count': co_occurrence,
                'support_percent': round(rate * 100, 2)
            })
        
        # ترتيب حسب معدل التواجد
        results.sort(key=lambda x: x['co_occurrence_rate'], reverse=True)
        return results
    
    def _calculate_sequence_metrics(self, patterns: List[Dict], 
                                    total_movements: int) -> List[Dict]:
        """
        حساب مقاييس التسلسل
        """
        # تجميع الأنماط
        related_map = {}
        for pattern in patterns:
            cod = pattern['related_cod']
            if cod not in related_map:
                related_map[cod] = {'count': 0, 'types': []}
            related_map[cod]['count'] += 1
            related_map[cod]['types'].append(pattern['type'])
        
        results = []
        for related_cod, data in related_map.items():
            rate = data['count'] / total_movements if total_movements > 0 else 0
            
            results.append({
                'cod_art': related_cod,
                'co_occurrence': data['count'],
                'co_occurrence_rate': round(rate * 100, 2),
                'sequence_types': list(set(data['types'])),
                'confidence_level': 'high' if rate >= 0.5 else 'medium' if rate >= 0.2 else 'low',
                'lib_art': self._get_article_info(related_cod)
            })
        
        results.sort(key=lambda x: x['co_occurrence_rate'], reverse=True)
        return results
    
    def _combine_results(self, simple: Dict, sequence: Dict) -> List[Dict]:
        """
        دمج نتائج الخوارزميات المختلفة
        """
        combined_map = {}
        
        # إضافة النتائج البسيطة
        for item in simple.get('related_articles', []):
            cod = item['cod_art']
            combined_map[cod] = {
                **item,
                'simple_score': item['co_occurrence_rate'],
                'sequence_score': 0
            }
        
        # إضافة نتائج التسلسل
        for item in sequence.get('related_articles', []):
            cod = item['cod_art']
            if cod in combined_map:
                combined_map[cod]['sequence_score'] = item['co_occurrence_rate']
                # تحديث النتيجة الإجمالية
                combined_map[cod]['combined_score'] = (
                    combined_map[cod]['simple_score'] * 0.6 + 
                    combined_map[cod]['sequence_score'] * 0.4
                )
            else:
                combined_map[cod] = {
                    **item,
                    'simple_score': 0,
                    'sequence_score': item['co_occurrence_rate'],
                    'combined_score': item['co_occurrence_rate'] * 0.4
                }
        
        # ترتيب حسب النتيجة المركبة
        results = list(combined_map.values())
        results.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
        return results
    
    def _get_article_info(self, cod_art: str) -> str:
        """جلب معلومات المقال من SQL Server"""
        sql = "SELECT TOP 1 LIB_ART FROM ARTICLE WHERE COD_ART = %s"
        
        try:
            with connections['sql_server'].cursor() as cursor:
                cursor.execute(sql, [cod_art])
                row = cursor.fetchone()
                return row[0] if row else 'Inconnu'
        except:
            return 'Inconnu'


def create_analysis_workflow(user, session_key: str, cod_art: str, 
                            algorithm: str = 'hybrid',
                            window_days: int = 2) -> ArticleAnalysisWorkflow:
    """
    إنشاء workflow تحليل جديد
    """
    # إلغاء التحليلات القديمة لنفس المقال والجلسة
    ArticleAnalysisWorkflow.objects.filter(
        session_key=session_key,
        cod_art=cod_art,
        status__in=['pending', 'processing']
    ).update(status='expired')
    
    # إنشاء workflow جديد
    workflow = ArticleAnalysisWorkflow.objects.create(
        user=user,
        session_key=session_key,
        cod_art=cod_art,
        algorithm=algorithm,
        window_days=window_days,
        expires_at=timezone.now() + timedelta(hours=24)  # النتائج صالحة 24 ساعة
    )
    
    return workflow


def get_or_start_analysis(workflow_id: str) -> Dict:
    """
    الحصول على نتائج التحليل أو بدء معالجته
    """
    try:
        workflow = ArticleAnalysisWorkflow.objects.get(id=workflow_id)
        
        # التحقق من انتهاء الصلاحية
        if workflow.is_expired():
            workflow.status = 'expired'
            workflow.save()
            return {
                'status': 'expired',
                'message': 'Résultats expirés. Veuillez relancer l\'analyse.'
            }
        
        # إذا اكتمل التحليل، إرجاع النتائج
        if workflow.status == 'completed':
            return {
                'status': 'completed',
                'progress': 100,
                'result': workflow.analysis_result
            }
        
        # إذا فشل التحليل
        if workflow.status == 'failed':
            return {
                'status': 'failed',
                'error': workflow.error_message
            }
        
        # إذا كان قيد المعالجة، إرجاع التقدم
        if workflow.status == 'processing':
            return {
                'status': 'processing',
                'progress': workflow.progress_percent,
                'processed': workflow.processed_movements,
                'total': workflow.total_movements
            }
        
        # إذا كان في الانتظار، بدء التحليل
        if workflow.status == 'pending':
            analyzer = ArticleSequenceAnalyzer(workflow)
            result = analyzer.analyze()
            
            return {
                'status': 'completed',
                'progress': 100,
                'result': result
            }
        
    except ArticleAnalysisWorkflow.DoesNotExist:
        return {
            'status': 'error',
            'message': 'Analyse non trouvée'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


def cleanup_expired_workflows():
    """
    تنظيف التحليلات منتهية الصلاحية (تشغيل دوري)
    """
    expired = ArticleAnalysisWorkflow.objects.filter(
        expires_at__lt=timezone.now(),
        status__in=['pending', 'processing', 'completed']
    )
    count = expired.count()
    expired.update(status='expired')
    logger.info(f"Nettoyé {count} workflows expirés")
    return count

    # =============================================================================
# ✅ خدمات التحديث التزايدي لـ ArticleCorrelation
# =============================================================================

def update_correlations_incremental(cod_art_ref=None, days=7, min_support=3):
    """
    تحديث تزايدي لجدول ArticleCorrelation
    - يفحص فقط الحركات الجديدة منذ آخر تحديث
    - يُحدِّف الارتباطات الموجودة أو يُنشئ جديدة
    """
    from django.db import connections
    from datetime import timedelta, date
    from django.utils import timezone
    
    date_to = date.today()
    date_from = date_to - timedelta(days=days)
    
    # إذا تم تحديد مقال معين
    if cod_art_ref:
        articles_to_update = [cod_art_ref]
    else:
        # جلب جميع المقالات التي لها ارتباطات
        articles_to_update = ArticleCorrelation.objects.values_list(
            'cod_art_ref', flat=True
        ).distinct()
    
    total_new = 0
    total_updated = 0
    
    for cod_art in articles_to_update:
        # جلب آخر تاريخ معالجة لهذا المقال
        last_processed = ArticleCorrelation.objects.filter(
            cod_art_ref=cod_art
        ).aggregate(max_date=models.Max('last_movement_date'))['max_date']
        
        effective_from = last_processed if last_processed else date_from
        
        # تخطي إذا لم تكن هناك حركات جديدة
        if effective_from >= date_to:
            continue
        
        # تحليل الحركات الجديدة
        new_correlations = _analyze_new_movements(
            cod_art, effective_from, date_to, min_support
        )
        
        # تحديث أو إنشاء الارتباطات
        for corr_data in new_correlations:
            obj, created = ArticleCorrelation.objects.update_or_create(
                cod_art_ref=corr_data['cod_art_ref'],
                cod_art_related=corr_data['cod_art_related'],
                date_min=corr_data['date_min'],
                date_max=corr_data['date_max'],
                defaults=corr_data
            )
            if created:
                total_new += 1
            else:
                total_updated += 1
    
    return {'new': total_new, 'updated': total_updated}


def _analyze_new_movements(cod_art_ref, date_from, date_to, min_support):
    """
    تحليل الحركات الجديدة فقط لتحديث الارتباطات
    """
    from django.db import connections
    from datetime import timedelta
    
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
            if data['count'] < min_support:
                continue
            
            avg_time_gap = sum(data['time_gaps']) / len(data['time_gaps']) if data['time_gaps'] else 0
            
            # حساب نسبة الدعم (مبسط)
            total_ref = len(new_movements)
            support_percent = round((data['count'] / total_ref) * 100, 2) if total_ref > 0 else 0
            
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
                'support_count': data['count'],
                'support_percent': support_percent,
                'confidence_percent': support_percent,
                'lift_ratio': 1.0,
                'avg_time_gap_hours': round(avg_time_gap, 2),
                'sequence_order': 'mixed',
                'date_min': date_from,
                'date_max': date_to,
                'last_movement_date': date_to,
                'confidence_level': confidence_level,
                'is_active': True,
                'is_verified': False
            })
    
    return correlations
#!/usr/bin/env python
"""
Script لملء جدول stock_evolution لكل المقالات الموجودة في جدول STOCK
يمكن تشغيله ليلاً عبر: python fill_stock_evolution.py

المنطق:
- لكل (cod_art, val_art, nat_stock) في جدول STOCK:
  - نحصل على stock_actuel
  - نجلب جميع الحركات من fiche_ebc لهذا cod_art
  - لكل حركة، نحدد nat_stock الفعلي:
    * B1/A1/A2/A3/A4 → من Etat_b1
    * B2 → من Etat_b2
    * B3/R1/R2/R3/R4 → من Etat_b3
    * B4 → من Etat_b4
    * INV أو فارغ → من جدول STOCK (إذا سطر واحد نستخدم nat_stock، وإلا نستخدم '1')
  - نطبق الخوارزمية العكسية
  - نحفظ النتائج في stock_evolution
"""
import os
import sys
import django
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'petro_dashboard.settings')
django.setup()

from django.db import connections
from django.utils import timezone
import logging

# إعداد الـ logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fill_stock_evolution.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# =============================================================================
# ✅ دوال مساعدة
# =============================================================================

def get_nature_rules():
    """جلب قواعد sign من جدول naturebon (MySQL)"""
    from core.models import NatureBon
    nature_rules = {}
    try:
        for nb in NatureBon.objects.all():
            nature_rules[nb.code_nature] = nb.sign if nb.sign is not None else 0
    except Exception as e:
        logger.warning(f"Erreur chargement naturebon: {e}")
    return nature_rules


def get_nat_stock_from_etat(cursor, nature_bon, num, cod_art):
    """
    تحديد nat_stock من جداول etat_bX حسب nature_bon
    """
    nature_upper = nature_bon.upper().strip() if nature_bon else ''
    
    # تحديد جدول etat المناسب
    etat_table = None
    if nature_upper in ('B1', 'A1', 'A2', 'A3', 'A4'):
        etat_table = 'Etat_b1'
    elif nature_upper == 'B2':
        etat_table = 'Etat_b2'
    elif nature_upper in ('B3', 'R1', 'R2', 'R3', 'R4'):
        etat_table = 'Etat_b3'
    elif nature_upper == 'B4':
        etat_table = 'Etat_b4'
    
    if etat_table:
        try:
            cursor.execute(f"""
                SELECT TOP 1 nat_stock FROM {etat_table}
                WHERE numero_bon = %s AND cod_art = %s
            """, [num, cod_art])
            row = cursor.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
        except Exception as e:
            logger.warning(f"Erreur lecture {etat_table} pour num={num}: {e}")
    
    return None


def get_default_nat_stock(cursor, cod_art, val_art):
    """
    الحصول على nat_stock الافتراضي من جدول STOCK
    - إذا كان هناك سطر واحد: نستخدم nat_stock منه
    - إذا كان هناك أكثر من سطر: نستخدم '1' كقيمة افتراضية
    """
    try:
        cursor.execute("""
            SELECT NAT_STOCK FROM STOCK
            WHERE COD_ART = %s AND VAL_ART = %s
        """, [cod_art, val_art])
        rows = cursor.fetchall()
        if len(rows) == 1 and rows[0][0]:
            return str(rows[0][0]).strip()
        else:
            return '1'
    except Exception as e:
        logger.warning(f"Erreur get_default_nat_stock: {e}")
        return '1'


def insert_stock_evolution(cod_art, val_art, nat_stock, date_b, stock_value, 
                           movement_type, movement_qty, nature_bon, class_cout):
    """إدراج سطر في جدول stock_evolution باستخدام Django ORM"""
    from core.models import StockEvolution
    
    date_obj = None
    if isinstance(date_b, str):
        try:
            date_obj = datetime.strptime(date_b, '%Y-%m-%d').date()
        except:
            date_obj = date.today()
    elif hasattr(date_b, 'date'):
        date_obj = date_b.date()
    elif hasattr(date_b, 'isoformat'):
        date_obj = date_b
    else:
        date_obj = date.today()
    
    try:
        StockEvolution.objects.create(
            cod_art=str(cod_art),
            val_art=str(val_art),
            nat_stock=str(nat_stock),
            date_b=date_obj,
            stock_value=Decimal(str(round(float(stock_value), 2))),
            movement_type=str(movement_type) if movement_type else None,
            movement_qty=Decimal(str(round(float(movement_qty), 2))),
            nature_bon=str(nature_bon) if nature_bon else None,
            class_cout=str(class_cout) if class_cout else None
        )
    except InvalidOperation:
        logger.warning(f"InvalidOperation pour {cod_art}: stock_value={stock_value}")
    except Exception as e:
        logger.error(f"Erreur insertion stock_evolution pour {cod_art}: {e}")


# =============================================================================
# ✅ الدالة الرئيسية لمعالجة cod_art واحد
# =============================================================================

def process_cod_art(cursor, cod_art, nature_rules):
    """
    معالجة cod_art واحد وحفظ النتائج في stock_evolution لكل (val_art, nat_stock)
    """
    cod_art = str(cod_art).strip()
    
    # 1. جلب جميع (val_art, nat_stock) لهذا cod_art من STOCK
    val_nat_pairs = []
    try:
        cursor.execute("""
            SELECT VAL_ART, NAT_STOCK, ISNULL(SUM(QTE_SURSTK), 0) as stock_total
            FROM STOCK
            WHERE COD_ART = %s
            GROUP BY VAL_ART, NAT_STOCK
            ORDER BY VAL_ART, NAT_STOCK
        """, [cod_art])
        for row in cursor.fetchall():
            val_art = str(row[0]).strip() if row[0] else '1'
            nat_stock = str(row[1]).strip() if row[1] else '1'
            stock_actuel = float(row[2]) if row[2] else 0.0
            val_nat_pairs.append({
                'val_art': val_art,
                'nat_stock': nat_stock,
                'stock_actuel': stock_actuel
            })
    except Exception as e:
        logger.error(f"Erreur lecture STOCK pour {cod_art}: {e}")
        return
    
    if not val_nat_pairs:
        return
    
    # 2. جلب جميع الحركات من fiche_ebc (مرتبة من الأحدث للأقدم)
    all_movements = []
    try:
        cursor.execute("""
            SELECT
                f.date_b,
                f.qte_mvt,
                f.nature_bon,
                f.class_cout,
                f.num
            FROM fiche_ebc f
            WHERE f.cod_art = %s
              AND f.class_cout IS NOT NULL
              AND LTRIM(RTRIM(f.class_cout)) <> ''
            ORDER BY f.date_b DESC
        """, [cod_art])
        
        for row in cursor.fetchall():
            date_b, qte_mvt, nature_bon, class_cout, num = row
            all_movements.append({
                'date_b': date_b,
                'qte_mvt': float(qte_mvt or 0),
                'nature_bon': str(nature_bon or '').strip().upper(),
                'class_cout': str(class_cout or '').strip().upper(),
                'num': str(num or '').strip()
            })
    except Exception as e:
        logger.error(f"Erreur chargement mouvements pour {cod_art}: {e}")
        return
    
    # 3. لكل (val_art, nat_stock)، نطبق الخوارزمية العكسية
    for pair in val_nat_pairs:
        val_art = pair['val_art']
        nat_stock = pair['nat_stock']
        stock_actuel = pair['stock_actuel']
        
        stock = stock_actuel
        today_str = date.today().isoformat()
        
        # ✅ حفظ السطر الأول (INITIAL)
        insert_stock_evolution(
            cod_art, val_art, nat_stock, today_str,
            stock, 'INITIAL', 0, None, None
        )
        
        # ✅ المرور على الحركات من الأحدث للأقدم
        for mv in all_movements:
            date_b = mv['date_b']
            date_str = date_b.isoformat() if hasattr(date_b, 'isoformat') else str(date_b)
            nature_bon = mv['nature_bon']
            class_cout = mv['class_cout']
            num = mv['num']
            qte_mvt = mv['qte_mvt']
            
            # ✅ تحديد nat_stock الفعلي لهذه الحركة
            movement_nat_stock = nat_stock  # الافتراضي
            
            if nature_bon == 'INV' or not nature_bon:
                # للجرد أو الحركات الفارغة: من جدول STOCK
                movement_nat_stock = get_default_nat_stock(cursor, cod_art, val_art)
            else:
                # للحركات الأخرى: من جدول etat المناسب
                etat_nat = get_nat_stock_from_etat(cursor, nature_bon, num, cod_art)
                if etat_nat:
                    movement_nat_stock = etat_nat
            
            # ✅ تطبيق الخوارزمية العكسية
            is_inv = (class_cout == 'INV' or nature_bon == 'INV')
            
            if is_inv:
                stock = qte_mvt
                movement_type = 'INV'
            else:
                sign = nature_rules.get(nature_bon, 0)
                stock -= (qte_mvt * sign)
                movement_type = nature_bon
            
            # ✅ حفظ في stock_evolution
            insert_stock_evolution(
                cod_art, val_art, movement_nat_stock, date_str,
                round(stock, 2), movement_type, qte_mvt, nature_bon, class_cout
            )


# =============================================================================
# ✅ الدالة الرئيسية
# =============================================================================

def main():
    """الدالة الرئيسية"""
    logger.info("=" * 70)
    logger.info("بدء ملء جدول stock_evolution")
    logger.info(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # جلب قواعد sign
    nature_rules = get_nature_rules()
    logger.info(f"تم جلب {len(nature_rules)} قاعدة من naturebon")
    
    # مسح البيانات القديمة
    try:
        from core.models import StockEvolution
        count = StockEvolution.objects.count()
        if count > 0:
            logger.info(f"مسح {count} سطر قديم من stock_evolution")
            # مسح على دفعات لتجنب مشاكل الذاكرة
            batch_size = 10000
            while StockEvolution.objects.exists():
                ids = list(StockEvolution.objects.values_list('id', flat=True)[:batch_size])
                StockEvolution.objects.filter(id__in=ids).delete()
                logger.info(f"  تم مسح {len(ids)} سطر...")
    except Exception as e:
        logger.warning(f"Erreur suppression anciennes données: {e}")
    
    # جلب جميع cod_art الفريدة من جدول STOCK
    articles = []
    try:
        with connections['sql_server'].cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT COD_ART
                FROM STOCK
                ORDER BY COD_ART
            """)
            articles = [str(row[0]).strip() for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Erreur lecture STOCK: {e}")
        return
    
    logger.info(f"تم العثور على {len(articles)} مقال فريد في جدول STOCK")
    
    # معالجة كل مقال
    start_time = datetime.now()
    errors_count = 0
    success_count = 0
    
    with connections['sql_server'].cursor() as cursor:
        for idx, cod_art in enumerate(articles, 1):
            logger.info(f"[{idx}/{len(articles)}] معالجة المقال: {cod_art}")
            
            try:
                process_cod_art(cursor, cod_art, nature_rules)
                success_count += 1
                
                # commit كل 10 مقالات
                if idx % 10 == 0:
                    from django.db import connection
                    connection.close()
                    logger.info(f"  ✓ تم معالجة {idx} مقال بنجاح")
                    
            except Exception as e:
                errors_count += 1
                logger.error(f"  ✗Erreur traitement {cod_art}: {e}", exc_info=True)
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    # إحصائيات نهائية
    try:
        from core.models import StockEvolution
        total_rows = StockEvolution.objects.count()
        logger.info("=" * 70)
        logger.info(f"انتهى ملء جدول stock_evolution")
        logger.info(f"المقالات المعالجة بنجاح: {success_count}")
        logger.info(f"المقالات التي فشلت: {errors_count}")
        logger.info(f"إجمالي الأسطر في stock_evolution: {total_rows}")
        logger.info(f"المدة الزمنية: {duration}")
        logger.info("=" * 70)
    except Exception as e:
        logger.error(f"Erreur statistiques finales: {e}")


if __name__ == '__main__':
    main()
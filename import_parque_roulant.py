# import_parque_roulant.py
import os
import sys
import django
from datetime import datetime

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'petro_dashboard.settings')
django.setup()

from core.models import Engin, Service
import openpyxl

def parse_date(date_value):
    """
    تحويل تاريخ من Excel (قد يكون نصًا أو رقمًا) إلى كائن datetime.date.
    """
    if not date_value or date_value == "SANS VISITE" or date_value == "NOUVELLE":
        return None
    if isinstance(date_value, datetime):
        return date_value.date()
    if isinstance(date_value, str):
        try:
            # تنسيقات متوقعة: "12/2/05", "29/3/22"
            return datetime.strptime(date_value, "%m/%d/%y").date()
        except ValueError:
            try:
                return datetime.strptime(date_value, "%d/%m/%y").date()
            except ValueError:
                return None
    return None

def get_or_create_service(service_name):
    """
    إنشاء خدمة جديدة أو إرجاع موجودة.
    """
    if not service_name or service_name.strip() == "":
        return None
    service, created = Service.objects.get_or_create(
        nom=service_name.strip(),
        defaults={'description': f"Service créé depuis le fichier Excel: {service_name}"}
    )
    return service

def import_engins_from_excel(file_path):
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active  # افتراض أن البيانات في الورقة الأولى

    # تخطي الصف الأول (العناوين)
    rows = list(sheet.iter_rows(min_row=2, values_only=True))

    imported_count = 0
    for row in rows:
        if not row[2]:  # تخطي الصفوف بدون رقم ترقيم (Immatriculation)
            continue

        try:
            # استخراج القيم من الأعمدة
            numero_bp = str(row[1]) if row[1] else ""
            immatriculation = str(row[2]) if row[2] else ""
            marque = str(row[3]) if row[3] else ""
            type_engin_excel = str(row[4]) if row[4] else ""
            genre = str(row[5]) if row[5] else ""
            numero_serie = str(row[6]) if row[6] else ""
            date_1ere = parse_date(row[7])
            date_derniere_visite = parse_date(row[8])
            puissance_fiscale = str(row[9]) if row[9] else ""
            service_name = str(row[10]) if row[10] else ""
            situation_excel = str(row[11]).lower() if row[11] else "en_service"
            observations = str(row[12]) if row[12] else ""

            # تحديد الحالة (situation)
            SITUATION_MAP = {
                'en service': 'en_service',
                'en panne': 'en_panne',
                'hors service': 'hors_service',
                'vendu': 'vendu',
            }
            situation = SITUATION_MAP.get(situation_excel, 'en_service')

            # تحديد نوع المحرك (type_engin)
            TYPE_ENGIN_MAP = {
                'voiture': ['voiture'],
                'camion': ['camion', 'truck', 'transport'],
                'tractopelle': ['tractopelle', 'pelle'],
                'grue': ['grue', 'grue'],
                'autre': [],
            }
            type_engin = 'autre'
            for key, keywords in TYPE_ENGIN_MAP.items():
                if any(kw in type_engin_excel.lower() for kw in keywords):
                    type_engin = key
                    break

            # ربط الخدمة
            service = get_or_create_service(service_name)

            # إنشاء أو تحديث Engin
            engin, created = Engin.objects.update_or_create(
                immatriculation=immatriculation,
                defaults={
                    'libelle': f"{marque} {type_engin_excel}",
                    'type_engin': type_engin,
                    'numero_serie': numero_serie,
                    'numero_bp': numero_bp,
                    'marque': marque,
                    'genre': genre,
                    'date_1ere_mise_en_circulation': date_1ere,
                    'date_derniere_visite': date_derniere_visite,
                    'puissance_fiscale': puissance_fiscale,
                    'service': service,
                    'situation': situation,
                    'observations': observations,
                    'actif': True,
                    'type_carburant': 'gasoil',  # افتراضيًا من الملف
                }
            )
            imported_count += 1
            status = " créé" if created else " mis à jour"
            print(f"✅ Engin {immatriculation} {status}.")

        except Exception as e:
            print(f"❌ خطأ في معالجة الصف {row}: {e}")

    print(f"\n✅ تم استيراد/تحديث {imported_count} engin(s) بنجاح.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("الاستخدام: python import_parque_roulant.py <مسار_الملف.xlsx>")
        sys.exit(1)

    excel_file = sys.argv[1]
    if not os.path.exists(excel_file):
        print(f"❌ الملف غير موجود: {excel_file}")
        sys.exit(1)

    import_engins_from_excel(excel_file)
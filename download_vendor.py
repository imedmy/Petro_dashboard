# download_vendor.py
import os
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VENDOR_DIR = BASE_DIR / 'static' / 'vendor'

LIBRARIES = {
    # Bootstrap 5.3.3
    'bootstrap/css/bootstrap.min.css': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
    'bootstrap/css/bootstrap.min.css.map': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css.map',
    'bootstrap/js/bootstrap.bundle.min.js': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js',
    'bootstrap/js/bootstrap.bundle.min.js.map': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js.map',
    
    # Bootstrap Icons
    'bootstrap-icons/font/bootstrap-icons.min.css': 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css',
    'bootstrap-icons/font/fonts/bootstrap-icons.woff': 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/fonts/bootstrap-icons.woff',
    'bootstrap-icons/font/fonts/bootstrap-icons.woff2': 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/fonts/bootstrap-icons.woff2',
    
    # Chart.js 4.4.1 (أحدث إصدار)
    'chart.js/chart.umd.min.js': 'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js',
    
    # SheetJS (xlsx)
    'xlsx/xlsx.full.min.js': 'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js',
    
    # ✅ Alpine.js 3.13.5 - بديل خفيف لـ jQuery (حديث جداً)
    'alpinejs/alpine.min.js': 'https://cdn.jsdelivr.net/npm/alpinejs@3.13.5/dist/cdn.min.js',
    
    # ✅ HTMX 1.9.10 - لتحديث الصفحات بدون إعادة تحميل (مثل SPA)
    'htmx/htmx.min.js': 'https://cdn.jsdelivr.net/npm/htmx.org@1.9.10/dist/htmx.min.js',
    
    # ✅ LocalForage - لتخزين البيانات محلياً (Offline Storage)
    'localforage/localforage.min.js': 'https://cdn.jsdelivr.net/npm/localforage@1.10.0/dist/localforage.min.js',
    
    # DataTables (لجداول متقدمة)
    'datatables/css/dataTables.dataTables.min.css': 'https://cdn.jsdelivr.net/npm/datatables.net-dt@1.13.8/css/jquery.dataTables.min.css',
    'datatables/js/dataTables.min.js': 'https://cdn.jsdelivr.net/npm/datatables.net@2.1.8/js/dataTables.min.js',
}

def download_libraries():
    for local_path, url in LIBRARIES.items():
        filepath = VENDOR_DIR / local_path
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        if filepath.exists():
            print(f'✅ موجود مسبقًا: {local_path}')
            continue
        
        try:
            print(f'⬇️ جاري التحميل: {local_path}')
            urllib.request.urlretrieve(url, filepath)
            print(f'✅ تم: {local_path}')
        except Exception as e:
            print(f'❌ فشل في {local_path}: {e}')

if __name__ == '__main__':
    download_libraries()
    print('\n🎉 اكتمل تحميل المكتبات!')
    print('الآن حدّث base.html لاستخدام المسارات المحلية.')
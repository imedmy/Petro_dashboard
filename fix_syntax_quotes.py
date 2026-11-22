#!/usr/bin/env python3
"""
Fix common syntax errors in Django project files caused by French apostrophes in single quotes.
Only processes source code files, ignores vendor libraries and static assets.
"""

import os
import re
import shutil
from pathlib import Path

# =============================
# ⚙️ الإعدادات
# =============================

PROJECT_ROOT = Path("D:/petro_dashboard")  # عدّل المسار إذا لزم
BACKUP_DIR = PROJECT_ROOT / "fix_quotes_backup"
FILES_TO_SCAN = ("*.html", "*.js", "*.py")
IGNORE_DIRS = {
    'static/vendor', 'staticfiles', '__pycache__', '.git', 'node_modules',
    'venv', 'env', '.pytest_cache', '.vscode', '.idea'
}

# النمط لاكتشاف النصوص بين '...' التي تحتوي على فاصلة عليا مثل l' أو d' أو n' أو t' أو s' أو qu'
# لكنها لا تبدأ بـ \' (التي هي بالفعل مهربة)
PATTERN = re.compile(
    r"('[^'\\]*(?:l|d|n|t|s|qu)'[^']*)'"
)

def should_process_file(file_path):
    """تحقق مما إذا كان يجب معالجة الملف بناءً على الموقع والامتداد."""
    rel_path = file_path.relative_to(PROJECT_ROOT).as_posix()
    if any(ignored in rel_path for ignored in IGNORE_DIRS):
        return False
    return True

def fix_line(line):
    """صلح السطر الواحد إذا كان يحتوي على مشكلة."""
    # إذا كان السطر يحتوي على 'text' مع فاصلة داخلية غير مهربة
    if PATTERN.search(line):
        # استخدم "..." بدلاً من '...' لتلك النصوص
        fixed = PATTERN.sub(r'"\1"', line)
        return fixed
    return line

def process_file(file_path):
    """عالج ملف واحد وقم بتحديثه مع النسخ الاحتياطي."""
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.splitlines()
        fixed_lines = []
        modified = False

        for line in lines:
            fixed_line = fix_line(line)
            if fixed_line != line:
                modified = True
            fixed_lines.append(fixed_line)

        if modified:
            backup_path = BACKUP_DIR / file_path.relative_to(PROJECT_ROOT)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            print(f"✅ [تم التعديل] {file_path}")
            print(f"   ↳ نسخة احتياطية: {backup_path}")

            # أعد الكتابة بتنسيق جديد
            new_content = '\n'.join(fixed_lines) + '\n'
            file_path.write_text(new_content, encoding='utf-8')

    except Exception as e:
        print(f"❌ خطأ في معالجة {file_path}: {e}")

def main():
    print("🔍 بدء فحص المشروع لإصلاح مشاكل الفاصلة العليا...")
    print(f"جذر المشروع: {PROJECT_ROOT}")
    print("-" * 60)

    # إنشاء مجلد النسخ الاحتياطي
    BACKUP_DIR.mkdir(exist_ok=True)

    processed_files = 0
    for pattern in FILES_TO_SCAN:
        for file_path in PROJECT_ROOT.rglob(pattern):
            if file_path.is_file() and should_process_file(file_path):
                process_file(file_path)
                processed_files += 1

    print("-" * 60)
    print(f"✅ اكتمل الفحص. عدد الملفات المعالجة: {processed_files}")
    print(f"📁 النسخ الاحتياطية موجودة في: {BACKUP_DIR}")

if __name__ == "__main__":
    main()
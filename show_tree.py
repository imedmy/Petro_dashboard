import os
from pathlib import Path

# قائمة بالمجلدات والملفات التي نريد تجاهلها (لتوضيح الهيكل)
IGNORE_DIRS = {'.git', '__pycache__', 'venv', 'env', '.venv', 'node_modules', '.idea', '.vscode'}
IGNORE_FILES = {'.pyc', '.pyo', '.so', '.dll'}

def print_tree(dir_path, prefix=''):
    """
    دالة عودية لطباعة هيكل المجلدات
    """
    try:
        path_obj = Path(dir_path)
        # جلب المحتويات
        contents = list(path_obj.iterdir())
        
        # تصفية العناصر المستبعدة
        contents = [
            p for p in contents 
            if not (p.name in IGNORE_DIRS or p.suffix in IGNORE_FILES or p.name.startswith('.'))
        ]
        
        # ترتيب العناصر (المجلدات أولاً ثم الملفات)
        contents.sort(key=lambda p: (not p.is_dir(), p.name.lower()))

        pointers = ['├── '] * (len(contents) - 1) + ['└── '] if contents else []

        for pointer, path in zip(pointers, contents):
            print(prefix + pointer + path.name)

            if path.is_dir():
                extension = '│   ' if pointer == '├── ' else '    '
                print_tree(path, prefix=prefix + extension)
                
    except PermissionError:
        print(prefix + "⚠️ لا يوجد صلاحيات للوصول")
    except Exception as e:
        print(prefix + f"⚠️ خطأ: {e}")

if __name__ == "__main__":
    # استخدام المجلد الحالي مباشرة
    target_dir = '.'
    current_path = os.path.abspath(target_dir)
    
    print(f"📂 هيكلية المشروع للمجلد الحالي:\n{current_path}\n")
    print("📁 " + os.path.basename(current_path))
    print_tree(target_dir)
"""
خدمة الذكاء الاصطناعي للتحليل الذكي للمقالات
تستخدم Google Gemini 1.5 Flash (مجاني حتى 60 طلب/دقيقة)
"""

import logging
import os
import json
import re
from typing import Dict, List, Optional, Any
from django.conf import settings

logger = logging.getLogger(__name__)

# مفتاح API من متغيرات البيئة
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')


def get_ai_advice(
    article_data: Dict[str, Any],
    caracteristiques: List[Dict[str, Any]],
    family_data: Optional[Dict[str, Any]] = None,
    language: str = 'fr'
) -> Dict[str, Any]:
    """
    الحصول على نصائح ذكية من الذكاء الاصطناعي
    
    Args:
        article_data: dict - بيانات المقال (cod_art, lib_art, class_cout...)
        caracteristiques: list - قائمة الخصائص التقنية
        family_data: dict - معلومات العائلة (اختياري)
        language: str - 'fr' للفرنسية أو 'ar' للعربية
    
    Returns:
        dict - يحتوي على:
            - usage_tips_fr: list[str] - نصائح الاستخدام بالفرنسية
            - usage_tips_ar: list[str] - نصائح الاستخدام بالعربية
            - recommended_accessories: list[dict] - الإكسسوارات الموصى بها
            - safety_notes: list[str] - ملاحظات السلامة
    """
    
    # إذا لم يكن مفتاح API موجودًا، نستخدم ردود افتراضية
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY non configuré. Utilisation de réponses par défaut.")
        return get_default_advice(article_data, caracteristiques, language)
    
    try:
        # استيراد مكتبة Google Gemini
        import google.generativeai as genai
        
        # تهيئة النموذج
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # بناء الـ Prompt
        prompt = build_ai_prompt(article_data, caracteristiques, family_data, language)
        
        # إرسال الطلب مع إعدادات الأمان
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.2,  # تقليل الإبداع لنتائج أكثر دقة
                'max_output_tokens': 1024,
            }
        )
        
        # تحليل الرد
        return parse_ai_response(response.text, language)
    
    except ImportError:
        logger.error("google-generativeai library not installed. Run: pip install google-generativeai")
        return get_default_advice(article_data, caracteristiques, language)
    
    except Exception as e:
        logger.error(f"Erreur API Gemini: {type(e).__name__} - {str(e)}")
        return get_default_advice(article_data, caracteristiques, language)


def build_ai_prompt(
    article_data: Dict[str, Any],
    caracteristiques: List[Dict[str, Any]],
    family_data: Optional[Dict[str, Any]],
    language: str
) -> str:
    """
    بناء Prompt مخصص للذكاء الاصطناعي
    
    Args:
        article_data: بيانات المقال
        caracteristiques: قائمة الخصائص
        family_data: معلومات العائلة
        language: لغة الرد المطلوبة
    
    Returns:
        str: الـ Prompt النهائي
    """
    
    lang_name = 'Français' if language == 'fr' else 'Arabe'
    
    # تنظيف البيانات من الأحرف الخاصة لتجنب مشاكل الـ Prompt
    def safe_str(value: Any) -> str:
        if value is None:
            return 'N/A'
        return str(value).replace('{', '(').replace('}', ')').replace('"', "'")
    
    # تنسيق الخصائص التقنية
    carac_text = format_caracteristiques(caracteristiques)
    
    # تنسيق معلومات العائلة
    family_text = ""
    if family_data:
        family_text = f"Nom: {safe_str(family_data.get('name'))} (Code: {safe_str(family_data.get('full_code'))})"
    else:
        family_text = "Non définie"
    
    prompt = f"""
Tu es un expert en gestion de stock industriel pour une société pétrolière (SITEP - Tunisie).

Analyse l'article suivant et fournis des conseils d'utilisation pratiques:

**Informations de l'article:**
- Code: {safe_str(article_data.get('cod_art'))}
- Libellé: {safe_str(article_data.get('lib_art'))}
- Désignation: {safe_str(article_data.get('designat'))}
- Classe de coût: {safe_str(article_data.get('class_cout'))}
- Emplacement: {safe_str(article_data.get('empl'))}

**Caractéristiques techniques:**
{carac_text}

**Famille:**
{family_text}

**Tâche:**
Réponds en {lang_name} avec:
1. 3-5 conseils d'utilisation pratiques et spécifiques au contexte pétrolier
2. 2-3 accessoires/pièces recommandés à utiliser avec cet article
3. 2-3 notes de sécurité importantes liées à l'environnement industriel

Format de réponse (JSON strict, sans texte supplémentaire):
{{
    "usage_tips": ["conseil 1", "conseil 2", "conseil 3"],
    "recommended_accessories": [
        {{"nom": "accessoire 1", "reason": "raison d'utilisation", "priority": "high|medium|low"}},
        {{"nom": "accessoire 2", "reason": "raison d'utilisation", "priority": "medium"}}
    ],
    "safety_notes": ["note 1", "note 2", "note 3"]
}}

Réponds UNIQUEMENT avec le JSON valide, sans texte avant ou après, sans markdown.
"""
    
    return prompt


def format_caracteristiques(caracteristiques: List[Dict[str, Any]]) -> str:
    """
    تنسيق الخصائص التقنية للـ Prompt
    
    Args:
        caracteristiques: قائمة القواميس تحتوي على nom, valeur, unite
    
    Returns:
        str: نص منسق للخصائص
    """
    if not caracteristiques:
        return "Aucune caractéristique technique définie"
    
    lines = []
    for c in caracteristiques:
        nom = c.get('nom', 'N/A')
        valeur = c.get('valeur', 'N/A')
        unite = c.get('unite', '')
        
        ligne = f"- {nom}: {valeur}"
        if unite:
            ligne += f" {unite}"
        lines.append(ligne)
    
    return "\n".join(lines)


def parse_ai_response(response_text: str, language: str) -> Dict[str, Any]:
    """
    تحليل رد الذكاء الاصطناعي واستخراج البيانات المفيدة
    
    Args:
        response_text: النص الخام من الـ AI
        language: اللغة المطلوبة للرد
    
    Returns:
        dict: البيانات المهيكلة الجاهزة للعرض
    """
    
    try:
        # تنظيف الرد من أي نصوص إضافية أو markdown
        cleaned_text = response_text.strip()
        
        # إزالة أي markdown code blocks إذا وجدت
        if cleaned_text.startswith('```'):
            # إزالة السطر الأول إذا كان ```json أو ```
            lines = cleaned_text.split('\n')
            if lines[0].startswith('```'):
                cleaned_text = '\n'.join(lines[1:])
            if cleaned_text.rstrip().endswith('```'):
                cleaned_text = cleaned_text.rstrip()[:-3].strip()
        
        # استخراج أول كائن JSON صالح من النص
        json_data = None
        
        # محاولة 1: البحث عن { ... }
        json_match = re.search(r'\{[\s\S]*\}', cleaned_text)
        if json_match:
            json_str = json_match.group()
            json_data = json.loads(json_str)
        
        # محاولة 2: إذا فشلت، محاولة تحليل النص كاملاً
        if json_data is None:
            json_data = json.loads(cleaned_text)
        
        # التحقق من وجود المفاتيح المطلوبة
        usage_tips = json_data.get('usage_tips', [])
        if not isinstance(usage_tips, list):
            usage_tips = []
        
        accessories = json_data.get('recommended_accessories', [])
        if not isinstance(accessories, list):
            accessories = []
        
        safety = json_data.get('safety_notes', [])
        if not isinstance(safety, list):
            safety = []
        
        # تنسيق الإكسسوارات مع القيم الافتراضية
        formatted_accessories = []
        for acc in accessories:
            if isinstance(acc, dict):
                formatted_accessories.append({
                    'nom': acc.get('nom', 'Accessoire'),
                    'reason': acc.get('reason', ''),
                    'priority': acc.get('priority', 'medium').lower() if acc.get('priority') in ['high', 'medium', 'low'] else 'medium'
                })
        
        # إعداد النتيجة حسب اللغة
        result = {
            'usage_tips_fr': usage_tips if language == 'fr' else [],
            'usage_tips_ar': usage_tips if language == 'ar' else [],
            'recommended_accessories': formatted_accessories,
            'safety_notes': safety
        }
        
        return result
    
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error: {str(e)}")
        logger.debug(f"Response text: {response_text[:200]}...")
        return get_empty_response()
    
    except Exception as e:
        logger.error(f"Erreur parsing AI response: {type(e).__name__} - {str(e)}")
        return get_empty_response()


def get_empty_response() -> Dict[str, Any]:
    """إرجاع هيكل فارغ عند فشل التحليل"""
    return {
        'usage_tips_fr': [],
        'usage_tips_ar': [],
        'recommended_accessories': [],
        'safety_notes': []
    }


def get_default_advice(
    article_data: Dict[str, Any],
    caracteristiques: List[Dict[str, Any]],
    language: str
) -> Dict[str, Any]:
    """
    ردود افتراضية عندما لا يتوفر الذكاء الاصطناعي
    
    تُستخدم كـ fallback لضمان استمرارية العمل
    """
    
    lib_art = article_data.get('lib_art', 'cet article')
    class_cout = article_data.get('class_cout', '')
    
    # نصائح عامة تناسب معظم المواد الصناعية
    usage_tips_fr = [
        f"Vérifier la compatibilité de {lib_art} avec l'équipement avant installation",
        "Consulter la fiche technique et les spécifications du fabricant",
        "Respecter les conditions de stockage (température, humidité, propreté)",
        "Contrôler régulièrement l'état et la date de péremption si applicable",
        "Former le personnel à l'utilisation correcte de ce matériel"
    ]
    
    usage_tips_ar = [
        f"التحقق من توافق {lib_art} مع المعدات قبل التركيب",
        "الرجوع إلى الورقة الفنية ومواصفات المصنع",
        "احترام ظروف التخزين الموصى بها (درجة الحرارة، الرطوبة، النظافة)",
        "مراقبة الحالة وتاريخ الصلاحية بانتظام إن وجد",
        "تأهيل الموظفين على الاستخدام الصحيح لهذه المادة"
    ]
    
    # إكسسوارات عامة موصى بها
    recommended_accessories = [
        {
            'nom': 'Équipements de protection individuelle (EPI)',
            'reason': 'Pour assurer la sécurité du personnel lors de la manipulation',
            'priority': 'high'
        },
        {
            'nom': 'Outils de contrôle et de mesure',
            'reason': 'Pour vérifier la conformité et l état de l article',
            'priority': 'medium'
        },
        {
            'nom': 'Documentation technique',
            'reason': 'Pour référence rapide aux procédures d utilisation',
            'priority': 'low'
        }
    ]
    
    # ملاحظات سلامة عامة
    safety_notes = [
        "Porter les équipements de protection individuelle (EPI) appropriés avant toute manipulation",
        "Suivre les procédures de sécurité et les consignes HSE en vigueur sur site",
        "Signaler immédiatement tout défaut, dommage ou anomalie constaté(e) sur l'article"
    ]
    
    return {
        'usage_tips_fr': usage_tips_fr,
        'usage_tips_ar': usage_tips_ar,
        'recommended_accessories': recommended_accessories,
        'safety_notes': safety_notes
    }


def is_api_available() -> bool:
    """
    التحقق من توفر خدمة الذكاء الاصطناعي
    
    Returns:
        bool: True إذا كان المفتاح موجودًا والمكتبة مثبتة
    """
    if not GEMINI_API_KEY:
        return False
    
    try:
        import google.generativeai as genai
        return True
    except ImportError:
        return False


def get_api_status() -> Dict[str, Any]:
    """
    الحصول على حالة خدمة الذكاء الاصطناعي
    
    Returns:
        dict: معلومات عن حالة الـ API
    """
    return {
        'available': is_api_available(),
        'api_key_configured': bool(GEMINI_API_KEY),
        'library_installed': _check_library_installed(),
        'model': 'gemini-1.5-flash' if is_api_available() else None
    }


def _check_library_installed() -> bool:
    """التحقق من تثبيت مكتبة google-generativeai"""
    try:
        import google.generativeai
        return True
    except ImportError:
        return False
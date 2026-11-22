document.addEventListener('DOMContentLoaded', function () {
    const button = document.getElementById('choose-feature-btn');
    const featureList = document.getElementById('feature-list');

    if (button && featureList) {
        button.addEventListener('click', function () {
            // يمكنك فتح نافذة منبثقة أو تحويل إلى صفحة أخرى
            alert("فتح نافذة اختيار الخاصية");
            // أو استخدم window.location:
            // window.location.href = "/features/select/";
        });
    } else {
        console.warn("زر أو قائمة الخواص غير موجودة في الصفحة.");
    }
}); 

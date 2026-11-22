# core/models_sql.py
from django.db import models

class ArticleSQL(models.Model):
    COD_ART = models.CharField(max_length=50, primary_key=True)
    LIB_ART = models.CharField(max_length=200, blank=True, null=True)
    CLASS_COUT = models.CharField(max_length=50, blank=True, null=True)
    EMPL = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False  # لأن الجدول موجود في قاعدة البيانات
        db_table = 'ARTICLE'  # اسم الجدول في قاعدة البيانات SQL Server
        app_label = 'core'

    def __str__(self):
        return f"{self.COD_ART} - {self.LIB_ART}"
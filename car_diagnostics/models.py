from django.db import models
from django.utils.translation import gettext_lazy as _

class CarBrand(models.Model):
    """نموذج يمثل الشركات المصنعة للسيارات"""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("اسم الشركة"))
    logo = models.ImageField(upload_to='brands/', blank=True, null=True, verbose_name=_("شعار الشركة"))
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("شركة مصنعة")
        verbose_name_plural = _("الشركات المصنعة")

class Car(models.Model):
    """نموذج يمثل موديلات السيارات"""
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, related_name='models', verbose_name=_("الشركة المصنعة"))
    model = models.CharField(max_length=100, verbose_name=_("الموديل"))
    year = models.IntegerField(verbose_name=_("سنة الصنع"))
    engine_type = models.CharField(max_length=100, verbose_name=_("نوع المحرك"))
    common_issues = models.TextField(blank=True, null=True, verbose_name=_("الأعطال الشائعة"))
    image = models.ImageField(upload_to='cars/', blank=True, null=True, verbose_name=_("صورة السيارة"))
    
    def __str__(self):
        return f"{self.brand} {self.model} {self.year}"
    
    class Meta:
        verbose_name = _("سيارة")
        verbose_name_plural = _("السيارات")
        unique_together = ('brand', 'model', 'year', 'engine_type')

class ErrorCodeCategory(models.Model):
    """نموذج يمثل فئات أكواد الأعطال"""
    CATEGORY_CHOICES = [
        ('ENGINE', _('المحرك')),
        ('TRANSMISSION', _('ناقل الحركة')),
        ('FUEL', _('نظام الوقود')),
        ('IGNITION', _('نظام الإشعال')),
        ('EMISSION', _('نظام العادم')),
        ('ELECTRICAL', _('النظام الكهربائي')),
        ('ABS', _('نظام المكابح')),
        ('HVAC', _('نظام التكييف')),
        ('OTHER', _('أخرى')),
    ]
    
    code_prefix = models.CharField(max_length=10, unique=True, verbose_name=_("بادئة الكود"))
    name = models.CharField(max_length=100, verbose_name=_("اسم الفئة"))
    category_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name=_("نوع الفئة"))
    description = models.TextField(verbose_name=_("وصف الفئة"))
    
    def __str__(self):
        return f"{self.code_prefix} - {self.name}"
    
    class Meta:
        verbose_name = _("فئة أكواد الأعطال")
        verbose_name_plural = _("فئات أكواد الأعطال")

class ErrorCode(models.Model):
    """نموذج يمثل أكواد الأعطال"""
    SEVERITY_CHOICES = [
        ('LOW', _('منخفضة')),
        ('MEDIUM', _('متوسطة')),
        ('HIGH', _('عالية')),
        ('CRITICAL', _('حرجة')),
    ]
    
    obd_code = models.CharField(max_length=10, unique=True, verbose_name=_("كود العطل"))
    category = models.ForeignKey(ErrorCodeCategory, on_delete=models.CASCADE, related_name='error_codes', verbose_name=_("فئة الكود"))
    description = models.TextField(verbose_name=_("وصف العطل"))
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, verbose_name=_("خطورة العطل"))
    emergency_action = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("إجراء الطوارئ"))
    repair_difficulty = models.CharField(max_length=10, choices=[
        ('EASY', _('سهل')),
        ('MEDIUM', _('متوسط')),
        ('HARD', _('صعب')),
    ], verbose_name=_("صعوبة الإصلاح"))
    
    def __str__(self):
        return f"{self.obd_code} - {self.description[:30]}"
    
    class Meta:
        verbose_name = _("كود عطل")
        verbose_name_plural = _("أكواد الأعطال")

class CarError(models.Model):
    """نموذج يمثل العلاقة بين السيارة وكود العطل"""
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='car_errors', verbose_name=_("السيارة"))
    error_code = models.ForeignKey(ErrorCode, on_delete=models.CASCADE, related_name='car_errors', verbose_name=_("كود العطل"))
    common_causes = models.TextField(verbose_name=_("الأسباب الشائعة"))
    solutions = models.TextField(blank=True, null=True, verbose_name=_("الحلول المقترحة"))
    repair_steps = models.TextField(blank=True, null=True, verbose_name=_("خطوات الإصلاح"))
    estimated_cost = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("التكلفة التقديرية"))
    
    def __str__(self):
        return f"{self.car} - {self.error_code}"
    
    class Meta:
        verbose_name = _("عطل السيارة")
        verbose_name_plural = _("أعطال السيارات")
        unique_together = ('car', 'error_code')

class RepairResource(models.Model):
    """نموذج يمثل موارد الإصلاح (فيديوهات، مقالات، إلخ)"""
    car_error = models.ForeignKey(CarError, on_delete=models.CASCADE, related_name='resources', verbose_name=_("عطل السيارة"))
    title = models.CharField(max_length=255, verbose_name=_("العنوان"))
    resource_type = models.CharField(max_length=20, choices=[
        ('VIDEO', _('فيديو')),
        ('ARTICLE', _('مقالة')),
        ('MANUAL', _('دليل')),
        ('TOOL', _('أداة')),
    ], verbose_name=_("نوع المورد"))
    url = models.URLField(verbose_name=_("الرابط"))
    
    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"
    
    class Meta:
        verbose_name = _("مورد إصلاح")
        verbose_name_plural = _("موارد الإصلاح")
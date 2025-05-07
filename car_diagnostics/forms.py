from django import forms
from .models import CarBrand, Car, ErrorCode

class CarSearchForm(forms.Form):
    brand = forms.ModelChoiceField(
        queryset=CarBrand.objects.all(),
        required=False,
        label='الشركة المصنعة',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    model = forms.CharField(
        max_length=100,
        required=False,
        label='الموديل',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    year = forms.IntegerField(
        required=False,
        label='سنة الصنع',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class ErrorSearchForm(forms.Form):
    obd_code = forms.CharField(
        max_length=10,
        required=False,
        label='كود العطل (مثال: P0300)',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    category = forms.ModelChoiceField(
        queryset=ErrorCodeCategory.objects.all(),
        required=False,
        label='فئة العطل',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    severity = forms.ChoiceField(
        choices=[('', '-- اختر --')] + ErrorCode.SEVERITY_CHOICES,
        required=False,
        label='خطورة العطل',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class SmartDiagnosticForm(forms.Form):
    brand = forms.ModelChoiceField(
        queryset=CarBrand.objects.all(),
        required=True,
        label='الشركة المصنعة',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    model = forms.CharField(
        max_length=100,
        required=True,
        label='الموديل',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    year = forms.IntegerField(
        required=True,
        label='سنة الصنع',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    problem_description = forms.CharField(
        required=True,
        label='وصف المشكلة',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )
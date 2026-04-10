from django import forms
from .models import Student, StudentBulkUpload


class StudentBulkUploadForm(forms.ModelForm):
    class Meta:
        model = StudentBulkUpload
        fields = ['csv_file']

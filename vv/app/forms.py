from django import forms
#from app.models import UserProfileInfo
from django.contrib.auth.models import User
from django.contrib.auth.forms import (UserCreationForm)

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta():
        model = User
        fields = ['username', 'email', 'password']



# class UserRegistrationForm(UserCreationForm):
#     username = forms.CharField(widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "text",
#         "placeholder": "enter username"
#     }))
#
#     email = forms.CharField(widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "email",
#         "placeholder": "enter email-id"
#     }))
#
#     password1 = forms.CharField(widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "password",
#         "placeholder": "enter password"
#     }))
#
#     password2 = forms.CharField(widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "password",
#         "placeholder": "re-enter password"
#     }))
#
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', "password2"]








from django import forms
from app.models import ExcelFile
class ExcelFileForm(forms.ModelForm):
    class Meta:
        model = ExcelFile
        fields = ('file','name','date')

from django import forms
class MyForm(forms.Form):
    pk = forms.IntegerField(label='Primary Key')

# from django import forms
# class ExcelDataForm(forms.Form):
#     enrolment_number = forms.IntegerField()

from django import forms
class ExcelDataForm(forms.Form):
    date=forms.DateField(label='Exam Date',)
    enrolment_number = forms.IntegerField(label='Enrolment Number')

from django import forms

class EnrollmentForm(forms.Form):
    enrolment_number = forms.IntegerField(label='Enrollment Number')

from django import forms
class StudentNameForm(forms.Form):
    student_name = forms.CharField(label='Student Name', max_length=100)
    date = forms.DateField(label='Date')


from django import forms

class AnalysisForm(forms.Form):
    enrolment_number = forms.IntegerField(label='Enrollment Number')

from .models import Choice, Examination, Question, Students, SchoolFees, Program, StudentResponse
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

class StudentsForm(forms.ModelForm):
    class Meta:
        model = Students
        fields = '__all__'

class SchoolFeesForm(forms.ModelForm):
    class Meta:
        model = SchoolFees
        fields = '__all__'

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = '__all__'
        
class StudentResponseForm(forms.ModelForm):
    class Meta:
        model = StudentResponse
        fields = ["selected_choice"]
    def __init__(self, *args, question=None, **kwargs):
        super().__init__(*args, **kwargs)
        if question:
            self.fields["selected_choice"].queryset = question.choices.all()
            self.fields["selected_choice"].label = question.text

class StudentregistrationForm(forms.Form):
    Username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    program = forms.ModelChoiceField(queryset=Program.objects.all())

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match.")
        if User.objects.filter(username=cleaned_data.get("Username")).exists():
            raise forms.ValidationError("Username already exists.")   
        return cleaned_data
    
class StudentLoginForm(AuthenticationForm):
    pass
class ExamForm(forms.ModelForm):
    class Meta:
        model = Examination
        fields = ["title", "description", "duration_minutes", "total_marks", "is_active"] 
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text", "marks", "order"]
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ["text", "is_correct"]
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            }   


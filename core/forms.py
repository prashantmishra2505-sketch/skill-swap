from django import forms
from .models import UserSkill, Skill ,Profile
from django.contrib.auth.models import User

class UserSkillForm(forms.ModelForm):
    class Meta:
        model = UserSkill
        fields = ['skill', 'role']
        widgets = {
            'skill': forms.Select(attrs={'class': 'form-input'}),
            'role': forms.Select(attrs={'class': 'form-input'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['location', 'bio', 'image'] # All three fields are here!
        
        # This tells Django how to style the auto-generated HTML boxes
        widgets = {
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. New York, USA'}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Tell us about yourself...'}),
            # Optional: You can also style the image upload button!
            'image': forms.FileInput(attrs={'class': 'form-input'}), 
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']



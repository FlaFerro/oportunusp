from django import forms
from django.contrib.auth.models import User
from .models import Profile, Comment, Opportunity



class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    description = forms.CharField(
        widget=forms.Textarea, 
        required=False, 
        label="Descrição do perfil"
    )
    profile_pic = forms.ImageField(required=False, label="Foto de perfil")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6:
            raise forms.ValidationError("A senha deve ter pelo menos 6 caracteres.")
        return password

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        
class PostForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = [
            'title',
            'description',
            'category',
            'is_active',
        ]
        labels = {
            'title' : 'Título', 
            'description':'Descição da oportunidade', 
            'category':'Categoria' ,
            'is_active':'Vísivel ao público?',
        }
        
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['description','profile_pic']
        labels = {'description':'Descrição','profile_pic':'Foto de perfil'} 
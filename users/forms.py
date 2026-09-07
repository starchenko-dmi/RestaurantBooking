from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User

UserModel = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации пользователя"""

    email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Телефон (необязательно)"}),
    )

    class Meta:
        model = User
        fields = ("username", "email", "phone", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control", "placeholder": "Имя пользователя"})
        self.fields["password1"].widget.attrs.update({"class": "form-control", "placeholder": "Пароль"})
        self.fields["password2"].widget.attrs.update({"class": "form-control", "placeholder": "Подтверждение пароля"})


class CustomAuthenticationForm(AuthenticationForm):
    """Форма входа"""

    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Имя пользователя"})
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Пароль"}))


class ProfileForm(forms.ModelForm):
    """Форма редактирования профиля"""

    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "avatar")
        widgets = {"avatar": forms.FileInput(attrs={"class": "form-control"})}

    def clean_email(self):
        """Проверка уникальности email"""
        email = self.cleaned_data.get("email")
        user = self.instance

        if User.objects.filter(email=email).exclude(pk=user.pk).exists():
            raise forms.ValidationError("Этот email уже используется")
        return email

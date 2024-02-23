from django import forms
from django.forms import widgets
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Record, Wallet, Category
from django.utils import timezone


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        min_length=6,
        max_length=150,
        required=True,
        widget=widgets.TextInput(
            attrs={"id": "username", "placeholder": "Tên đăng nhập"}
        ),
    )

    email = forms.EmailField(
        max_length=100,
        required=True,
        widget=widgets.EmailInput(attrs={"id": "email", "placeholder": "Email"}),
    )

    password1 = forms.CharField(
        min_length=8,
        required=True,
        widget=widgets.PasswordInput(
            attrs={"id": "password1", "placeholder": "Mật khẩu"}
        ),
    )

    password2 = forms.CharField(
        min_length=8,
        required=True,
        widget=widgets.PasswordInput(
            attrs={"id": "password2", "placeholder": "Nhập lại mật khẩu"}
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

        username = self.__getitem__("username")
        email = self.__getitem__("email")
        # password1 = self.__getitem__('password1')
        password2 = self.__getitem__("password2")

        errors = ""
        if username.errors:
            errors += "username;"
        if email.errors:
            errors += "email;"
        if password2.errors:
            errors += "password1;password2;"

        for visible in self.visible_fields():
            if visible.field.widget.attrs["id"] in errors:
                visible.field.widget.attrs["class"] = "form-control is-invalid"
            else:
                visible.field.widget.attrs["class"] = "form-control"


class SignInForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=widgets.TextInput(
            attrs={
                "id": "username",
                "class": "form-control",
                "placeholder": "Tên đăng nhập",
            }
        ),
    )

    password = forms.CharField(
        required=True,
        widget=widgets.PasswordInput(
            attrs={
                "id": "password",
                "class": "form-control",
                "placeholder": "Mật khẩu",
            }
        ),
    )

    remember = forms.BooleanField(
        required=False,
        widget=widgets.CheckboxInput(
            attrs={"id": "remember", "class": "form-check-input"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super(SignInForm, self).__init__(*args, **kwargs)

        if self.errors:
            for visible in self.visible_fields():
                if visible.field.widget.attrs["id"] != "remember":
                    visible.field.widget.attrs["class"] = "form-control is-invalid"


class RecordForm(forms.ModelForm):
    datetime_format = "%d/%m/%Y - %H:%M:%S"
    initial_datetime = timezone.now().strftime(datetime_format)
    timestamp = forms.DateTimeField(
        label="Tại thời điểm", initial=initial_datetime, input_formats=[datetime_format]
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={"style": "height: 100px;"}),
        label="Mô tả",
        required=False,
    )

    class Meta:
        model = Record
        fields = ["name", "wallet", "category", "money", "timestamp", "description"]
        labels = {
            "name": "Tên",
            "wallet": "Ví",
            "category": "Hạng mục",
            "money": "Số tiền",
        }


class WalletForm(forms.ModelForm):
    name = forms.CharField(label="Tên ví")
    money = forms.IntegerField(label="Số dư")
    is_calculate = forms.BooleanField(label="Tính vào báo cáo", required=False)

    class Meta:
        model = Wallet
        fields = ["name", "money", "is_calculate"]

    def __init__(self, *args, **kwargs):
        super(WalletForm, self).__init__(*args, **kwargs)
        self.initial["is_calculate"] = True

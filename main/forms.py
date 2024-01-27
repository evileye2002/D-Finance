from django import forms
from django.forms import widgets
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Income
from datetime import datetime


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


class PostIncomeForm(forms.ModelForm):
    name = forms.CharField(
        min_length=3,
        max_length=100,
        required=True,
        widget=widgets.TextInput(
            attrs={
                "id": "income-name",
                "placeholder": "Tên khoản thu",
                "class": "form-control",
            }
        ),
    )

    description = forms.CharField(
        max_length=250,
        required=False,
        widget=widgets.Textarea(
            attrs={
                "id": "income-description",
                "placeholder": "Mô tả",
                "style": "height: 100px",
                "class": "form-control",
            }
        ),
    )

    money = forms.IntegerField(
        required=True,
        widget=widgets.NumberInput(
            attrs={
                "id": "income-money",
                "placeholder": "Số tiền",
                "class": "form-control",
            }
        ),
    )

    date = forms.DateField(
        required=True,
        widget=widgets.DateInput(
            attrs={
                "id": "income-date",
                "type": "date",
                "class": "form-control",
                # "value": datetime.now().date(),
            }
        ),
    )

    time = forms.TimeField(
        required=True,
        widget=widgets.TimeInput(
            attrs={
                "id": "income-time",
                "type": "time",
                "class": "form-control",
                "style": "max-width: 120px;",
                # "value": str(datetime.now().time().hour).zfill(2)
                # + ":"
                # + str(datetime.now().time().minute).zfill(2)
                # + ":"
                # + str(datetime.now().time().second).zfill(2),
            }
        ),
    )

    datetime = forms.DateTimeField(
        required=True,
        widget=widgets.DateTimeInput(
            attrs={
                "id": "income-datetime",
            }
        ),
    )

    class Meta:
        model = Income
        fields = ["name", "description", "money", "datetime"]

    def __init__(self, *args, **kwargs):
        super(PostIncomeForm, self).__init__(*args, **kwargs)

        name = self.__getitem__("name")
        description = self.__getitem__("description")
        money = self.__getitem__("money")

        errors = ""
        if name.errors:
            errors += "name;"
        if description.errors:
            errors += "description;"
        if money.errors:
            errors += "money"

        for visible in self.visible_fields():
            if visible.field.widget.attrs["id"] in errors:
                visible.field.widget.attrs["class"] = "form-control is-invalid"
            else:
                visible.field.widget.attrs["class"] = "form-control"

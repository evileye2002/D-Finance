from django import forms
from django.forms import widgets
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Record, Wallet, Category, Loan, PeopleDirectory, CategoryGroup
from django.db import models
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
    datetime_format = "%Y-%m-%dT%H:%M"
    timestamp = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format=datetime_format,
        ),
        label="Tại thời điểm",
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
            "wallet": "Ví của bạn",
            "money": "Số tiền",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        type = kwargs.pop("type", None)
        super(RecordForm, self).__init__(*args, **kwargs)

        if user:
            self.fields["wallet"].queryset = Wallet.objects.filter(author=user)
            self.fields["wallet"].initial = Wallet.objects.first()

            if type == "income":
                self.fields["name"].label = "Tên khoản thu"
                self.fields["category"].label = "Hạng mục thu"
                self.fields["category"].queryset = Category.objects.filter(
                    models.Q(is_default=True) | models.Q(author=user),
                    category_group__name="Thu tiền",
                )
                self.fields["timestamp"].initial = timezone.now().strftime(
                    self.datetime_format
                )

            if type == "spending":
                self.fields["name"].label = "Tên khoản chi"
                self.fields["category"].label = "Hạng mục chi"
                self.fields["category"].queryset = Category.objects.filter(
                    models.Q(is_default=True) | models.Q(author=user),
                    category_group__name="Chi tiền",
                )
                self.fields["timestamp"].initial = timezone.now().strftime(
                    self.datetime_format
                )

            if type == "loan":
                self.fields["name"].label = "Tên khoản vay"
                self.fields["category"].label = "Hạng mục vay"
                self.fields["category"].queryset = Category.objects.filter(
                    models.Q(is_default=True) | models.Q(author=user),
                    category_group__name="Vay nợ",
                )

            if type == "change":
                self.fields["name"].label = "Tên bản ghi"
                self.fields["category"].label = "Hạng mục"
                self.fields["category"].queryset = Category.objects.filter(
                    models.Q(is_default=True) | models.Q(author=user),
                    models.Q(category_group__name="Thu tiền")
                    | models.Q(category_group__name="Chi tiền"),
                )


class WalletForm(forms.ModelForm):
    name = forms.CharField(label="Tên ví")
    is_calculate = forms.BooleanField(
        label="Tính vào báo cáo", required=False, initial=True
    )

    class Meta:
        model = Wallet
        fields = ["name", "is_calculate"]


class LoanForm(forms.ModelForm):
    datetime_format = "%Y-%m-%dT%H:%M"
    timestamp = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format=datetime_format,
        ),
        label="Tại thời điểm",
    )
    loan_end = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format=datetime_format,
        ),
        label="Thời hạn",
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"style": "height: 100px;"}),
        label="Mô tả",
        required=False,
    )

    class Meta:
        model = Loan
        fields = [
            "name",
            "wallet",
            "category",
            "lender_borrower",
            "money",
            "timestamp",
            "loan_end",
            "description",
        ]
        labels = {
            "name": "Tên khoản vay",
            "wallet": "Ví của bạn",
            "money": "Số tiền",
            "category": "Hạng mục vay",
            "lender_borrower": "Người cho vay/ đi vay",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(LoanForm, self).__init__(*args, **kwargs)

        if user:
            self.fields["wallet"].queryset = Wallet.objects.filter(author=user)
            self.fields["lender_borrower"].queryset = PeopleDirectory.objects.filter(
                author=user
            )
            self.fields["category"].queryset = Category.objects.filter(
                category_group__name="Vay nợ",
            )


class LoanCollectionForm(forms.ModelForm):
    datetime_format = "%Y-%m-%dT%H:%M"
    timestamp = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format=datetime_format,
        ),
        label="Tại thời điểm",
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"style": "height: 100px;"}),
        label="Mô tả",
        required=False,
    )

    class Meta:
        model = Loan
        fields = [
            "name",
            "wallet",
            "category",
            "lender_borrower",
            "money",
            "timestamp",
            "description",
        ]
        labels = {
            "name": "Tên",
            "wallet": "Ví của bạn",
            "money": "Số tiền",
            "category": "Hạng mục",
            "lender_borrower": "Người cho/đi vay",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(LoanCollectionForm, self).__init__(*args, **kwargs)

        if user:
            self.fields["wallet"].queryset = Wallet.objects.filter(author=user)
            self.fields["lender_borrower"].queryset = PeopleDirectory.objects.filter(
                author=user
            )
            self.fields["category"].queryset = Category.objects.filter(
                category_group__name="Vay nợ",
            )


class DirectoryForm(forms.ModelForm):
    class Meta:
        model = PeopleDirectory
        fields = [
            "last_name",
            "first_name",
            "phone",
            "address",
        ]
        labels = {
            "first_name": "Tên",
            "last_name": "Họ",
            "phone": "Số điện thoại",
            "address": "Địa chỉ",
        }


class CategoryForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={"style": "height: 100px;"}),
        label="Mô tả",
        required=False,
    )

    class Meta:
        model = Category
        fields = [
            "name",
            "category_group",
            "description",
        ]
        labels = {
            "name": "Tên",
            "category_group": "Nhóm",
        }

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)

        self.fields["category_group"].queryset = CategoryGroup.objects.filter(
            models.Q(name="Thu tiền") | models.Q(name="Chi tiền"),
        )

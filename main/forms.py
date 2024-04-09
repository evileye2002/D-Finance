from django import forms
from django.forms import widgets
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import *
from django.db import models
from django.utils import timezone
from .utils import datetime_local_format


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        min_length=6,
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Nhập tên tài khoản"}),
    )
    email = forms.EmailField(
        max_length=100,
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "Nhập địa chỉ email"}),
    )
    password1 = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={"placeholder": "Nhập mật khẩu"}),
    )
    password2 = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={"placeholder": "Xác nhận mật khẩu"}),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"


class SignInForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=widgets.TextInput(attrs={"placeholder": "Tên tài khoản"}),
    )

    password = forms.CharField(
        required=True,
        widget=widgets.PasswordInput(attrs={"placeholder": "Mật khẩu"}),
    )

    remember = forms.BooleanField(
        required=False,
        widget=widgets.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def __init__(self, *args, **kwargs):
        super(SignInForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            if visible.name != "remember":
                visible.field.widget.attrs["class"] = "form-control"


class RecordForm(forms.ModelForm):
    timestamp = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format=datetime_local_format,
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

            name = ""
            category_label = ""
            category = Category.objects.all()
            wallet = Wallet.objects.filter(author=user)

            if type == CategoryGroup.INCOME:
                name = "Tên khoản thu"
                category_label = "Hạng mục thu"
                category = Category.objects.filter(
                    models.Q(is_default=True) | models.Q(author=user),
                    category_group=type,
                )

            if type == CategoryGroup.SPENDING:
                name = "Tên khoản chi"
                category_label = "Hạng mục chi"
                category = Category.objects.filter(
                    models.Q(is_default=True) | models.Q(author=user),
                    category_group=type,
                )

            if type == "change":
                name = "Tên bản ghi"
                category_label = "Hạng mục"
                category = Category.objects.filter(
                    models.Q(is_default=True) | models.Q(author=user),
                    models.Q(category_group=CategoryGroup.INCOME)
                    | models.Q(category_group=CategoryGroup.SPENDING),
                )

            self.fields["name"].label = name
            self.fields["name"].required = False
            self.fields["category"].label = category_label
            self.fields["category"].queryset = category
            self.fields["wallet"].queryset = wallet
            self.fields["wallet"].initial = wallet.first()
            self.fields["timestamp"].initial = timezone.now().strftime(
                datetime_local_format
            )


class WalletForm(forms.ModelForm):
    name = forms.CharField(label="Tên ví")
    is_calculate = forms.BooleanField(
        label="Tính vào báo cáo", required=False, initial=True
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"style": "height: 100px;"}),
        label="Mô tả",
        required=False,
    )

    class Meta:
        model = Wallet
        fields = ["name", "description", "is_calculate"]


class LoanForm(forms.ModelForm):
    timestamp = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format=datetime_local_format,
        ),
        label="Tại thời điểm",
    )
    loan_end = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format=datetime_local_format,
        ),
        label="Thời hạn",
        required=False,
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
            "category": "Hạng mục",
            "lender_borrower": "Người vay/cho vay",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        type = kwargs.pop("type", None)
        lender_borrower_id = kwargs.pop("lender_borrower_id", None)
        super(LoanForm, self).__init__(*args, **kwargs)

        if user:
            category = Category.objects.all()
            wallet = Wallet.objects.filter(author=user)
            lender_borrower = PeopleDirectory.objects.filter(author=user)

            if "lend" in type:
                category = Category.objects.filter(
                    models.Q(name="Cho vay") | models.Q(name="Thu nợ"),
                )

            if "borrow" in type:
                category = Category.objects.filter(
                    models.Q(name="Đi vay") | models.Q(name="Trả nợ"),
                )

            if type == "lend-detail":
                lender_borrower = PeopleDirectory.objects.filter(id=lender_borrower_id)

            if type == "borrow-detail":
                lender_borrower = PeopleDirectory.objects.filter(id=lender_borrower_id)

            if "detail" in type:
                self.fields["lender_borrower"].initial = lender_borrower.first()

            if type == "change":
                category = Category.objects.filter(category_group=CategoryGroup.LOAN)

            self.fields["name"].required = False
            self.fields["category"].queryset = category
            self.fields["category"].initial = category.first()
            self.fields["wallet"].initial = wallet.first()
            self.fields["wallet"].queryset = wallet
            self.fields["lender_borrower"].queryset = lender_borrower
            self.fields["timestamp"].initial = timezone.now().strftime(
                datetime_local_format
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
            "name": "Tên hạng mục",
            "category_group": "Nhóm hạng mục",
        }

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)

        self.fields["category_group"].choices = [
            (choice[0], choice[1])
            for choice in CategoryGroup.choices
            if choice[0] in [CategoryGroup.INCOME, CategoryGroup.SPENDING]
        ]


class ProfileForm(forms.ModelForm):
    email = forms.CharField(
        widget=forms.TextInput(attrs={"class": "disabled"}),
        label="Email",
        required=False,
    )

    class Meta:
        model = UserProfile
        fields = ["last_name", "first_name", "phone", "address"]
        labels = {
            "last_name": "Họ",
            "first_name": "Tên",
            "phone": "Số điện thoại",
            "address": "Địa chỉ",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields["email"].disabled = True

        if user:
            self.fields["email"].initial = user.email

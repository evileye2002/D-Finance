from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, HTML, Button
from crispy_forms.bootstrap import InlineField, InlineCheckboxes

from .models import Category


class SearchForm(forms.Form):
    q = forms.CharField(max_length=100, required=False)
    t = forms.ChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(SearchForm, self).__init__(*args, **kwargs)

        if user:
            categories = Category.objects.filter()
            choices = [("all", "All")]
            choices.extend([(category.id, category.name) for category in categories])

            self.fields["t"].choices = choices


class TimestampFilterForm(forms.Form):
    f = forms.DateField(
        label="Từ ngày",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    t = forms.DateField(
        label="Đến ngày",
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date"},
        ),
    )
    c = forms.ModelChoiceField(
        label="Hạng mục",
        required=False,
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        c_group = kwargs.pop("c_group", None)
        super(TimestampFilterForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "form-filter"
        self.helper.form_class = "p-3"
        self.helper.form_method = "get"
        self.helper.layout = Layout(
            Div(
                "f",
                "t",
                css_class="d-flex align-items-end gap-3",
            ),
            InlineCheckboxes("c"),
            Div(
                HTML(
                    '<button type="button" id="reset-btn" class="btn btn-outline-danger ms-auto"><i class="fa-solid fa-arrow-rotate-right me-1"></i> Đặt lại</button>'
                ),
                HTML(
                    '<button type="submit" class="btn btn-outline-primary ms-2"><i class="fa fa-search me-1"></i> Tìm kiếm</button>'
                ),
                css_class="d-flex ",
            ),
        )

        if user:
            categories = Category.objects.filter(author=user, category_group=c_group)
            choices = [(category.id, category.name) for category in categories]
            self.fields["c"].choices = choices

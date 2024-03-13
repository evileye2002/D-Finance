from django import forms
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

from django import forms


class SearchWordForm(forms.Form):
    word = forms.CharField(label="")

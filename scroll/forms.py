from django import forms
from .models import Entry

class EntryForm(forms.ModelForm):
    label_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'bg-transparent border-none p-0 text-sm font-bold text-[#1d1d1d] focus:ring-0 placeholder:text-zinc-400 w-full',
            'placeholder': 'Add label...',
        })
    )
    class Meta:
        model = Entry
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'w-full bg-transparent text-lg text-zinc-800 focus:ring-0 border-0 outline-none resize-none',
                'placeholder': 'Write a thought...',
                'rows': 3,
            }),
        }

class SearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search thoughts...',
            'class': 'text-sm bg-transparent border-b border-zinc-100 focus:border-zinc-900 placeholder:text-zinc-400 outline-none w-full pb-1 mt-8',
        })
    )
from django import forms
from .models import Entry

class EntryForm(forms.ModelForm):
    label_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': (
                'bg-transparent border-none p-0 text-xs md:text-base text-white focus:ring-0 '
                'placeholder:text-white/60 w-full'
            ),
            'placeholder': 'Add label...',
        })
    )
    
    class Meta:
        model = Entry
        fields = ['body']
        widgets = {
        'body': forms.Textarea(attrs={
            'class': (
                'w-full bg-transparent text-white p-2 text-xs md:text-base focus:ring-0 border-0 outline-none resize-none '
                'placeholder:text-white/60'
            ),
            'placeholder': 'Add an entry...',
            'rows': 3,
        }),
    }

class SearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search thoughts...',
            'class': 'text-sm bg-transparent border-b border-zinc-100 focus:border-zinc-100 placeholder:text-zinc-400 outline-none w-full pb-1 mt-8',
        })
    )
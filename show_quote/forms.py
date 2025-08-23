# show_quote/forms.py
from django import forms
from .models import Quote

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['text', 'source', 'weight']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Введите цитату...'}),
            'source': forms.TextInput(attrs={'placeholder': 'Например: Гарри Поттер'}),
            'weight': forms.NumberInput(attrs={'min': '1', 'value': '1'}),
        }
        help_texts = {
            'weight': 'Чем выше вес — тем чаще цитата будет показываться.',
        }
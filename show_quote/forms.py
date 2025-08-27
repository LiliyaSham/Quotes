# show_quote/forms.py
from django import forms
from .models import Quote

class QuoteForm(forms.ModelForm):
    weight = forms.IntegerField(
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'min': '1',
            'max': '10',
            'value': '1',
            'placeholder': '1-10'
        }),
        help_text='Вес цитаты — от 1 до 10 (чем выше, тем чаще она будет показываться).'
    )

    class Meta:
        model = Quote
        fields = ['text', 'source', 'weight']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Введите цитату...'}),
            'source': forms.TextInput(attrs={'placeholder': 'Например: Гарри Поттер'}),
        }
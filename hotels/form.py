from django import forms
from .models import Review

class CommentForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=5, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Rate from 1 to 5'
    }))

    class Meta:
        model = Review
        fields = ['comment', 'rating']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add a comment...'
            }),
        }
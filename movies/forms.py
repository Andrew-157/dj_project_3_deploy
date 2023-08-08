from django import forms
from movies.models import Rating, Review


class RateMovieForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']


class ReviewMovieForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['content']

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')

        if content and len(content) < 11:
            msg = 'Your review is too short.'
            self.add_error('content', msg)

        return cleaned_data

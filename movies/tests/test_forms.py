from django.test import TestCase

from movies.forms import ReviewMovieForm, RateMovieForm


class ReviewMovieFormTest(TestCase):

    def test_content_label(self):
        form = ReviewMovieForm()
        field_label = form.fields['content'].label
        self.assertEqual(field_label, 'Content')


class RateMovieFormTest(TestCase):

    def test_rating_label(self):
        form = RateMovieForm()
        field_label = form.fields['rating'].label
        self.assertEqual(field_label, 'Rating')

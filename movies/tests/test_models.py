import tempfile
from datetime import date
from django.test import TestCase
from movies.models import Director, Actor, Movie, Review, Rating
from users.models import CustomUser


class DirectorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Director.objects.create(name="Quentin Tarantino",
                                photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)

    def test_name_label(self):
        director = Director.objects.get(name="Quentin Tarantino")
        field_label = director._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_photo_label(self):
        director = Director.objects.get(name="Quentin Tarantino")
        field_label = director._meta.get_field('photo').verbose_name
        self.assertEqual(field_label, 'photo')

    def test_name_max_length(self):
        director = Director.objects.get(name="Quentin Tarantino")
        max_length = director._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)

    def test_slug_max_length(self):
        director = Director.objects.get(name="Quentin Tarantino")
        max_length = director._meta.get_field('slugged_name').max_length
        self.assertEqual(max_length, 300)


class ActorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Actor.objects.create(name="Brad Pitt",
                             photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)

    def test_name_label(self):
        actor = Actor.objects.get(name="Brad Pitt")
        field_label = actor._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_photo_label(self):
        actor = Actor.objects.get(name="Brad Pitt")
        field_label = actor._meta.get_field('photo').verbose_name
        self.assertEqual(field_label, 'photo')

    def test_name_max_length(self):
        actor = Actor.objects.get(name="Brad Pitt")
        max_length = actor._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)

    def test_slug_max_length(self):
        actor = Actor.objects.get(name="Brad Pitt")
        max_length = actor._meta.get_field('slugged_name').max_length
        self.assertEqual(max_length, 300)


class MovieModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        director = Director.objects.create(name="Quentin Tarantino",
                                           photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)
        Movie.objects.create(title='Pulp Fiction',
                             synopsis='Cool movie',
                             release_date=date(1994, 10, 14),
                             country='US',
                             poster=tempfile.NamedTemporaryFile(
                                 suffix=".jpg").name,
                             director=director)

    def test_title_label(self):
        movie = Movie.objects.get(title='Pulp Fiction')
        field_label = movie._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')

    def test_synopsis_label(self):
        movie = Movie.objects.get(title='Pulp Fiction')
        field_label = movie._meta.get_field('synopsis').verbose_name
        self.assertEqual(field_label, 'synopsis')

    def test_release_date_label(self):
        movie = Movie.objects.get(title='Pulp Fiction')
        field_label = movie._meta.get_field('release_date').verbose_name
        self.assertEqual(field_label, 'release date')

    def test_country_label(self):
        movie = Movie.objects.get(title='Pulp Fiction')
        field_label = movie._meta.get_field('country').verbose_name
        self.assertEqual(field_label, 'country')

    def test_poster_label(self):
        movie = Movie.objects.get(title='Pulp Fiction')
        field_label = movie._meta.get_field('poster').verbose_name
        self.assertEqual(field_label, 'poster')

    def test_director_label(self):
        movie = Movie.objects.get(title='Pulp Fiction')
        field_label = movie._meta.get_field('director').verbose_name
        self.assertEqual(field_label, 'director')

    def test_genres_label(self):
        movie = Movie.objects.get(title='Pulp Fiction')
        field_label = movie._meta.get_field('genres').verbose_name
        self.assertEqual(field_label, 'genres')

    def test_title_max_length(self):
        movie = Movie.objects.get(title='Pulp Fiction')
        max_length = movie._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)

    def test_slug_max_length(self):
        movie = Movie.objects.get(id=1)
        max_length = movie._meta.get_field('slug').max_length
        self.assertEqual(max_length, 300)

    def test_country_max_length(self):
        movie = Movie.objects.get(id=1)
        max_length = movie._meta.get_field('country').max_length
        self.assertEqual(max_length, 2)


class ReviewModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(username="antonio",
                                              email="antonio@gmail.com",
                                              password="34somepassword34")
        director = Director.objects.create(name="Quentin Tarantino",
                                           photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)
        movie = Movie.objects.create(title='Pulp Fiction',
                                     synopsis='Cool movie',
                                     release_date=date(1994, 10, 14),
                                     country='US',
                                     poster=tempfile.NamedTemporaryFile(
                                         suffix=".jpg").name,
                                     director=director)
        Review.objects.create(
            movie=movie,
            owner=user,
            content='I think this is a cool movie.')

    def test_movie_label(self):
        review = Review.objects.get(owner__username='antonio')
        field_label = review._meta.get_field('movie').verbose_name
        self.assertEqual(field_label, 'movie')

    def test_owner_label(self):
        review = Review.objects.get(owner__username='antonio')
        field_label = review._meta.get_field('owner').verbose_name
        self.assertEqual(field_label, 'owner')

    def test_str_method(self):
        review = Review.objects.get(owner__username='antonio')
        expected_object_str = review.movie.title + ' ' + review.owner.username
        self.assertEqual(str(review), expected_object_str)


class RatingModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(username="antonio",
                                              email="antonio@gmail.com",
                                              password="34somepassword34")
        director = Director.objects.create(name="Quentin Tarantino",
                                           photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)
        movie = Movie.objects.create(title='Pulp Fiction',
                                     synopsis='Cool movie',
                                     release_date=date(1994, 10, 14),
                                     country='US',
                                     poster=tempfile.NamedTemporaryFile(
                                         suffix=".jpg").name,
                                     director=director)
        Rating.objects.create(
            movie=movie,
            owner=user,
            rating=9
        )

    def test_movie_label(self):
        rating = Rating.objects.get(owner__username='antonio')
        field_label = rating._meta.get_field('movie').verbose_name
        self.assertEqual(field_label, 'movie')

    def test_owner_label(self):
        rating = Rating.objects.get(owner__username='antonio')
        field_label = rating._meta.get_field('owner').verbose_name
        self.assertEqual(field_label, 'owner')

    def test_str_method(self):
        rating = Rating.objects.get(owner__username='antonio')
        expected_object_str = rating.movie.title + ' ' + rating.owner.username
        self.assertEqual(str(rating), expected_object_str)

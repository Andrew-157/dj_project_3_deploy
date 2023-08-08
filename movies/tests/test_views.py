import tempfile
from datetime import date
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse


from movies.models import Movie, Director, Rating, Actor, Review
from users.models import CustomUser
from taggit.models import Tag, TaggedItem


class IndexViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        director = Director.objects.create(name="Quentin Tarantino",
                                           photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)
        number_of_movies = 5
        for id in range(1, number_of_movies+1):
            Movie.objects.create(
                title=f'Movie {id}',
                synopsis=f'Cool movie {id}',
                release_date=date(1990 + id, 10, 14),
                country='US',
                poster=tempfile.NamedTemporaryFile(
                    suffix=".jpg").name,
                director=director,
            )

        number_of_tags = 5
        for id in range(1, number_of_tags+1):
            Tag.objects.create(name=f'Tag {id}')

        unused_tag = Tag.objects.create(name='Unused')

        movie_content_type = ContentType.objects.get_for_model(Movie)

        for id in range(1, 6):
            TaggedItem.objects.create(
                object_id=id,
                tag_id=id,
                content_type=movie_content_type
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('movies:index'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('movies:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/index.html')

    def test_correct_context_object_name_is_used(self):
        response = self.client.get(reverse('movies:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('genres' in response.context)

    def test_list_only_used_genres(self):
        number_of_used_tags = TaggedItem.objects.count()
        response = self.client.get(reverse('movies:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['genres']), number_of_used_tags)


class MoviesByGenreViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        director = Director.objects.create(name="Quentin Tarantino",
                                           photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)
        number_of_movies = 5
        for id in range(1, number_of_movies+1):
            Movie.objects.create(
                title=f'Movie {id}',
                synopsis=f'Cool movie {id}',
                release_date=date(1990, 10, 14),
                country='US',
                poster=tempfile.NamedTemporaryFile(
                    suffix=".jpg").name,
                director=director,
            )

        genre = Tag.objects.create(name='Random genre')

        movie_content_type = ContentType.objects.get_for_model(Movie)

        for movie in Movie.objects.all():
            TaggedItem.objects.create(
                object_id=movie.id,
                tag_id=genre.id,
                content_type=movie_content_type
            )

    def test_view_url_exists_at_desired_location(self):
        genre = Tag.objects.get(name='Random genre')
        response = self.client.get(f'/genres/{genre.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        genre = Tag.objects.get(name='Random genre')
        response = self.client.get(
            reverse('movies:genre-movies', kwargs={'slug': genre.slug}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        genre = Tag.objects.get(name='Random genre')
        response = self.client.get(
            reverse('movies:genre-movies', kwargs={'slug': genre.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/movies_by_genre.html')

    def test_correct_context_names_are_used(self):
        genre = Tag.objects.get(name='Random genre')
        response = self.client.get(
            reverse('movies:genre-movies', kwargs={'slug': genre.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('movies' in response.context)
        self.assertTrue('genre' in response.context)

    def test_correct_response_for_nonexistent_genre(self):
        genre = Tag.objects.get(name='Random genre')
        nonexistent_genre_slug = genre.slug + 'hhh'
        response = self.client.get(
            reverse("movies:genre-movies",
                    kwargs={'slug': nonexistent_genre_slug})
        )
        self.assertEqual(response.status_code, 404)


class MovieDetailViewTest(TestCase):
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

    def test_view_url_exists_at_desired_location(self):
        movie = Movie.objects.get(title='Pulp Fiction')
        response = self.client.get(f'/movies/{movie.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        movie = Movie.objects.get(title='Pulp Fiction')
        response = self.client.get(
            reverse('movies:movie-detail', kwargs={'slug': movie.slug}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        movie = Movie.objects.get(title='Pulp Fiction')
        response = self.client.get(
            reverse('movies:movie-detail', kwargs={'slug': movie.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/movie_detail.html')

    def test_view_has_number_of_ratings_in_context(self):
        movie = Movie.objects.get(title='Pulp Fiction')
        response = self.client.get(
            reverse('movies:movie-detail', kwargs={'slug': movie.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('number_of_ratings' in response.context)

    def test_correct_response_for_nonexistent_movie(self):
        movie = Movie.objects.get(title='Pulp Fiction')
        nonexistent_movie_slug = movie.slug + 'hhh'
        response = self.client.get(
            reverse("movies:genre-movies",
                    kwargs={'slug': nonexistent_movie_slug})
        )
        self.assertEqual(response.status_code, 404)

    def test_view_has_rating_of_movie_by_user_in_context(self):
        test_user = CustomUser.objects.create_user(username='johnny',
                                                   password='34somepassword34',
                                                   email='johnny@gmail.com')
        movie = Movie.objects.get(title='Pulp Fiction')
        rating = Rating.objects.create(
            movie=movie,
            owner=test_user,
            rating=9
        )
        login = self.client.login(
            username='johnny', password='34somepassword34')
        response = self.client.get(
            reverse('movies:movie-detail', kwargs={'slug': movie.slug}))
        self.assertEqual(str(response.context['user']), 'johnny')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('rating' in response.context)


class DirectorPageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        director = Director.objects.create(name="Quentin Tarantino",
                                           photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)
        number_of_movies = 5
        for id in range(1, number_of_movies+1):
            Movie.objects.create(
                title=f'Movie {id}',
                synopsis=f'Cool movie {id}',
                release_date=date(1990 + id, 10, 14),
                country='US',
                poster=tempfile.NamedTemporaryFile(
                    suffix=".jpg").name,
                director=director,
            )

    def test_view_url_exists_at_desired_place(self):
        director = Director.objects.get(name='Quentin Tarantino')
        response = self.client.get(f'/directors/{director.slugged_name}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        director = Director.objects.get(name='Quentin Tarantino')
        response = self.client.get(reverse('movies:director-page',
                                           kwargs={'slug': director.slugged_name}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        director = Director.objects.get(name='Quentin Tarantino')
        response = self.client.get(reverse(
            'movies:director-page',
            kwargs={'slug': director.slugged_name}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/director_page.html')

    def test_view_has_right_objects_in_context(self):
        director = Director.objects.get(name='Quentin Tarantino')
        response = self.client.get(reverse(
            'movies:director-page',
            kwargs={'slug': director.slugged_name}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('director' in response.context)
        self.assertTrue('movies' in response.context)

    def test_view_has_correct_number_of_movies_by_director_in_context(self):
        director = Director.objects.get(name='Quentin Tarantino')
        number_of_movies_by_director = Movie.objects.filter(
            director=director).count()
        response = self.client.get(reverse(
            'movies:director-page',
            kwargs={'slug': director.slugged_name}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context['movies']), number_of_movies_by_director)

    def test_correct_response_for_nonexistent_director(self):
        response = self.client.get(reverse(
            'movies:director-page',
            kwargs={'slug': 'Nothing'}
        ))
        self.assertEqual(response.status_code, 404)


class ActorPageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        director = Director.objects.create(name="David Fincher",
                                           photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)
        actor = Actor.objects.create(name="Brad Pitt",
                                     photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)
        number_of_movies = 5
        for id in range(1, number_of_movies+1):
            movie = Movie.objects.create(
                title=f'Movie {id}',
                synopsis=f'Cool movie {id}',
                release_date=date(1990 + id, 10, 14),
                country='US',
                poster=tempfile.NamedTemporaryFile(
                    suffix=".jpg").name,
                director=director,
            )
            movie.actors.add(actor)

    def test_view_url_exists_at_desired_place(self):
        actor = Actor.objects.get(name='Brad Pitt')
        response = self.client.get(f'/actors/{actor.slugged_name}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        actor = Actor.objects.get(name='Brad Pitt')
        response = self.client.get(reverse('movies:actor-page',
                                           kwargs={'slug': actor.slugged_name}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        actor = Actor.objects.get(name='Brad Pitt')
        response = self.client.get(reverse('movies:actor-page',
                                           kwargs={'slug': actor.slugged_name}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/actor_page.html')

    def test_view_has_correct_objects_in_context(self):
        actor = Actor.objects.get(name='Brad Pitt')
        response = self.client.get(reverse('movies:actor-page',
                                           kwargs={'slug': actor.slugged_name}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('actor' in response.context)
        self.assertTrue('movies' in response.context)

    def test_view_has_correct_number_of_movies_in_context(self):
        actor = Actor.objects.get(name='Brad Pitt')
        movies_with_actor = Movie.objects.filter(actors=actor).count()
        response = self.client.get(reverse('movies:actor-page',
                                           kwargs={'slug': actor.slugged_name}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['movies']), movies_with_actor)

    def test_correct_response_for_nonexistent_actor(self):
        response = self.client.get(reverse(
            'movies:actor-page', kwargs={'slug': 'Nothing'}
        ))
        self.assertEqual(response.status_code, 404)


class RateMovieViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')

        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')
        director = Director.objects.create(
            name='David Fincher',
            photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)

        movie = Movie.objects.create(
            title=f'Fight Club',
            synopsis=f'Cool movie',
            release_date=date(1999, 9, 10),
            country='US',
            poster=tempfile.NamedTemporaryFile(
                    suffix=".jpg").name,
            director=director,
        )

        rating = Rating.objects.create(
            movie=movie,
            owner=test_user_1,
            rating=9
        )

    def test_view_url_exists_at_desired_place_if_logged_in(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(
            username='User2', password='34somepassword34')
        response = self.client.get(f'/movies/{movie.id}/rate/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name_if_logged_in(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(
            username='User2', password='34somepassword34')
        response = self.client.get(reverse('movies:rate-movie',
                                           kwargs={'pk': movie.id}))
        self.assertEqual(response.status_code, 200)

    def test_view_not_allowed_if_logged_in_user_has_rating(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(
            username='User1', password='34somepassword34')
        response = self.client.get(reverse('movies:rate-movie',
                                           kwargs={'pk': movie.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('movies:movie-detail',
                                               kwargs={'slug': movie.slug}))
        self.assertEqual(
            str(messages[0]), 'You cannot have more than one rating per movie')
        self.assertEqual(response.status_code, 302)

    def test_redirect_if_not_logged_in(self):
        movie = Movie.objects.get(title='Fight Club')
        response = self.client.get(reverse('movies:rate-movie',
                                           kwargs={'pk': movie.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertRedirects(response, reverse('movies:movie-detail',
                                               kwargs={'slug': movie.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(str(messages[0]),
                         'Please, authenticate to rate a movie')

    def test_view_uses_correct_template_if_logged_in_without_rating(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(
            username='User2', password='34somepassword34')
        response = self.client.get(reverse('movies:rate-movie',
                                           kwargs={'pk': movie.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/rate_movie.html')

    def test_view_has_correct_objects_in_context_if_logged_in_without_rating(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(
            username='User2', password='34somepassword34'
        )
        response = self.client.get(reverse('movies:rate-movie',
                                           kwargs={'pk': movie.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('movie' in response.context)
        self.assertTrue('form' in response.context)

    def test_correct_response_for_nonexistent_movie(self):
        response = self.client.get(reverse('movies:rate-movie',
                                           kwargs={'pk': 951}))
        self.assertEqual(response.status_code, 404)

    def test_logged_user_rates_movie_with_value_less_than_zero(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(
            reverse('movies:rate-movie', kwargs={'pk': movie.id}),
            data={'rating': -1})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/rate_movie.html')

    def test_logged_user_rates_movie_with_value_bigger_than_ten(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(
            reverse('movies:rate-movie', kwargs={'pk': movie.id}),
            data={'rating': 11})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/rate_movie.html')

    def test_logged_user_rates_movie_with_empty_data(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(
            reverse('movies:rate-movie', kwargs={'pk': movie.id}),
            data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/rate_movie.html')

    def test_logged_user_rates_movie_with_no_data(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(
            reverse('movies:rate-movie', kwargs={'pk': movie.id}),
            data=None)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/rate_movie.html')

    def test_correct_response_if_movie_successfully_rated_by_logged_in_user(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(
            reverse('movies:rate-movie', kwargs={'pk': movie.id}),
            data={'rating': 9})
        messages = list(get_messages(response.wsgi_request))
        self.assertRedirects(response, reverse('movies:movie-detail',
                                               kwargs={'slug': movie.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(str(messages[0]), 'You successfully rated this movie')
        rating = Rating.objects.filter(owner__username='User2').first()
        self.assertTrue(rating is not None)


class UpdateRatingViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')

        director = Director.objects.create(
            name='David Fincher',
            photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)

        movie = Movie.objects.create(
            title=f'Fight Club',
            synopsis=f'Cool movie',
            release_date=date(1999, 9, 10),
            country='US',
            poster=tempfile.NamedTemporaryFile(
                    suffix=".jpg").name,
            director=director,
        )

        rating = Rating.objects.create(
            movie=movie,
            owner=test_user_1,
            rating=9
        )

    def test_view_url_exists_at_desired_place_if_user_with_rating_logged_in(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(f'/movies/{movie.id}/rate/update/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name_if_user_with_rating_logged(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('movies:rate-movie-update',
                                           kwargs={'pk': movie.id}))
        self.assertEqual(response.status_code, 200)

    def test_correct_objects_in_context_for_logged_user_with_rating(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('movies:rate-movie-update',
                                           kwargs={'pk': movie.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('movie' in response.context)
        self.assertTrue('form' in response.context)

    def test_correct_template_used_for_logged_user_with_rating(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('movies:rate-movie-update',
                                           kwargs={'pk': movie.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/update_rating.html')

    def test_redirect_if_user_not_logged_in(self):
        response = self.client.get(reverse('movies:rate-movie-update',
                                           kwargs={'pk': 87}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_redirect_logged_user_without_rating(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(
            username='User2', password='34somepassword34')
        response = self.client.get(reverse('movies:rate-movie-update',
                                           kwargs={'pk': movie.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('movies:movie-detail',
                                               kwargs={'slug': movie.slug}))
        self.assertEqual(
            str(messages[0]), 'You have no rating on this movie to update')

    def test_logged_user_updates_rating_with_value_less_than_zero(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('movies:rate-movie-update',
                                            kwargs={'pk': movie.id}),
                                    data={'rating': -1})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/update_rating.html')

    def test_logged_user_updates_rating_with_value_bigger_than_ten(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('movies:rate-movie-update',
                                            kwargs={'pk': movie.id}),
                                    data={'rating': 11})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/update_rating.html')

    def test_logged_user_updates_rating_with_empty_data(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('movies:rate-movie-update',
                                            kwargs={'pk': movie.id}),
                                    data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/update_rating.html')

    def test_logged_user_updates_rating_with_no_data(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('movies:rate-movie-update',
                                            kwargs={'pk': movie.id}),
                                    data=None)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/update_rating.html')

    def test_response_if_logged_user_successfully_updated_rating(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(
            reverse('movies:rate-movie-update', kwargs={'pk': movie.id}),
            data={'rating': 10})
        messages = list(get_messages(response.wsgi_request))
        self.assertRedirects(response, reverse('movies:movie-detail',
                                               kwargs={'slug': movie.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            str(messages[0]), 'You successfully updated your rating of the movie')
        rating = Rating.objects.filter(owner__username='User1').first()
        self.assertTrue(rating is not None)
        self.assertEqual(rating.rating, 10)

    def test_correct_response_for_nonexistent_movie(self):
        login = self.client.login(
            username='User1', password='34somepassword34')
        response = self.client.get(reverse('movies:rate-movie',
                                           kwargs={'pk': 951}))
        self.assertEqual(response.status_code, 404)


class DeleteRatingViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     password='34somepassword34',
                                                     email='user1@gmail.com')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     password='34somepassword34',
                                                     email='user2@gmail.com')

        director = Director.objects.create(
            name='David Fincher',
            photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)

        movie = Movie.objects.create(
            title=f'Fight Club',
            synopsis=f'Cool movie',
            release_date=date(1999, 9, 10),
            country='US',
            poster=tempfile.NamedTemporaryFile(
                    suffix=".jpg").name,
            director=director,
        )

        rating = Rating.objects.create(owner=test_user_1,
                                       movie=movie,
                                       rating=8)

    def test_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('movies:rate-movie-delete',
                                           kwargs={'pk': 99}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_redirect_logged_user_without_rating(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(
            username='User2', password='34somepassword34')
        response = self.client.post(reverse('movies:rate-movie-delete',
                                            kwargs={'pk': movie.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('movies:movie-detail',
                                               kwargs={'slug': movie.slug}))
        self.assertEqual(
            str(messages[0]), 'You have no rating on the movie to delete.')

    def test_response_logged_user_after_success_deleting_of_rating(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(
            username='User1', password='34somepassword34')
        response = self.client.post(reverse('movies:rate-movie-delete',
                                            kwargs={'pk': movie.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('movies:movie-detail',
                                               kwargs={'slug': movie.slug}))
        self.assertEqual(
            str(messages[0]), 'You successfully deleted your rating on the movie.')
        rating = Rating.objects.filter(owner__username='User1').first()
        self.assertTrue(rating is None)

    def test_correct_response_for_nonexistent_movie(self):
        login = self.client.login(
            username='User2', password='34somepassword34')
        response = self.client.post(reverse('movies:rate-movie-delete',
                                            kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 404)


class ReviewListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_1 = CustomUser.objects.create_user(username=f'User1',
                                                email=f'user1@gmail.com',
                                                password='34somepassword34')
        user_2 = CustomUser.objects.create_user(username=f'User2',
                                                email=f'user2@gmail.com',
                                                password='34somepassword34')
        user_3 = CustomUser.objects.create_user(username=f'User3',
                                                email=f'user3@gmail.com',
                                                password='34somepassword34')

        director = Director.objects.create(
            name='David Fincher',
            photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)

        movie = Movie.objects.create(
            title=f'Fight Club',
            synopsis=f'Cool movie',
            release_date=date(1999, 9, 10),
            country='US',
            poster=tempfile.NamedTemporaryFile(
                    suffix=".jpg").name,
            director=director,
        )

        review_1 = Review.objects.create(
            owner=user_1, movie=movie, content=f'Review content {user_1.id}')
        review_2 = Review.objects.create(
            owner=user_2, movie=movie, content=f'Review content {user_2.id}')

    def test_correct_response_for_nonexistent_movie(self):
        response = self.client.get(reverse('movies:review-list',
                                           kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 404)

    def test_correct_objects_in_context_for_logged_user_with_review(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('movies:review-list',
                                           kwargs={'pk': movie.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/review_list.html')
        self.assertTrue('reviews_ratings' in response.context)
        self.assertTrue('user_has_review' in response.context)
        self.assertTrue('movie' in response.context)

    def test_correct_objects_in_context_for_logged_user_without_review(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User3',
                                  password='34somepassword34')
        response = self.client.get(reverse('movies:review-list',
                                           kwargs={'pk': movie.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/review_list.html')
        self.assertTrue('reviews_ratings' in response.context)
        self.assertFalse(response.context['user_has_review'])
        self.assertTrue('movie' in response.context)

    def test_correct_length_of_reviews_in_context(self):
        movie = Movie.objects.get(title='Fight Club')
        number_of_existing_reviews = Review.objects.filter(movie=movie).count()
        response = self.client.get(reverse('movies:review-list',
                                           kwargs={'pk': movie.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['reviews_ratings']),
                         number_of_existing_reviews)


class ReviewMovieViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user_1 = CustomUser.objects.create_user(
            username='User1', email='user1@gmail.com',
            password='34somepassword34'
        )
        test_user_2 = CustomUser.objects.create_user(
            username='User2', email='user2@gmail.com',
            password='34somepassword34'
        )

        director = Director.objects.create(
            name='David Fincher',
            photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)

        movie = Movie.objects.create(
            title=f'Fight Club',
            synopsis=f'Cool movie',
            release_date=date(1999, 9, 10),
            country='US',
            poster=tempfile.NamedTemporaryFile(
                    suffix=".jpg").name,
            director=director,
        )

        Review.objects.create(
            owner=test_user_1, movie=movie,
            content='Cool movie.'
        )

    def test_redirect_for_not_logged_user(self):
        movie = Movie.objects.get(title='Fight Club')
        response = self.client.get(reverse('movies:review-movie',
                                           kwargs={'pk': movie.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('movies:review-list',
                                               kwargs={'pk': movie.id}))
        self.assertEqual(
            str(messages[0]), 'Please, authenticate to publish your review on the movie')

    def test_redirect_for_logged_user_with_existing_review(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(
            username='User1', password='34somepassword34')
        response = self.client.get(
            reverse('movies:review-movie', kwargs={'pk': movie.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('movies:review-list',
                                               kwargs={'pk': movie.id}))
        self.assertEqual(str(messages[0]),
                         'You can have only one review per movie')

    def test_correct_template_for_logged_user_without_review(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(
            username='User2', password='34somepassword34')
        response = self.client.get(
            reverse('movies:review-movie', kwargs={'pk': movie.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/review_movie.html')

    def test_correct_objects_in_context_for_logged_user_without_review(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(
            username='User2', password='34somepassword34')
        response = self.client.get(
            reverse('movies:review-movie', kwargs={'pk': movie.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/review_movie.html')
        self.assertTrue('form' in response.context)
        self.assertTrue('movie' in response.context)

    def test_correct_objects_in_context_if_invalid_data_posted(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(reverse('movies:review-movie',
                                            kwargs={'pk': movie.id}),
                                    data={'content': 'Too short'})
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/review_movie.html')
        self.assertTrue('movie' in response.context)
        self.assertTrue('form' in response.context)

    def test_logged_user_posts_review_with_empty_data(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(reverse('movies:review-movie',
                                            kwargs={'pk': movie.id},
                                            data={}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/review_movie.html')

    def test_logged_user_posts_review_with_empty_data(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(reverse('movies:review-movie',
                                            kwargs={'pk': movie.id}),
                                    data=None)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/review_movie.html')

    def test_response_if_logged_user_posted_valid_data(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.post(
            reverse('movies:review-movie', kwargs={'pk': movie.id}),
            data={'content': 'Cool movie in my opinion.'}
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('movies:review-list',
                                               kwargs={'pk': movie.id}))
        self.assertEqual(
            str(messages[0]), 'You successfully published your review on the movie')
        review = Review.objects.filter(owner__username='User2').first()
        self.assertTrue(review is not None)
        self.assertEqual(review.content, 'Cool movie in my opinion.')

    def test_correct_response_for_nonexistent_movie(self):
        response = self.client.get(
            reverse('movies:review-movie', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, 404)


class ReviewDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user_1 = CustomUser.objects.create_user(
            username='User1', password='34somepassword34',
            email='user1@gmail.com')

        test_user_2 = CustomUser.objects.create_user(
            username='User2', password='34somepassword34',
            email='user2@gmail.com'
        )

        test_user_3 = CustomUser.objects.create_user(
            username='User3', password='34somepassword34',
            email='user3@gmail.com'
        )

        director = Director.objects.create(
            name='David Fincher',
            photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)

        movie = Movie.objects.create(
            title=f'Fight Club',
            synopsis=f'Cool movie',
            release_date=date(1999, 9, 10),
            country='US',
            poster=tempfile.NamedTemporaryFile(
                    suffix=".jpg").name,
            director=director,
        )

        Review.objects.create(
            owner=test_user_1, movie=movie,
            content='Cool movie.'
        )

        Review.objects.create(
            owner=test_user_2,
            movie=movie,
            content='Movie is cool.'
        )

        Rating.objects.create(
            owner=test_user_2,
            movie=movie,
            rating=9
        )

    def test_redirect_for_not_logged_user(self):
        response = self.client.get(reverse(
            'movies:review-detail', kwargs={'pk': 99}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_redirect_for_logged_user_without_review(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User3',
                                  password='34somepassword34')
        response = self.client.get(reverse(
            'movies:review-detail', kwargs={'pk': movie.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             reverse('movies:review-list',
                                     kwargs={'pk': movie.id}))
        self.assertEqual(str(messages[0]), 'You have not reviewed the movie.')

    def test_correct_objects_in_context_for_logged_user_with_review_without_rating(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(
            username='User1', password='34somepassword34')
        response = self.client.get(reverse(
            'movies:review-detail', kwargs={'pk': movie.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('movie' in response.context)
        self.assertTrue('form' in response.context)
        self.assertTrue('review' in response.context)
        self.assertFalse(response.context['rating'])

    def test_correct_template_used_for_user_with_review(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User2',
                                  password='34somepassword34')
        response = self.client.get(reverse(
            'movies:review-detail', kwargs={'pk': movie.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/review_detail.html')

    def test_correct_objects_in_context_for_logged_user_with_review_with_rating(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(
            username='User2', password='34somepassword34')
        response = self.client.get(reverse(
            'movies:review-detail', kwargs={'pk': movie.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('movie' in response.context)
        self.assertTrue('form' in response.context)
        self.assertTrue('review' in response.context)
        self.assertTrue(response.context['rating'])

    def test_correct_objects_if_post_invalid_data(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('movies:review-detail',
                                            kwargs={'pk': movie.id}),
                                    data={'content': 'Too short'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/review_detail.html')
        self.assertTrue('movie' in response.context)
        self.assertTrue('form' in response.context)

    def test_logged_user_posts_review_with_empty_data(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('movies:review-detail',
                                            kwargs={'pk': movie.id}),
                                    data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/review_detail.html')

    def test_logged_user_posts_review_with_no_data(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('movies:review-detail',
                                            kwargs={'pk': movie.id}),
                                    data=None)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/review_detail.html')

    def test_correct_response_if_post_valid_data(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('movies:review-detail',
                                            kwargs={'pk': movie.id}),
                                    data={'content': 'Enough content.'})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('movies:review-list',
                                               kwargs={'pk': movie.id}))
        self.assertEqual(
            str(messages[0]), 'You successfully updated your review of the movie.')
        review = Review.objects.filter(owner__username='User1').first()
        self.assertTrue(review is not None)
        self.assertEqual(review.content, 'Enough content.')

    def test_correct_response_for_nonexistent_movie(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.get(reverse('movies:review-detail',
                                           kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 404)


class DeleteReviewViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user_1 = CustomUser.objects.create_user(username='User1',
                                                     email='user1@gmail.com',
                                                     password='34somepassword34')
        test_user_2 = CustomUser.objects.create_user(username='User2',
                                                     email='user2@gmail.com',
                                                     password='34somepassword34')

        director = Director.objects.create(
            name='David Fincher',
            photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)

        movie = Movie.objects.create(
            title=f'Fight Club',
            synopsis=f'Cool movie',
            release_date=date(1999, 9, 10),
            country='US',
            poster=tempfile.NamedTemporaryFile(
                    suffix=".jpg").name,
            director=director,
        )

        Review.objects.create(
            owner=test_user_1, movie=movie,
            content='Cool movie.'
        )

    def test_redirect_for_not_logged_user(self):
        response = self.client.get(reverse('movies:review-delete',
                                           kwargs={'pk': 99}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/become_user/'))

    def test_redirect_for_logged_user_without_review(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(
            username='User2', password='34somepassword34')
        response = self.client.post(reverse('movies:review-delete',
                                            kwargs={'pk': movie.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('movies:review-list',
                                               kwargs={'pk': movie.id}))
        self.assertEqual(
            str(messages[0]), 'You have no review of the movie to delete.')

    def test_correct_response_for_deleting_of_review_by_logged_user_with_review(self):
        movie = Movie.objects.get(title='Fight Club')
        login = self.client.login(
            username='User1', password='34somepassword34'
        )
        response = self.client.post(reverse('movies:review-delete',
                                            kwargs={'pk': movie.id}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('movies:review-list',
                                               kwargs={'pk': movie.id}))
        self.assertEqual(
            str(messages[0]), 'You successfully deleted your review of the movie.')
        review = Review.objects.filter(owner__username='User1').first()
        self.assertTrue(review is None)

    def test_correct_response_for_nonexistent_movie(self):
        login = self.client.login(username='User1',
                                  password='34somepassword34')
        response = self.client.post(reverse('movies:review-delete',
                                            kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 404)


class SearchResultsViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        director = Director.objects.create(
            name='David Fincher',
            photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)
        movie = Movie.objects.create(
            title=f'Fight Club',
            synopsis=f'Cool movie',
            release_date=date(1999, 9, 10),
            country='US',
            poster=tempfile.NamedTemporaryFile(
                    suffix=".jpg").name,
            director=director,
        )
        actor = Actor.objects.create(name='Brad Pitt',
                                     photo=tempfile.NamedTemporaryFile(suffix=".jpg").name)

    def test_correct_template_for_empty_search(self):
        response = self.client.get(reverse('movies:search') + '?query=')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/empty_search.html')

    def test_view_uses_correct_template(self):
        query = 'something'
        response = self.client.get(
            reverse('movies:search') + f'?q={query}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/search_results.html')

    def test_correct_objects_used_in_context(self):
        query = 'something'
        response = self.client.get(
            reverse('movies:search') + f'?q={query}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('results' in response.context)
        self.assertTrue('query' in response.context)
        self.assertTrue('number_of_results' in response.context)

    def test_view_returns_correct_length_of_results_if_directors_found(self):
        query = 'David+Fincher'
        response = self.client.get(
            reverse('movies:search') + f'?q={query}')
        number_of_directors_with_name = Director.objects.filter(
            name='David Fincher').count()
        length_of_found_directors_list = len(
            response.context['results']['directors'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(length_of_found_directors_list,
                         number_of_directors_with_name)

    def test_view_returns_correct_length_of_results_if_actors_found(self):
        query = 'Brad+Pitt'
        response = self.client.get(
            reverse('movies:search') + f'?q={query}'
        )
        number_of_actors_with_name = Actor.objects.filter(
            name='Brad Pitt').count()
        length_of_found_actors_list = len(
            response.context['results']['actors'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(length_of_found_actors_list,
                         number_of_actors_with_name)

    def test_view_returns_correct_length_of_results_if_movies_found(self):
        query = 'Fight+Club'
        response = self.client.get(
            reverse('movies:search') + f'?q={query}'
        )
        number_of_movies_with_title = Movie.objects.filter(
            title='Fight Club').count()
        length_of_found_movies_list = len(
            response.context['results']['movies'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(length_of_found_movies_list,
                         number_of_movies_with_title)

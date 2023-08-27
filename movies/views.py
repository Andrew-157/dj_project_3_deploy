from typing import Any, Dict, Optional
from django import http
from django.db import models
from django.db.models import Avg, Count
from django.db.models.query_utils import Q
from django.db.models.query import QuerySet
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.shortcuts import render
from django.views.generic import ListView, DetailView, View
from taggit.models import Tag, TaggedItem
from movies.models import Movie, Director, Actor, Rating, Review
from movies.forms import RateMovieForm, ReviewMovieForm


class IndexView(ListView):
    template_name = 'movies/index.html'
    context_object_name = 'genres'

    def get_queryset(self):
        tagged_items_ids = [t.tag_id for t in TaggedItem.objects.all()]
        return Tag.objects.filter(id__in=tagged_items_ids)\
            .order_by('name').all().annotate(number_of_movies=Count('taggit_taggeditem_items'))


class MoviesByGenreListView(ListView):
    template_name = 'movies/movies_by_genre.html'
    context_object_name = 'movies'

    def get_queryset(self) -> QuerySet[Any]:
        genre_slug = self.kwargs['slug']
        genre = Tag.objects.filter(slug=genre_slug).first()
        if not genre:
            raise Http404
        self.genre = genre
        movies = Movie.objects.filter(genres=genre).\
            select_related('director').all().annotate(
            avg_rating=Avg('ratings__rating')
        )
        return movies

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['genre'] = self.genre
        return context


class MovieDetailView(DetailView):
    model = Movie
    queryset = Movie.objects.select_related('director').\
        all().annotate(avg_rating=Avg('ratings__rating'))
    template_name = 'movies/movie_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        current_user = self.request.user
        context = super().get_context_data(**kwargs)
        if current_user.is_authenticated:
            rating = Rating.objects.\
                filter(
                    Q(movie__slug=self.kwargs['slug']) &
                    Q(owner=current_user)
                ).first()
            if rating:
                context['rating'] = rating
            else:
                context['rating'] = None
        else:
            context['rating'] = None
        context['number_of_ratings'] = Rating.objects.\
            filter(movie__slug=self.kwargs['slug']).all().count()
        return context

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class DirectorPageView(View):
    template_name = 'movies/director_page.html'

    def get(self, request, *args, **kwargs):
        director_slugged_name = self.kwargs['slug']
        director = Director.objects.filter(
            slugged_name=director_slugged_name).first()
        if not director:
            raise Http404
        movies = Movie.objects.select_related('director').\
            filter(director=director).all().order_by('title').\
            annotate(avg_rating=Avg('ratings__rating'))
        return render(request, self.template_name, {'movies': movies,
                                                    'director': director})


class ActorPageView(View):
    template_name = 'movies/actor_page.html'

    def get(self, request, *args, **kwargs):
        actor_slugged_name = self.kwargs['slug']
        actor = Actor.objects.filter(
            slugged_name=actor_slugged_name
        ).first()
        if not actor:
            raise Http404
        movies = Movie.objects.select_related('director').\
            filter(actors=actor).all().order_by('title').\
            annotate(avg_rating=Avg('ratings__rating'))
        return render(request, self.template_name, {'movies': movies,
                                                    'actor': actor})


class RateMovieView(View):
    form_class = RateMovieForm
    template_name = 'movies/rate_movie.html'
    info_message = 'Please, authenticate to rate a movie'
    warning_message = 'You cannot have more than one rating per movie'
    redirect_to = 'movies:movie-detail'
    success_message = 'You successfully rated this movie'

    def get_movie(self, pk):
        return Movie.objects.filter(id=pk).first()

    def rating_exists(self, movie_pk, user):
        return Rating.objects.\
            filter(
                Q(owner=user) &
                Q(movie__id=movie_pk)
            ).first()

    def get(self, request, *args, **kwargs):
        current_user = self.request.user
        movie_pk = self.kwargs['pk']
        movie = self.get_movie(movie_pk)
        if not movie:
            raise Http404
        if not current_user.is_authenticated:
            messages.info(
                request, self.info_message
            )
            return HttpResponseRedirect(reverse(self.redirect_to, args=(movie.slug, )))
        if self.rating_exists(movie.id, current_user):
            messages.warning(request, self.warning_message)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(movie.slug, )))
        form = self.form_class()
        return render(request, self.template_name, {'form': form,
                                                    'movie': movie})

    def post(self, request, *args, **kwargs):
        current_user = self.request.user
        movie = self.get_movie(self.kwargs['pk'])
        if not movie:
            raise Http404
        if not current_user.is_authenticated:
            messages.info(
                request, self.info_message
            )
            return HttpResponseRedirect(reverse(self.redirect_to, args=(movie.slug, )))
        if self.rating_exists(movie.id, current_user):
            messages.warning(request, self.warning_message)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(movie.slug, )))
        form = self.form_class(request.POST)
        if form.is_valid():
            form.instance.movie = movie
            form.instance.owner = current_user
            form.save()
            messages.success(request, self.success_message)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(movie.slug, )))
        return render(request, self.template_name, {'form': form,
                                                    'movie': movie})


class UpdateRatingView(View):
    template_name = 'movies/update_rating.html'
    form_class = RateMovieForm
    redirect_to = 'movies:movie-detail'
    warning_message = 'You have no rating on this movie to update'
    success_message = 'You successfully updated your rating of the movie'

    def get_movie(self, pk):
        return Movie.objects.filter(id=pk).first()

    def get_rating(self, movie_pk, user):
        return Rating.objects.\
            filter(
                Q(owner=user) &
                Q(movie__id=movie_pk)
            ).first()

    def get(self, request, *args, **kwargs):
        current_user = self.request.user
        movie = self.get_movie(self.kwargs['pk'])
        if not movie:
            raise Http404
        rating = self.get_rating(movie.id, current_user)
        if not rating:
            messages.warning(request, self.warning_message)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(movie.slug, )))
        form = self.form_class(instance=rating)
        return render(request, self.template_name, {'form': form,
                                                    'movie': movie})

    def post(self, request, *args, **kwargs):
        current_user = self.request.user
        movie = self.get_movie(self.kwargs['pk'])
        if not movie:
            raise Http404
        rating = self.get_rating(movie.id, current_user)
        if not rating:
            messages.warning(request, self.warning_message)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(movie.slug, )))
        form = self.form_class(request.POST, instance=rating)
        if form.is_valid():
            form.save()
            messages.success(request, self.success_message)
            return HttpResponseRedirect(reverse(
                self.redirect_to, args=(movie.slug, )
            ))
        return render(request, self.template_name, {'form': form,
                                                    'movie': movie})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class DeleteRatingView(View):
    redirect_to = 'movies:movie-detail'
    warning_message = 'You have no rating on the movie to delete.'
    success_message = 'You successfully deleted your rating on the movie.'

    def get_movie(self, pk):
        return Movie.objects.filter(id=pk).first()

    def get_rating(self, movie_pk, user):
        return Rating.objects.\
            filter(
                Q(owner=user) &
                Q(movie__id=movie_pk)
            ).first()

    def post(self, request, *args, **kwargs):
        current_user = self.request.user
        movie = self.get_movie(self.kwargs['pk'])
        if not movie:
            raise Http404
        rating = self.get_rating(movie.id, current_user)
        if not rating:
            messages.warning(request, self.warning_message)
            return HttpResponseRedirect(reverse(
                self.redirect_to, args=(movie.slug, )
            ))
        rating.delete()
        messages.success(request, self.success_message)
        return HttpResponseRedirect(reverse(self.redirect_to, args=(movie.slug, )))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ReviewListView(View):
    template_name = 'movies/review_list.html'

    def get_movie(self, pk):
        return Movie.objects.filter(id=pk).first()

    def get(self, request, *args, **kwargs):
        movie = self.get_movie(self.kwargs['pk'])
        if not movie:
            raise Http404
        reviews_ratings = []
        reviews = list(Review.objects.select_related('owner').
                       filter(movie__id=movie.id).all().order_by('-published'))
        reviews_owner_ids = [review.owner.id for review in reviews]
        ratings = list(Rating.objects.
                       filter(
                           Q(movie__id=movie.id) &
                           Q(owner__id__in=reviews_owner_ids)
                       ).all())
        ratings_owner_ids = [rating.owner.id for rating in ratings]
        for review in reviews:
            if review.owner.id in ratings_owner_ids:
                rating_index = ratings_owner_ids.index(review.owner.id)
                rating = ratings[rating_index]
                reviews_ratings.append([review, rating])
            else:
                reviews_ratings.append([review, None])
        if self.request.user.is_authenticated and (self.request.user.id in reviews_owner_ids):
            user_has_review = True
        else:
            user_has_review = False
        return render(request, self.template_name, {'reviews_ratings': reviews_ratings,
                                                    'user_has_review': user_has_review,
                                                    'movie': movie})


class ReviewMovieView(View):
    template_name = 'movies/review_movie.html'
    redirect_to = 'movies:review-list'
    success_message = 'You successfully published your review on the movie'
    warning_message = 'You can have only one review per movie'
    info_message = 'Please, authenticate to publish your review on the movie'
    form_class = ReviewMovieForm

    def get_movie(self, pk):
        return Movie.objects.filter(id=pk).first()

    def review_exists(self, movie_pk, user):
        return Review.objects.\
            filter(
                Q(owner=user) &
                Q(movie__id=movie_pk)
            ).first()

    def get(self, request, *args, **kwargs):
        movie = self.get_movie(self.kwargs['pk'])
        if not movie:
            raise Http404
        current_user = self.request.user
        if not current_user.is_authenticated:
            messages.info(request, self.info_message)
            return HttpResponseRedirect(reverse(
                self.redirect_to, args=(movie.id, )
            ))
        if self.review_exists(movie.id, current_user):
            messages.warning(request, self.warning_message)
            return HttpResponseRedirect(reverse(
                self.redirect_to, args=(movie.id, )
            ))
        form = self.form_class()
        return render(request, self.template_name, {'form': form,
                                                    'movie': movie})

    def post(self, request, *args, **kwargs):
        current_user = self.request.user
        movie = self.get_movie(self.kwargs['pk'])
        if not movie:
            raise Http404
        if not current_user.is_authenticated:
            messages.info(request, self.info_message)
            return HttpResponseRedirect(reverse(
                self.redirect_to, args=(movie.id, )
            ))
        if self.review_exists(movie.id, current_user):
            messages.warning(request, self.warning_message)
            return HttpResponseRedirect(reverse(
                self.redirect_to, args=(movie.id, )
            ))
        form = self.form_class(request.POST)
        if form.is_valid():
            form.instance.movie = movie
            form.instance.owner = current_user
            form.save()
            messages.success(request, self.success_message)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(movie.id, )))
        return render(request, self.template_name, {'form': form,
                                                    'movie': movie})


class ReviewDetailView(View):
    template_name = 'movies/review_detail.html'
    form_class = ReviewMovieForm
    success_message = 'You successfully updated your review of the movie.'
    warning_message = 'You have not reviewed the movie.'
    redirect_to = 'movies:review-list'

    def get_movie(self, pk):
        return Movie.objects.filter(id=pk).first()

    def get_rating(self, movie_pk, user):
        return Rating.objects. \
            filter(
                Q(owner=user) &
                Q(movie__id=movie_pk)
            ).first()

    def get_review(self, movie_pk, user):
        return Review.objects.\
            filter(
                Q(owner=user) &
                Q(movie__id=movie_pk)
            ).first()

    def get(self, request, *args, **kwargs):
        movie = self.get_movie(self.kwargs['pk'])
        if not movie:
            raise Http404
        current_user = self.request.user
        review = self.get_review(movie.id, current_user)
        if not review:
            messages.warning(request, self.warning_message)
            return HttpResponseRedirect(reverse(
                self.redirect_to, args=(movie.id, )
            ))
        rating = self.get_rating(movie.id, current_user)
        form = self.form_class(instance=review)
        return render(request, self.template_name, {'movie': movie,
                                                    'review': review,
                                                    'rating': rating,
                                                    'form': form})

    def post(self, request, *args, **kwargs):
        movie = self.get_movie(self.kwargs['pk'])
        if not movie:
            raise Http404
        current_user = request.user
        review = self.get_review(movie.id, current_user)
        if not review:
            messages.warning(request, self.warning_message)
            return HttpResponseRedirect(reverse(
                self.redirect_to, args=(movie.id, )
            ))
        rating = self.get_rating(movie.id, current_user)
        form = self.form_class(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, self.success_message)
            return HttpResponseRedirect(reverse(self.redirect_to, args=(movie.id,)))
        return render(request, self.template_name, {'movie': movie,
                                                    'review': review,
                                                    'rating': rating,
                                                    'form': form})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class DeleteReviewView(View):
    redirect_to = 'movies:review-list'
    success_message = 'You successfully deleted your review of the movie.'
    warning_message = 'You have no review of the movie to delete.'

    def get_movie(self, pk):
        return Movie.objects.filter(id=pk).first()

    def get_review(self, movie_pk, user):
        return Review.objects.\
            filter(
                Q(owner=user) &
                Q(movie__id=movie_pk)
            ).first()

    def post(self, request, *args, **kwargs):
        movie = self.get_movie(self.kwargs['pk'])
        if not movie:
            raise Http404
        current_user = self.request.user
        review = self.get_review(movie.id, current_user)
        if not review:
            messages.warning(request, self.warning_message)
            return HttpResponseRedirect(reverse(
                self.redirect_to, args=(movie.id, )
            ))
        review.delete()
        messages.success(request, self.success_message)
        return HttpResponseRedirect(reverse(self.redirect_to, args=(movie.id, )))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class SearchResultsView(View):
    template_name = 'movies/search_results.html'

    def get(self, request, *args, **kwargs):
        results = {
            'actors': [],
            'directors': [],
            'movies': []
        }
        query = self.request.GET.get('q')
        if query:
            actors = Actor.objects.filter(
                Q(name__icontains=query)
            ).order_by('name').all()
            results['actors'] = actors
            ####################################
            directors = Director.objects.filter(
                Q(name__icontains=query)
            ).order_by('name').all()
            results['directors'] = directors
            #####################################
            movies = Movie.objects.filter(
                Q(title__icontains=query)
            ).all().order_by('title')
            results['movies'] = movies
            number_of_results = len(
                results['actors']) + len(results['directors']) + len(results['movies'])
            return render(request, self.template_name, {'results': results,
                                                        'query': query,
                                                        'number_of_results': number_of_results})
        return render(request, 'movies/empty_search.html')


def error_404_handler(request, exception):
    return render(request, 'errors/404.html', status=404)

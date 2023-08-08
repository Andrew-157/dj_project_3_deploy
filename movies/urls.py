from django.views.generic import TemplateView
from django.urls import path
from movies import views

app_name = 'movies'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('genres/<str:slug>/',
         views.MoviesByGenreListView.as_view(), name='genre-movies'),
    path('movies/<slug:slug>/', views.MovieDetailView.as_view(), name='movie-detail'),
    path('directors/<str:slug>/',
         views.DirectorPageView.as_view(), name='director-page'),
    path('actors/<str:slug>/', views.ActorPageView.as_view(), name='actor-page'),
    path('movies/<int:pk>/rate/', views.RateMovieView.as_view(), name='rate-movie'),
    path('movies/<int:pk>/rate/update/',
         views.UpdateRatingView.as_view(), name='rate-movie-update'),
    path('movies/<int:pk>/rate/delete/',
         views.DeleteRatingView.as_view(), name='rate-movie-delete'),
    path('movies/<int:pk>/reviews/',
         views.ReviewListView.as_view(), name='review-list'),
    path('movies/<int:pk>/review/',
         views.ReviewMovieView.as_view(), name='review-movie'),
    path('movies/<int:pk>/reviews/detail/',
         views.ReviewDetailView.as_view(), name='review-detail'),
    path('movies/<int:pk>/reviews/delete/',
         views.DeleteReviewView.as_view(), name='review-delete'),
    path('search/', views.SearchResultsView.as_view(), name='search')
]

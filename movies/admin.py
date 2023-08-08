from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.html import format_html
from movies.models import Movie, Director, Actor


class ActorInline(admin.TabularInline):
    model = Movie.actors.through


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ['name', 'photo_tag', 'slugged_name']
    list_filter = ['name',]
    search_fields = ['name']
    readonly_fields = ['photo_tag']
    exclude = ['slugged_name']

    def photo_tag(self, obj):
        return format_html(f'<img src="{obj.photo.url}" width="60" height="100">')
    photo_tag.short_description = 'Photo'


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ['name', 'photo_tag', 'slugged_name']
    list_filter = ['name',]
    search_fields = ['name']
    readonly_fields = ['photo_tag']
    exclude = ['slugged_name']

    def photo_tag(self, obj):
        return format_html(f'<img src="{obj.photo.url}" width="60" height="100">')
    photo_tag.short_description = 'Photo'


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'slug', 'release_date', 'country', 'director', 'poster_tag',
        'genres_list'
    ]
    list_filter = ['title', 'slug', 'country',
                   'release_date', 'director', 'genres']
    search_fields = ['title', 'slug', 'country']
    readonly_fields = ['poster_tag']
    exclude = ['slug', 'actors']
    inlines = (ActorInline, )
    autocomplete_fields = ['director']

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).\
            prefetch_related('genres')

    def poster_tag(self, obj):
        return format_html(f'<img src="{obj.poster.url}" width="60" height="100">')
    poster_tag.short_description = 'Poster'

    def genres_list(self, obj):
        return u", ".join(o.name for o in obj.genres.all())

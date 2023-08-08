from django.db import models
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from taggit.managers import TaggableManager


def validate_file_size(file):
    max_kb_size = 700

    if file.size > max_kb_size * 1024:
        raise ValidationError(f'Files cannot be larger than {max_kb_size}KB')


class Director(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slugged_name = models.SlugField(max_length=300, unique=True)
    photo = models.ImageField(
        upload_to='movies/images/', validators=[validate_file_size])

    def save(self, *args, **kwargs):
        self.slugged_name = slugify(self.name)
        super(Director, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Actor(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slugged_name = models.SlugField(max_length=300, unique=True)
    photo = models.ImageField(
        upload_to='movies/images/', validators=[validate_file_size])

    def save(self, *args, **kwargs):
        self.slugged_name = slugify(self.name)
        super(Actor, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['name']


class Movie(models.Model):
    UNITED_STATES = 'US'
    UNITED_KINGDOM = 'UK'
    POLAND = 'PL'
    CANADA = 'CA'
    ITALY = 'IT'
    JAPAN = 'JP'
    CHINA = 'CN'
    COUNTRIES = (
        (UNITED_STATES, 'United States'),
        (UNITED_KINGDOM, 'United Kingdom'),
        (POLAND, 'Poland'),
        (CANADA, 'Canada'),
        (ITALY, 'Italy'),
        (JAPAN, 'Japan'),
        (CHINA, 'China')
    )
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=300, unique=True)
    synopsis = models.TextField()
    release_date = models.DateField()
    country = models.CharField(max_length=2, choices=COUNTRIES)
    poster = models.ImageField(
        upload_to='movies/images', validators=[validate_file_size])
    director = models.ForeignKey(
        Director, on_delete=models.PROTECT, related_name='movies')
    actors = models.ManyToManyField(Actor)
    genres = TaggableManager(
        verbose_name='genres', help_text='A comma-separated list of genres.'
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Movie, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Review(models.Model):
    movie = models.ForeignKey(
        Movie, related_name='reviews', on_delete=models.CASCADE)
    owner = models.ForeignKey(
        'users.CustomUser', related_name='reviews', on_delete=models.CASCADE)
    content = models.TextField()
    published = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("movie", "owner")

    def __str__(self):
        return self.movie.title + ' ' + self.owner.username


class Rating(models.Model):
    rating_choices = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5),
                      (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)]
    movie = models.ForeignKey(
        Movie, related_name='ratings', on_delete=models.CASCADE)
    owner = models.ForeignKey(
        'users.CustomUser', related_name='ratings', on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(choices=rating_choices)

    class Meta:
        unique_together = ("movie", "owner")

    def __str__(self):
        return self.movie.title + ' ' + self.owner.username

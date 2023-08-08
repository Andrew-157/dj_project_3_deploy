# Generated by Django 4.2.2 on 2023-06-12 18:52

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0005_auto_20220424_2025'),
        ('movies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='genres',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of genres.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='genres'),
        ),
    ]

# Generated by Django 2.2 on 2019-04-17 07:51

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ob', '0002_auto_20190414_2143'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='accepted_currencies_array',
            new_name='accepted_currencies',
        ),
        migrations.RenameField(
            model_name='listing',
            old_name='categories_array',
            new_name='categories',
        ),
        migrations.RenameField(
            model_name='listing',
            old_name='tags_array',
            new_name='tags',
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='moderator_accepted_currencies_array',
            new_name='moderator_accepted_currencies',
        ),
        migrations.RenameField(
            model_name='shippingoptions',
            old_name='regions_array',
            new_name='regions',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='moderator_languages',
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='moderator_languages_array',
            new_name='moderator_languages',
        ),
    ]

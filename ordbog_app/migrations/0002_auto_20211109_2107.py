# Generated by Django 3.2.8 on 2021-11-09 20:07

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ordbog_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='searchhistory',
            name='user',
        ),
        migrations.AddField(
            model_name='searchhistory',
            name='user',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]

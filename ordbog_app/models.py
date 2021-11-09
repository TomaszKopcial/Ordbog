from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Username(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(Username, on_delete=models.CASCADE)
    forget_word_time = models.IntegerField()
    forget_forever = models.BooleanField(default=False)

    def __str__(self):
        return self.user


class Notes(models.Model):
    user = models.OneToOneField(Username, on_delete=models.CASCADE)
    note = models.CharField(max_length=512)

    def __str__(self):
        return self.user


class SearchHistory(models.Model):
    user = models.OneToOneField(Username, on_delete=models.CASCADE)
    date_searched = models.DateTimeField()
    word_en = models.CharField(max_length=256)
    word_pl = models.CharField(max_length=256)
    word_dk = models.CharField(max_length=256)

    def __str__(self):
        return self.user


class Favourites(models.Model):
    user = models.OneToOneField(Username, on_delete=models.CASCADE)
    date_added = models.DateTimeField()
    word_en = models.CharField(max_length=256)
    word_pl = models.CharField(max_length=256)
    word_dk = models.CharField(max_length=256)

    def __str__(self):
        return self.user

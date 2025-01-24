from django.db import models



class User(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.email


class UserInfo(models.Model):
    age = models.IntegerField()
    height = models.IntegerField()
    weight = models.IntegerField()
    gender = models.CharField(max_length=10)
    activity_level = models.IntegerField()
    allergy = models.CharField(max_length=50)
    dietary_preferences = models.CharField(max_length=50)
    health_issues = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.age} - {self.gender}'
    
from django.contrib.auth.models import User
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.user.username
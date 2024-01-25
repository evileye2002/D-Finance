from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class RecordType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class CategoryGroup(models.Model):
    record_type = models.ForeignKey(RecordType, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Category(models.Model):
    category_group = models.ForeignKey(CategoryGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Income(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=False
    )
    name = models.CharField(max_length=50)
    money = models.IntegerField()
    description = models.TextField(max_length=50, null=True, blank=True)
    datetime = models.DateTimeField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

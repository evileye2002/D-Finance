from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


# Create your models here.
class CategoryGroup(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Category(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category_group = models.ForeignKey(CategoryGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=250, null=True, blank=True)
    is_default = models.BooleanField()
    # is_active = models.BooleanField()

    def __str__(self):
        return self.name


class Wallet(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    is_calculate = models.BooleanField()

    def __str__(self):
        return self.name

    def formatted_money(self):
        total_money = Record.objects.filter(wallet_id=self.id).aggregate(
            total_money=Sum("money")
        )["total_money"]

        if total_money is not None:
            return "{:,}".format(total_money)
        else:
            return 0


class Record(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    money = models.IntegerField()
    timestamp = models.DateTimeField()
    description = models.TextField(max_length=250, null=True, blank=True)
    # createdAt = models.DateTimeField(auto_now_add=True)
    # updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def formatted_money(self):
        return "{:,}".format(self.money)


class PeopleDirectory(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Loan(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    lender_borrower = models.ForeignKey(PeopleDirectory, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    money = models.IntegerField()
    timestamp = models.DateTimeField()
    loan_end = models.DateField(blank=True)
    description = models.TextField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name

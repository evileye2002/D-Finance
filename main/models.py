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
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Wallet(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    is_calculate = models.BooleanField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def total(self):
        income = (
            Record.objects.filter(
                wallet_id=self.id, category__category_group__name="Thu tiền"
            ).aggregate(total_money=Sum("money"))["total_money"]
            or 0
        )

        spending = (
            Record.objects.filter(
                wallet_id=self.id, category__category_group__name="Chi tiền"
            ).aggregate(total_money=Sum("money"))["total_money"]
            or 0
        )

        total = income - spending
        formatted_total = "{:,}".format(total)

        return {"as_number": total, "as_formatted_number": formatted_total}


class Record(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    money = models.IntegerField()
    timestamp = models.DateTimeField()
    description = models.TextField(max_length=250, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def formatted_money(self):
        return "{:,}".format(self.money)


class PeopleDirectory(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=12, null=True, blank=True, unique=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.last_name:
            return self.last_name + " " + self.first_name
        else:
            return self.first_name


class Loan(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    lender_borrower = models.ForeignKey(PeopleDirectory, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    money = models.IntegerField()
    timestamp = models.DateTimeField()
    loan_end = models.DateField(null=True, blank=True)
    description = models.TextField(max_length=250, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

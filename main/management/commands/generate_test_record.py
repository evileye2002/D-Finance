import os
import random
from faker import Faker

from django.db import models
from django.core.management.base import BaseCommand

from main.models import User, Record, Category, CategoryGroup, Wallet


class Command(BaseCommand):
    help = "Generate test records"

    def handle(self, *args, **options):
        fake = Faker()
        categories = [
            (CategoryGroup.SPENDING, "Điện Nước"),
            (CategoryGroup.SPENDING, "Internet"),
            (CategoryGroup.SPENDING, "Cắt Tóc"),
            (CategoryGroup.SPENDING, "Xăng Xe"),
            (CategoryGroup.SPENDING, "Quần Áo"),
            (CategoryGroup.SPENDING, "Du Lịch"),
            (CategoryGroup.SPENDING, "Quà Vặt"),
            (CategoryGroup.SPENDING, "Mỹ Phẩm"),
            (CategoryGroup.SPENDING, "Khách Sạn"),
            (CategoryGroup.INCOME, "Lương"),
            (CategoryGroup.INCOME, "Thưởng"),
            (CategoryGroup.INCOME, "Freelancer"),
        ]

        user = User.objects.filter(username="tester").first()
        if not user:
            if not os.environ.get("TESTER_PASSWORD"):
                print("Create tester user error")
                return

            user = User.objects.create_superuser(
                username="tester", password=os.environ.get("TESTER_PASSWORD")
            )

        wallet = Wallet.objects.get(author=user)

        for category in categories:
            Category.objects.get_or_create(
                author=user,
                category_group=category[0],
                name=category[1],
                is_default=False,
            )

        income_categories_choices = Category.objects.filter(
            models.Q(is_default=True) | models.Q(author=user),
            category_group=CategoryGroup.INCOME,
        )
        spending_categories_choices = Category.objects.filter(
            models.Q(is_default=True) | models.Q(author=user),
            category_group=CategoryGroup.SPENDING,
        )

        print("Rocord Generating...")

        for i in range(1, 50):
            Record.objects.create(
                category=random.choice(income_categories_choices),
                wallet=wallet,
                money=random.uniform(100000, 500000),
                timestamp=fake.date_between(start_date="-1y", end_date="today"),
            )

        for i in range(1, 50):
            Record.objects.create(
                category=random.choice(spending_categories_choices),
                wallet=wallet,
                money=random.uniform(10000, 500000),
                timestamp=fake.date_between(start_date="-1y", end_date="today"),
            )

        print("Done!")

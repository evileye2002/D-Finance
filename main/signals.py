from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Wallet
from django.utils import timezone
from .utils import append_log


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(
            author=instance, name=instance.username, is_calculate=True
        )


@receiver(post_save)
def log_entry_created(sender, instance, created, **kwargs):
    append_log(sender, instance, created, "save")


@receiver(pre_delete)
def log_deletion(sender, instance, **kwargs):
    append_log(sender, instance, None, "delete")

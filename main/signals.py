from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
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


@receiver(post_save, sender=LogEntry)
def log_entry_created(sender, instance, created, **kwargs):
    if created:
        current_time = timezone.now().strftime("%d/%b/%Y %H:%M:%S")
        log = f"[{current_time}] (administrator) {instance.user} {instance} ==> {instance.content_type}"

        print(log)
        with open(f"logs/administrator_{timezone.now().strftime("%d-%m-%Y")}.txt", "a", encoding="utf-8") as file:
            file.write("\n"+log)


@receiver(post_save)
def log_entry_created(sender, instance, created, **kwargs):
    append_log(sender, instance, created, "save")


@receiver(pre_delete)
def log_deletion(sender, instance, **kwargs):
    append_log(sender, instance, None, "delete")

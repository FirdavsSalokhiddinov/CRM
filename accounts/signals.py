from django.db.models.signals import post_migrate, post_save
from django.contrib.auth.models import User, Group
from .models import *

def create_default_groups(sender, **kwargs):
    Group.objects.get_or_create(name="admin")
    Group.objects.get_or_create(name="customer")


def customer_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser or instance.is_staff:
            group, _ = Group.objects.get_or_create(name="admin")
            instance.groups.add(group)
            return

        group, _ = Group.objects.get_or_create(name="customer")
        instance.groups.add(group)

        Customer.objects.get_or_create(
            user=instance,
            defaults={'name': instance.username},
        )


post_migrate.connect(create_default_groups)
post_save.connect(customer_profile, sender=User)

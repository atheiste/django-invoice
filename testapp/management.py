from django.db.models.signals import post_migrate
from django.dispatch import receiver

from invoice import models
from invoice import test_data


@receiver(post_migrate, sender=models)
def load_test_data(sender, **kwargs):
    """Load test model-data and images."""
    test_data.load()

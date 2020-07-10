from django.core.management.base import BaseCommand
from apps.general.models import HashTag


class Command(BaseCommand):
    def handle(self, *args, **options):
        hash_tags = HashTag.objects.all()
        for hash_tag in hash_tags:
            hash_tag.title = hash_tag.title.capitalize()
            hash_tag.save()

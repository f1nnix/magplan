from django.core.management.base import BaseCommand
from tqdm import tqdm

from magplan.models import *


class Command(BaseCommand):
    help = "Re-renders all posts content"

    def handle(self, *args, **options):
        posts = Post.objects.filter(xmd__isnull=False).exclude(xmd__exact="")
        for post in tqdm(posts):
            post.save()

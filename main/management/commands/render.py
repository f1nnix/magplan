from django.core.management.base import BaseCommand
from main.models import *
from xmd import XMDRenderer
from tqdm import tqdm


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        posts = Post.objects.filter(xmd__isnull=False).exclude(xmd__exact='')
        for post in tqdm(posts):
            renderer = XMDRenderer(images=post.images)
            markdown = mistune.Markdown(renderer=renderer)
            post.html = markdown(post.xmd)
            post.save()

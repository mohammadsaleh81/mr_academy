from django.core.management.base import BaseCommand
from django.core.files import File
from course.models import Course
from blog.models import Article, Video, Podcast
import os
import random
from pathlib import Path

class Command(BaseCommand):
    help = 'Updates thumbnails for courses and articles'

    def handle(self, *args, **kwargs):
        self.stdout.write('Updating thumbnails...')

        # Get list of thumbnail files
        thumbnail_dir = Path('media/courses/thumbnails')
        thumbnail_files = list(thumbnail_dir.glob('*.jpeg')) + list(thumbnail_dir.glob('*.png'))

        if not thumbnail_files:
            self.stdout.write(self.style.ERROR('No thumbnail files found!'))
            return

        # Update course thumbnails
        courses = Course.objects.all()
        for course in courses:
            thumbnail_file = random.choice(thumbnail_files)
            with open(thumbnail_file, 'rb') as f:
                course.thumbnail.save(
                    os.path.basename(thumbnail_file),
                    File(f),
                    save=True
                )
            self.stdout.write(f'Updated thumbnail for course: {course.title}')

        # Update article thumbnails
        articles = Article.objects.all()
        for article in articles:
            thumbnail_file = random.choice(thumbnail_files)
            with open(thumbnail_file, 'rb') as f:
                article.thumbnail.save(
                    os.path.basename(thumbnail_file),
                    File(f),
                    save=True
                )
            self.stdout.write(f'Updated thumbnail for article: {article.title}')

        # Update video thumbnails
        videos = Video.objects.all()
        for video in videos:
            thumbnail_file = random.choice(thumbnail_files)
            with open(thumbnail_file, 'rb') as f:
                video.thumbnail.save(
                    os.path.basename(thumbnail_file),
                    File(f),
                    save=True
                )
            self.stdout.write(f'Updated thumbnail for video: {video.title}')

        # Update podcast thumbnails
        podcasts = Podcast.objects.all()
        for podcast in podcasts:
            thumbnail_file = random.choice(thumbnail_files)
            with open(thumbnail_file, 'rb') as f:
                podcast.thumbnail.save(
                    os.path.basename(thumbnail_file),
                    File(f),
                    save=True
                )
            self.stdout.write(f'Updated thumbnail for podcast: {podcast.title}')

        self.stdout.write(self.style.SUCCESS('Successfully updated all thumbnails!')) 
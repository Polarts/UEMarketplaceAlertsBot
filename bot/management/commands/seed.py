from bot.models import AppState, AssetSource
from bot.functions import seed_database
from django.core.management.base import BaseCommand, CommandParser

class Command(BaseCommand):
    help = 'Seeds the database with necessary info'

    def handle(self, *args, **options):
        seed_database()
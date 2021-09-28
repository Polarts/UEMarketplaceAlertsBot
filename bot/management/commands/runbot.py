from django.core.management.base import BaseCommand, CommandParser
from bot.models import AppState, AssetSource
from bot.functions import append_log, get_json_assets, get_new_session, run_bot, scrape_assets, persist_new_assets, post_new_assets, seed_database

class Command(BaseCommand):
    help = 'Runs the bot once'

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Runs in debug mode'
        )

    def handle(self, *args, **options):
        debug = options['debug']
        
        status = None
        try:
            status = AppState.objects.get(pk=1)
        except AppState.DoesNotExist:
            seed_database()

        result = run_bot(status, debug)
        if result != None:
            self.stdout.write(result)
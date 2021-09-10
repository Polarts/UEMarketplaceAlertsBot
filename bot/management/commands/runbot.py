from requests.sessions import session
from bot.models import AssetSource
from bot.functions import get_json_assets, get_new_session, scrape_assets, persist_new_assets, post_new_assets
from django.core.management.base import BaseCommand, CommandError, CommandParser

class Command(BaseCommand):
    help = 'Runs the bot once'

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Runs in  debug mode'
        )

    def handle(self, *args, **options):
        debug = options['debug']
        session = get_new_session()

        sources = AssetSource.objects.all()
        for source in sources:
            assets = []
            if (source.type == AssetSource.SourceTypes.SCRAPE):
                assets = scrape_assets(session, source)
            else:
                assets = get_json_assets(session, source)

            new_assets = persist_new_assets(assets)
            
            if new_assets > 0:
                result = post_new_assets(source.post_title, debug)
                if debug:
                    self.stdout.write(self.style.SUCCESS(result))

from requests.sessions import session
from bot.models import AppState, AssetSource, LogEntry
from bot.functions import append_log, get_json_assets, get_new_session, scrape_assets, persist_new_assets, post_new_assets
from django.core.management.base import BaseCommand, CommandError, CommandParser

class Command(BaseCommand):
    help = 'Runs the bot once'

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Runs in debug mode'
        )

    def handle(self, *args, **options):
        status =  AppState.objects.get(pk=1)
        if status.play_state == 'PLAY':
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
        else:
            append_log('Command.handle', 0, 'But did not run because it\'s on STOP')
            self.stdout.write('Bot is on STOP!')

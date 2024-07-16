import sys

from django.core.management.base import CommandError
from django.core.management.commands.migrate import Command as MigrateCommand


class Command(MigrateCommand):
    help = "Run migrations with app name and database"

    def handle(self, *args, **options):
        app_label = options.get("app_label")
        if not app_label:
            raise CommandError("No app has been specified")

        if "--database" not in sys.argv:
            raise CommandError("No database supplied")

        super().handle(*args, **options)

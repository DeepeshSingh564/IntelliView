from django.core.management.base import BaseCommand
import os
import shutil
from django.conf import settings

class Command(BaseCommand):
    help = "Wipes SQLite DB and migrations, then rebuilds fresh schema."

    def handle(self, *args, **kwargs):
        db_path = settings.DATABASES["default"]["NAME"]

        # Remove DB file
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write(self.style.WARNING(f"Deleted database: {db_path}"))

        # Remove migration files
        app_name = "interview"
        migrations_dir = os.path.join(app_name, "migrations")
        if os.path.exists(migrations_dir):
            for filename in os.listdir(migrations_dir):
                file_path = os.path.join(migrations_dir, filename)
                if filename != "__init__.py":
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
            self.stdout.write(self.style.WARNING(f"Cleared migrations for {app_name}"))

        # Rebuild schema
        os.system("python manage.py makemigrations")
        os.system("python manage.py migrate")

        self.stdout.write(self.style.SUCCESS("Database and migrations reset successfully."))

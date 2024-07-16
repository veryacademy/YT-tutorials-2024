class DefaultAppRouter:
    """
    A database router to control all database operations on default Django apps.
    """

    def db_for_read(self, model, **hints):
        if model._meta.app_label in ["admin", "auth", "contenttypes", "sessions"]:
            return "django_db"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in ["admin", "auth", "contenttypes", "sessions"]:
            return None
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label in [
            "admin",
            "auth",
            "contenttypes",
            "sessions",
        ] and obj2._meta.app_label in ["admin", "auth", "contenttypes", "sessions"]:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in ["admin", "auth", "contenttypes", "sessions"]:
            return db == "django_db"

        return None

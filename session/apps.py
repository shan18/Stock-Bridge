from django.apps import AppConfig


class SessionConfig(AppConfig):
    name = 'session'

    def ready(self):
        """ This function imports the signal file when the app is ready """
        import session.signals

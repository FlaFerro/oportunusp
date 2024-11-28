from django.apps import AppConfig

class OportunidadesConfig(AppConfig):
    name = 'oportunidades'

    def ready(self):
        # Importando o signal
        import oportunidades.signals

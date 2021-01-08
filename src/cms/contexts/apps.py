from django.apps import AppConfig


class CmsContextsConfig(AppConfig):
    name = 'cms.contexts'
    label = 'cmscontexts'
    verbose_name = 'cms contexts'

    def ready(self):
        # that actually loads the signals
        import cms.contexts.signals # noqa

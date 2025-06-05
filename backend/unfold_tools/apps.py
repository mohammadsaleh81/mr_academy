from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UnfoldToolsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'unfold_tools'
    verbose_name = _('ابزارهای مدیریت') 
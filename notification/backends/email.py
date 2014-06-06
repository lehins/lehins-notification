from django.conf import settings
from django.template.base import TemplateDoesNotExist
from django.utils.translation import ugettext_lazy as _

from notification.backends.base import NotificationBackend

class EmailBackend(NotificationBackend):
    """
    Email delivery backend.
    """
    id = 4
    title = _("By Email")
    slug = 'email'


    def send(self, notice, context, *args, **kwargs):
        try:
            template_name = 'notification/emails/%s.html' % notice.notice_type.template_slug
            return notice.recipient.send_email(template_name=template_name, context=context)
        except TemplateDoesNotExist:
            if settings.DEBUG and not settings.NOTIFICATION_FAIL_SILENTLY:
                raise



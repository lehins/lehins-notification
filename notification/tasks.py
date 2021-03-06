import celery

from notification.backends import get_backend


@celery.task(default_retry_delay=30 * 60)
def send_notice(notice, notice_settings, context):
    context = context or {}
    related_object = None
    if notice.content_type:
        try:
            related_object = notice.content_type.get_object_for_this_type(
                id=notice.object_id)
        except notice.content_type.DoesNotExist, exc:
            raise send_notice.retry(exc=exc, countdown=60)
    context.update({'notice': notice,
                    'recipient': notice.recipient,
                    'sender': notice.sender,
                    'related_object': related_object,
                    'notice_type': notice.notice_type})
    for setting in notice_settings:
        backend = get_backend(setting.medium)
        context.update({'notice_setting': setting})
        backend.send(notice, context)

from django.conf.urls import patterns, url

from notification.views import unsubscribe # notices, mark_all_seen, feed_for_user, single, notice_settings

urlpatterns = patterns('',
    #url(r'^$', notices, name="notification_notices"),
    #url(r'^settings/$', notice_settings, name="notification_notice_settings"),
    #url(r'^(\d+)/$', single, name="notification_notice"),
    #url(r'^feed/$', feed_for_user, name="notification_feed_for_user"),
    #url(r'^mark_all_seen/$', mark_all_seen, name="notification_mark_all_seen"),
    url(r'^unsubscribe/(?P<uuid>([\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}))/'
        '(?P<token>\w+)/$', unsubscribe, name='unsubscribe'),
)

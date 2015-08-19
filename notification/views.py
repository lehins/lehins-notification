from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.forms import CheckboxInput
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from notification.models import NoticeType, NoticeSetting, NoticeMediaListChoices


class NoticeSettingGroup(object):
    title = None
    settings = []
    template = "<h5>{title}</h5><p>{settings}</p>"
    setting_template = "<p>{notice_type.display}<ul>{checkboxes}</ul></p>"
    checkbox_template = "<li><label>{label} {input}</label></li>"
    notice_types = None
    media_choices = dict(NoticeMediaListChoices())
    _notice_settings = None

    def __init__(self, user, title, notice_types):
        self.user = user
        self.title = title
        self.notice_types = notice_types

    @property
    def notice_type_settings(self):
        if self._notice_settings is None:
            self._notice_settings = []
            for notice_type in self.notice_types:
                self._notice_settings.append(
                    NoticeSetting.objects.filter_or_create(
                        self.user, notice_type).order_by('medium'))
        return self._notice_settings
        

    def get_settings(self):
        settings = []
        notice_settings = self.notice_settings
        for n, notice_type in enumerate(self.notice_types):
            checkboxes = []
            for notice_setting in notice_settings[n]:
                if not notice_setting.can_modify:
                    continue
                checkboxes.append(self.get_checkbox(notice_type, notice_setting))
            settings.append(format_html(
                self.setting_template, notice_type=notice_type,
                notice_setting=notice_setting, checkboxes='\n'.join(checkboxes)))
        return '\n'.join(settings)

    def get_checkbox_name(self, notice_type, notice_setting):
        return "%s_%s" % (notice_type.label, notice_setting.medium)

    def get_checkbox(self, notice_type, notice_setting):
        label = self.media_choices[notice_setting.medium]
        name = self.get_checkbox_name()
        return format_html(
            self.checkbox_template, label=force_text(label),
            input=CheckboxInput().render(name, notice_setting.send))

    def render(self):
        return format_html(
            self.template, title=force_text(self.title), settings=self.get_settings())

    def update_settings(self, request):
        """Modifies settings depending on the checkboxes selected in a submitted form"""
        assert request.method == 'POST'
        notice_settings = self.notice_settings
        for n, notice_type in enumerate(self.notice_types):
            for notice_setting in notice_settings[n]:
                checkbox_name = self.get_checkbox_name(notice_type, notice_setting)
                new_send = request.POST.get(checkbox_name) == "on"
                if new_send != notice_setting.send:
                    notice_setting.send = new_send
                    notice_setting.save()    
    update_settings.alters_data = True
    

class NoticeSettingsView(TemplateView):
    group_class = NoticeSettingGroup

    def get_notice_types(self):
        return NoticeType.objects.exclude(allowed=0)

    def get_notice_groups(self):
        if self.groups is None:
            return [self.group_class(
                self.request.user, "Notice Settings", self.get_notice_types())]

    def get_context_data(self, **kwargs):
        kwargs['notice_groups'] = self.get_notice_groups()
        return super(NoticeSettingsView, self).get_context_data(**kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NoticeSettingsView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        for group in context['notice_groups']:
            group.update_settings(request)
        return self.render_to_response(context)


@csrf_exempt
def unsubscribe(request, uuid=None, token=None, extra_context=None, 
                template_name='notification/unsubscribe.html',
                template_name_post='notification/unsubscribe_post.html'):
    notice_setting = get_object_or_404(NoticeSetting, uuid=uuid)
    if token != notice_setting.token:
        raise PermissionDenied
    if request.method == 'POST':
        notice_setting.send = False
        notice_setting.save()
        template_name = template_name_post
    context = {'notice_setting': notice_setting}
    if not extra_context is None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context=context)    

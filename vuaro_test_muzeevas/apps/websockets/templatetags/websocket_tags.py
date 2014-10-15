# coding: utf-8
from __future__ import unicode_literals
from string import Template
from itertools import ifilter

from django import template
from django.conf import settings


from apps.notices.clients import pymongo_cli
from apps.notices.mapping import notify_date_format, get_project_ids
from apps.main.models import Project

register = template.Library()


@register.inclusion_tag('process_dashboard.html', takes_context=True)
def get_processes(context):
    request = context['request']
    processes = list(pymongo_cli.DB['notify.processes'].find(
        {'project_id': {"$in": list(int(x) for x in get_project_ids(request.user.pk))}}
    ).sort("_id", 1))

    for x in processes:
        x['object_id'] = str(x['_id'])

    processes = ifilter(lambda p: p.get('progress', []) < 100, processes)
    processes = ifilter(lambda p: any(Project.objects.filter(pk=p['project_id']).values(
        'statistics_in_progress', 'statistics_in_progress_gl')[0].values()), processes
    )

    return {'processes': list(processes), }


@register.inclusion_tag('events_dashboard.html', takes_context=True)
def get_events(context):
    """
    Вывод уведомлений всех проектов пользователя за последний час
    """
    request = context['request']

    #from pprintpp import pprint, pformat
    evs = list(pymongo_cli.DB['notify.events'].find({'user': str(request.user)}).sort("_id", -1))

    for x in evs:
        x['object_id'] = str(x['_id'])
        x['date_formatted'] = notify_date_format(x['origin']['date_created'])

    return {'events': evs}


@register.simple_tag(takes_context=True)
def websocket_port(context):
    # from pprint import pformat
    # print pformat(settings.DEVELOP_MACHINE)
    before = '<script type="text/javascript">\n\t$(document).ready(function(){'
    after = '\t});\n\t</script>'
    template_js = '\t\tglobal_websocket_port = "$port";'
    s = Template(template_js)

    port = ':8989' if settings.DEVELOP_MACHINE else ''

    return '\n'.join([before, s.substitute(port=port), after])

from __future__ import absolute_import, unicode_literals

import os
from functools import partial
from celery import Celery
from kombu import Queue
from kombu.utils import symbol_by_name

CYANIDE_TRANS = os.environ.get('CYANIDE_TRANS', False)
default_queue = 'c.stress.trans' if CYANIDE_TRANS else 'c.stress'
CYANIDE_QUEUE = os.environ.get('CYANIDE_QUEUE', default_queue)

templates = {}

def template(name=None):

    def _register(cls):
        templates[name or cls.__name__] = '.'.join([__name__, cls.__name__])
        return cls
    return _register


def use_template(app, template='default'):
    if isinstance(template, list) and len(template) == 1:
        template = template[0]
    template = template.split(',')

    # Apply the initial template
    app.config_from_object(templates[template[0]])

    # Apply the rest of the templates
    mixin_templates(template[1:], app.conf)


def mixin_templates(template_names, conf):
    return [mixin_template(name, conf) for name in template_names]


def mixin_template(template_name, conf):
    cls = symbol_by_name(templates[template_name])
    conf.update({
        k: v for k, v in vars(cls).items()
        if not k.startswith('_')
    })


def template_names():
    return ', '.join(templates)


@template()
class default(object):
    accept_content = ['json']
    broker_url = os.environ.get('CYANIDE_BROKER', 'pyamqp://')
    broker_heartbeat = 30
    result_backend = os.environ.get('CYANIDE_BACKEND', 'rpc://')
    result_serializer = 'json'
    result_persistent = True
    result_expires = 300
    max_cached_results = 100
    task_default_queue = CYANIDE_QUEUE
    imports = ['cyanide.tasks']
    task_track_started = True
    task_queues = [
        Queue(CYANIDE_QUEUE,
              durable=not CYANIDE_TRANS,
              no_ack=CYANIDE_TRANS),
    ]
    task_serializer = 'json'
    task_publish_retry_policy = {
        'max_retries': 100,
        'interval_max': 2,
        'interval_step': 0.1,
    }
    task_protocol = 2
    if CYANIDE_TRANS:
        task_default_delivery_mode = 1
    worker_prefetch_multiplier = int(os.environ.get('CYANIDE_PREFETCH', 10))


@template()
class redis(default):
    broker_url = os.environ.get('CYANIDE_BROKER', 'redis://')
    broker_transport_options = {
        'fanout_prefix': True,
        'fanout_patterns': True,
    }
    result_backend = os.environ.get('CYANIDE_BACKEND', 'redis://')


@template()
class redistore(default):
    result_backend = 'redis://'


@template()
class acks_late(default):
    task_acks_late = True


@template()
class pickle(default):
    accept_content = ['pickle', 'json']
    task_serializer = 'pickle'
    result_serializer = 'pickle'


@template()
class confirms(default):
    broker_url = 'pyamqp://'
    broker_transport_options = {'confirm_publish': True}


@template()
class events(default):
    task_send_sent_event = True
    worker_send_task_events = True


@template()
class execv(default):
    worker_force_execv = True


@template()
class sqs(default):
    broker_url = 'sqs://'
    broker_transport_options = {
        'region': os.environ.get('AWS_REGION', 'us-east-1'),
    }


@template()
class proto1(default):
    task_protocol = 1


@template()
class vagrant1(default):
    broker_url = 'pyamqp://testing:t3s71ng@192.168.33.123//testing'


@template()
class vagrant1_redis(redis):
    broker_url = 'redis://192.168.33.123'
    result_backend = 'redis://192.168.33.123'

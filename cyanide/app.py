from __future__ import absolute_import, print_function, unicode_literals

import celery
from celery import signals
from .templates import use_template, template_names

IS_CELERY_5 = celery.VERSION[0] >= 5

class App(celery.Celery):
    cyanide_suite = 'cyanide.suites.default:Default'
    template_selected = False

    def __init__(self, *args, **kwargs):
        self.template = kwargs.pop('template', None)
        super(App, self).__init__(*args, **kwargs)

        # Directly apply the template after initialization
        self._apply_template()

    def _apply_template(self):
        """ Apply the template after the app has been initialized. """
        if self.template:
            self.use_template(self.template)
        else:
            self._maybe_use_default_template()

    def use_template(self, name='default'):
        if self.template_selected:
            raise RuntimeError('App already configured')
        self.template_selected = True
        use_template(self, name)

    def _maybe_use_default_template(self, **kwargs):
        if not self.template_selected:
            self.use_template('default')

# Instantiate the app
app = App('cyanide', set_as_current=False)

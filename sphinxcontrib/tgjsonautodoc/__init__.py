import sys, json, os, inspect, operator
from docutils import nodes
from docutils.statemachine import ViewList
from docutils.parsers.rst import Directive, directives

from sphinx.util.nodes import nested_parse_with_titles

import tg
from tg.controllers.decoratedcontroller import DecoratedController
from tg import RestController
from tg.wsgiapp import TGApp

from paste.deploy import loadapp


DOC_TEMPLATE = '''
%(path)s
^^^^^^^^^^^^^^^^^^^^^^^

.. http:%(http_method)s:: %(path)s

    %(doc)s

'''

VALIDATION_TEMPLATE = '''

**Arguments Validation**

+---------------------------+---------------------------+
| Field                     | Validator                 |
+===========================+===========================+
'''

JSONCALL_TEMPLATE = '''

**Test Request**

.. jsoncall:: %(path)s

    %(argd_json)s

'''

class TGJSONAutodoc(Directive):
    required_arguments = 0
    optional_arguments = 0
    has_content = False
    option_spec = {'skip-urls': directives.unchanged}

    def _retrieve_root(self):
        env = self.state.document.settings.env
        tgapp = env.config.tgjsonautodoc_app

        app = loadapp('config:'+tgapp, name='main', relative_to=os.getcwd())
        return TGApp().find_controller('root')()

    def _filter_controllers(self, obj):
        if isinstance(obj, DecoratedController):
            return True
        elif inspect.ismethod(obj) and hasattr(obj, 'decoration'):
            return True
        return False

    def _gather_controller_json_methods(self, root_controller):
        json_methods = {}
        controllers = [root_controller]
        while controllers:
            controller = controllers.pop()

            ci_instance = controller
            controller_class = controller.__class__

            for name, value in inspect.getmembers(controller_class, self._filter_controllers):
                if isinstance(value, DecoratedController):
                    controllers.append(value)
                elif hasattr(value, 'decoration') and value.decoration.exposed:
                    registered_engines = map(operator.itemgetter(0), value.decoration.engines.values())
                    if 'json' in registered_engines:
                        if isinstance(ci_instance, RestController):
                            path = ci_instance.mount_point
                            http_method = value.__name__.upper()
                            for normalized_method in ('GET', 'POST', 'PUT', 'DELETE'):
                                if http_method.startswith(normalized_method):
                                    http_method = normalized_method
                                    break
                        else:
                            path = ci_instance.mount_point + '/' + value.__name__
                            http_method = 'GET'

                        should_skip = False
                        for skip_url in self.options.get('skip-urls', '').split(','):
                            skip_url = skip_url.strip()
                            if skip_url and path.startswith(skip_url):
                                should_skip = True

                        if should_skip:
                            continue

                        argspec = inspect.getargspec(value)
                        argspec = (argspec[0][1:], argspec[3] or [])

                        revargs = list(reversed(argspec[0]))
                        revdefaults = list(reversed(argspec[1]))

                        argd = {}
                        for idx, arg in enumerate(revargs):
                            try:
                                val = revdefaults[idx]
                                if val is None:
                                    val = ''

                                argd[arg] = val
                            except IndexError:
                                argd[arg] = ''

                        json_methods[path + http_method] = {'args':argspec[0], 'argv':argspec[1],
                                                            'argd': argd, 'http_method': http_method,
                                                            'doc':value.__doc__, 'path':path,
                                                            'validation':value.decoration.validation}
        return json_methods

    def add_line(self, line):
        self.result.append(line, '<tgjsonautodoc>')

    def _generate_doc(self, apis):
        for unique_path, info in apis.iteritems():
            path = info['path']
            jsoncall = None
            if info['doc'] and '.. jsoncall' in info['doc']:
                _doc, jsoncall = info['doc'].split('.. jsoncall::', 1)
                info['doc'] = _doc

            doc = DOC_TEMPLATE % info

            if info['validation']:
                doc += VALIDATION_TEMPLATE
                for field, validator in info['validation'].validators.items():
                    doc += '|%s|%s|\n' % (('**%s**' % field).ljust(27), ('`%s`' % validator.__class__.__name__).ljust(27))
                    doc += '+---------------------------+---------------------------+\n'

            if jsoncall is None:
                info['argd_json'] = json.dumps(info['argd'])
                doc += JSONCALL_TEMPLATE % info
            else:
                doc += '\n**Test Request**\n\n'
                doc += '.. jsoncall::' + jsoncall

            info['doc'] = doc

    def run(self):
        self.result = ViewList()

        root_controller = self._retrieve_root()
        json_methods = self._gather_controller_json_methods(root_controller)
        self._generate_doc(json_methods)

        for method_info in json_methods.values():
            docblock = method_info['doc']
            for line in docblock.splitlines():
                self.add_line(line)

        node = nodes.section()
        node.document = self.state.document
        nested_parse_with_titles(self.state, self.result, node)
        return node.children

def setup(app):
    app.add_config_value('tgjsonautodoc_app', True, 'env')
    app.add_directive('tgjsonautodoc', TGJSONAutodoc)


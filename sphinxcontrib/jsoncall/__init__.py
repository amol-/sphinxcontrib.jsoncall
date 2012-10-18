import docutils, json, os
from urlparse import urljoin
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive

JSONCALL_JS = """
<script>
function perform_%(callid)s_call() {
    var params = {};
    jQuery("#jsoncall_%(callid)s_params input").each(function(i, e) {
       e = jQuery(e);
       params[e.attr("name")] = e.val();
    });
    jQuery.get("%(url)s",
               params,
               function(data, textStatus, jqXHR) {
                   var text_data = JSON.stringify(data, undefined, 2);
                   var dest = jQuery("#jsoncall_%(callid)s_result"); 
                   dest.html(jsoncall_syntax_highlight(text_data));
               },
               "json"
    );
}
</script>
"""

class jsoncall(nodes.Element):
    def __init__(self, url, params, callid):
        super(jsoncall, self).__init__()
        self.url = url
        self.params = params
        self.callid = callid

def visit_jsoncall_html(self, node):
    self.body.append(JSONCALL_JS % dict(callid=node.callid, url=node.url))
 
def depart_jsoncall_html(self, node):
    self.body.append('<table class="jsoncall_testform" id="jsoncall_%s_params">' % node.callid)
    for key, value in node.params.items():
        self.body.append('<tr>')
        self.body.append('<td>%s</td>' % key)
        self.body.append('<td><input style="min-width:200px;padding:5px;" type="text" name="%s" value="%s"/></td>' % (key, value))
        self.body.append('</tr>')
    self.body.append('</table>')

    self.body.append('<div class="jsoncall_button" onclick="perform_%s_call()">Test Call</div>' % node.callid)   
    self.body.append('<pre class="jsoncall_result" id="jsoncall_%s_result"></pre>' % node.callid)

class JSONCall(Directive):
    required_arguments = 1
    optional_arguments = 0
    has_content = True

    def run(self):
        env = self.state.document.settings.env

        baseurl = env.config.jsoncall_baseurl
        url = self.arguments[0]
        apiurl = urljoin( env.config.jsoncall_baseurl, url)

        callid = env.new_serialno('jsoncall')
        content = '\n'.join(self.content)
        return [jsoncall(url=apiurl, params=json.loads(content), callid=callid)]

def on_init(app):
    dirpath = os.path.dirname(__file__)
    static_path = os.path.join(dirpath, '_static')
    app.config.html_static_path.append(static_path)

    if app.config.jsoncall_inject_css:
	app.add_stylesheet('jsoncall.css')

    app.add_javascript('jsoncall.js')


def setup(app):
    app.add_config_value('jsoncall_inject_css', True, 'env')
    app.add_config_value('jsoncall_baseurl', '', 'html')

    app.connect('builder-inited', on_init)
    app.add_node(jsoncall, html=(visit_jsoncall_html, depart_jsoncall_html))
    app.add_directive('jsoncall', JSONCall)


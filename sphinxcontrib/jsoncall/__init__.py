import docutils, json, os
from urlparse import urljoin
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive
from itertools import chain, takewhile
from ._escaping import escape

JSONCALL_JS = """
<script>
function indented_fill_%(callid)s_result(data) {
    if (typeof data !== "string")
        data = JSON.stringify(data, undefined, 2);
    var dest = jQuery("#jsoncall_%(callid)s_result");
    dest.html(jsoncall_syntax_highlight(data));
}

function perform_%(callid)s_call() {
    var params = {};
    jQuery("#jsoncall_%(callid)s_params input").each(function(i, e) {
       e = jQuery(e);
       params[e.attr("name")] = e.val();
    });
    jQuery.ajax({
                "url":"%(url)s",
                "type": "%(http_method)s",
                "data": params,
                "dataType":"json",
                'success':function(data, textStatus, jqXHR) {
                       indented_fill_%(callid)s_result(data);
                },
                'error':function(jqXHR, textStatus, errorThrown) {
                        var dest = jQuery("#jsoncall_%(callid)s_result");
                        if (textStatus === "error")
                            dest.text(jqXHR.statusText);
                        else
                            dest.text(textStatus);
                }
    });
}
</script>
"""

class jsoncall(nodes.Element):
    def __init__(self, url, http_method, params, callid, static_response):
        super(jsoncall, self).__init__()
        self.http_method = http_method
        self.url = url
        self.params = params
        self.callid = callid
        self.static_response = static_response

def visit_jsoncall_html(self, node):
    self.body.append(JSONCALL_JS % dict(callid=node.callid, url=node.url, http_method=node.http_method))
 
def depart_jsoncall_html(self, node):
    self.body.append('<table class="jsoncall_testform" id="jsoncall_%s_params">' % node.callid)
    for key, value in node.params.items():
        value = escape(value)
        self.body.append('<tr>')
        self.body.append('<td>%s</td>' % key)
        self.body.append('<td><input style="min-width:200px;padding:5px;" type="text" name="%s" value="%s"/></td>' % (key, value))
        self.body.append('</tr>')
    self.body.append('</table>')

    self.body.append('<div class="jsoncall_button" onclick="perform_%s_call()">Test Call</div>' % node.callid)   
    self.body.append('<pre class="jsoncall_result" id="jsoncall_%s_result">%s</pre>' % (node.callid, node.static_response))
    self.body.append("""
<script>
    var res = jQuery("#jsoncall_%(callid)s_result");
    res.html(indented_fill_%(callid)s_result(res.text()));
</script>""" % {'callid': node.callid})

class JSONCall(Directive):
    required_arguments = 1
    optional_arguments = 0
    has_content = True
    option_spec = {'method': directives.unchanged}

    def run(self):
        env = self.state.document.settings.env
        
        http_method = self.options.get('method', 'GET')
        baseurl = env.config.jsoncall_baseurl
        url = self.arguments[0]
        apiurl = urljoin( env.config.jsoncall_baseurl, url)
        iter_content = chain(self.content)
        content = '\n'.join(list(takewhile(lambda x: x.strip(), iter_content)))
        static_response = '\n'.join(list(iter_content))
        callid = env.new_serialno('jsoncall')
        return [jsoncall(url=apiurl, http_method=http_method, params=json.loads(content), 
                         callid=callid, static_response=static_response)]

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


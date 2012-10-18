function jsoncall_syntax_highlight(json) {
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'jsoncall_sxh_number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'jsoncall_sxh_key';
            } else {
                cls = 'jsoncall_sxh_string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'jsoncall_sxh_boolean';
        } else if (/null/.test(match)) {
            cls = 'jsoncall_sxh_null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}

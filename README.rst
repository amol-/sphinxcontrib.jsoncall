=========================
JSON Call
=========================

About
=======

This extension adds a simple button to perform test calls to
JSON based apis making also possible to change parameters
values through a set of input fields.

The resulting JSON response from the API will be displayed
under the call button in a block as prettyfied and highlighted
JSON.

It is meant to be used in conjunction with the ``sphinxcontrib.httpdomain``
extension to document APIs and provide a way to play with them.

  .. image:: http://raw.github.com/amol-/sphinxcontrib.jsoncall/master/example.png

CORS
--------

Keep in mind that the requests are performed using an ajax call
so it is required that the documentation and the API server
are on same domain, or that the API server provides a **Access-Control-Allow-Origin**
header

Usage
========

First you must add the extension to your list of extensions in conf.py::

  extensions = ['sphinxcontrib.httpdomain', 'sphinxcontrib.jsoncall']

Now simply providing the base url for your api calls is enough
to start using the jsoncall directive::

  jsoncall_baseurl = 'http://somwhere.com/api'

Directives
=============

This module defines a directive, `jsoncall` this directive takes
a single required argument which is the url of the API relative
to the ``jsoncall_baseurl``::

  .. jsoncall:: /publicapitest

It is also possible to provide a bunch of arguments to the API call
through the content of the directive. The content itself needs
to be a JSON dictionary with all the parameters.

Supposing we have a */movies/retrieve?id=movieid* API it would
be possible to test it with::

  .. jsoncall:: /movies/retrieve

        {"id": "505c6a9d93681621aa0000fe"}

This will also add an **id** input field which makes possible
to modify the id value to try with different api calls.

STYLING
============

The extension provides a default CSS file which can be disabled
using the ``jsoncall_inject_css`` option.

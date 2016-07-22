#!/usr/bin/env python

"""
Commands for rendering various parts of the app stack.
"""

from glob import glob
import logging
import os

from fabric.api import local, task

import app
import app_config

logging.basicConfig(format=app_config.LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(app_config.LOG_LEVEL)

def _fake_context(path):
    """
    Create a fact request context for a given path.
    """
    return app.app.test_request_context(path=path)

def _view_from_name(name):
    """
    Determine what module a view resides in, then get
    a reference to it.
    """
    bits = name.split('.')

    # Determine which module the view resides in
    if len(bits) > 1:
        module, name = bits
    else:
        module = 'app'

    return globals()[module].__dict__[name]

@task
def less():
    """
    Render LESS files to CSS.
    """
    for path in glob('less/*.less'):
        filename = os.path.split(path)[-1]
        name = os.path.splitext(filename)[0]
        out_path = 'www/css/%s.less.css' % name

        try:
            local('node_modules/less/bin/lessc %s %s' % (path, out_path))
        except:
            logger.error('It looks like "lessc" isn\'t installed. Try running: "npm install"')
            raise

@task
def jst():
    """
    Render Underscore templates to a JST package.
    """
    try:
        local('node_modules/universal-jst/bin/jst.js --template underscore jst www/js/templates.js')
    except:
        logger.error('It looks like "jst" isn\'t installed. Try running: "npm install"')

@task
def app_config_js():
    """
    Render app_config.js to file.
    """
    from static import _app_config_js

    with _fake_context('/js/app_config.js'):
        response = _app_config_js()

    with open('www/js/app_config.js', 'w') as f:
        f.write(response.data)

@task
def copytext_js():
    """
    Render COPY to copy.js.
    """
    from static import _copy_js

    with _fake_context('/js/copytext.js'):
        response = _copy_js()

    with open('www/js/copy.js', 'w') as f:
        f.write(response.data)

@task(default=True)
def render_all():
    """
    Render HTML templates and compile assets.
    """
    less()
    jst()
    app_config_js()
    copytext_js()

    compiled_includes = {}

    # Loop over all views in the app
    for rule in app.app.url_map.iter_rules():
        rule_string = rule.rule
        name = rule.endpoint

        # Skip utility views
        if name == 'static' or name.startswith('_'):
            logger.info('Skipping %s' % name)
            continue

        if rule_string == '/<lang>/':
            for lang in app_config.LANGS:
                write_view(name, '/{0}/'.format(lang), compiled_includes)
        else:
            write_view(name, rule_string, compiled_includes)


def write_view(name, path, compiled_includes):
    from flask import g

    args = filter(None, path.split("/"))

    # Convert trailing slashes to index.html files
    if path.endswith('/'):
        filename = 'www' + path + 'index.html'
    elif path.endswith('.html'):
        filename = 'www' + path
    else:
        logger.info('Skipping %s' % name)
        return

    # Create the output path
    dirname = os.path.dirname(filename)

    if not (os.path.exists(dirname)):
        os.makedirs(dirname)

    logger.info('Rendering %s' % (filename))

    # Render views, reusing compiled assets
    with _fake_context(path):
        g.compile_includes = True
        g.compiled_includes = compiled_includes

        view = _view_from_name(name)

        content = view(*args).data

        compiled_includes = g.compiled_includes

    # Write rendered view
    # NB: Flask response object has utf-8 encoded the data
    with open(filename, 'w') as f:
        f.write(content)

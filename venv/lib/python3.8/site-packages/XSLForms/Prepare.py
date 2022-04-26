#!/usr/bin/env python

"""
Preparation of templating stylesheets.

Copyright (C) 2005, 2006 Paul Boddie <paul@boddie.org.uk>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from XSLTools import XSLOutput
import libxml2dom
import os

resource_dir = os.path.join(os.path.split(__file__)[0], "XSL")

# Generic functions.

def _ensure_document(template_name, output_name, fn, *args, **kw):
    if not os.path.exists(output_name) or \
        os.path.getmtime(output_name) < os.path.getmtime(template_name):

        fn(template_name, output_name, *args, **kw)

def _make_document(input_name, output_name, stylesheet_names, encoding=None, parameters=None):
    stylesheets = [os.path.join(resource_dir, stylesheet_name) for stylesheet_name in stylesheet_names]
    proc = XSLOutput.Processor(stylesheets, parameters=parameters or {})
    input = libxml2dom.parse(input_name)
    proc.send_output(open(output_name, "wb"), encoding, input)

# Web template functions.

def make_stylesheet(template_name, output_name, stylesheet_names=["PrepareMacro.xsl", "Prepare.xsl"], encoding=None):

    """
    Make an output stylesheet using the file with the given 'template_name',
    producing a file with the given 'output_name'.
    """

    _make_document(template_name, output_name, stylesheet_names, encoding)

def make_stylesheet_fragment(template_name, output_name, element_id, stylesheet_names=["Extract.xsl", "PrepareMacro.xsl", "Prepare.xsl"], encoding=None):

    """
    Make an output stylesheet using the file with the given 'template_name',
    producing a file with the given 'output_name', capturing the fragment
    identified by the given 'element_id'.
    """

    _make_document(template_name, output_name, stylesheet_names, encoding, parameters={"element-id" : element_id})

def ensure_stylesheet(template_name, output_name):

    """
    Ensure the presence of an output stylesheet, preparing it if necessary
    using the file with the given 'template_name', producing a file with the
    given 'output_name'.
    """

    _ensure_document(template_name, output_name, make_stylesheet)

def ensure_stylesheet_fragment(template_name, output_name, element_id):

    """
    Ensure the presence of an output stylesheet, preparing it if necessary
    using the file with the given 'template_name', producing a file with the
    given 'output_name', capturing the fragment identified by the given
    'element_id'.
    """

    _ensure_document(template_name, output_name, make_stylesheet_fragment, element_id)

# Document initialisation functions.

def make_input_stylesheet(template_name, input_name, init_enumerations=1, stylesheet_names=["Schema.xsl", "Input.xsl"], encoding=None):

    """
    Make an input stylesheet using the file with the given 'template_name',
    producing a file with the given 'input_name'. Such stylesheets are used to
    ensure the general structure of an input document.

    The optional 'init_enumerations' (defaulting to true) may be used to
    indicate whether enumerations are to be initialised from external documents.
    """

    if init_enumerations:
        init_enumerations_str = "yes"
    else:
        init_enumerations_str = "no"
    _make_document(template_name, input_name, stylesheet_names, encoding, parameters={"init-enumerations" : init_enumerations_str})

def ensure_input_stylesheet(template_name, input_name, init_enumerations=1):

    """
    Ensure the presence of an input stylesheet, preparing it if necessary
    using the file with the given 'template_name', producing a file with the
    given 'input_name'.

    The optional 'init_enumerations' (defaulting to true) may be used to
    indicate whether enumerations are to be initialised from external documents.
    """

    _ensure_document(template_name, input_name, make_input_stylesheet, init_enumerations)

# Schema-related functions.

def make_schema(template_name, output_name, stylesheet_names=["Schema.xsl"], encoding=None):

    """
    Make a schema document using the file with the given 'template_name',
    producing a file with the given 'output_name'.
    """

    _make_document(template_name, output_name, stylesheet_names, encoding)

# Template repair functions.

def fix_namespaces(template_name, output_name, stylesheet_names=["FixNamespace.xsl"], encoding=None):

    """
    Fix damage done to document namespaces by various editing tools, taking the
    document identified by 'template_name' and producing a new document with the
    given 'output_name'.
    """

    _make_document(template_name, output_name, stylesheet_names, encoding)

# Qt Designer functions.

def make_qt_fragment(template_name, output_name, widget_name, stylesheet_names=["QtDesignerExtract.xsl"], encoding=None):
    _make_document(template_name, output_name, stylesheet_names, encoding, parameters={"widget-name" : widget_name})

def ensure_qt_fragment(template_name, output_name, widget_name):
    _ensure_document(template_name, output_name, make_qt_fragment, widget_name)

# Qt Designer Web functions.

def make_qt_template(template_name, output_name, stylesheet_names=["QtDesigner.xsl"], encoding=None):
    _make_document(template_name, output_name, stylesheet_names, encoding)

def ensure_qt_template(template_name, output_name):
    _ensure_document(template_name, output_name, make_qt_template)

def make_qt_stylesheet(template_name, output_name, stylesheet_names=["QtDesigner.xsl", "PrepareMacro.xsl", "Prepare.xsl"], encoding=None):
    _make_document(template_name, output_name, stylesheet_names, encoding)

def ensure_qt_stylesheet(template_name, output_name):
    _ensure_document(template_name, output_name, make_qt_stylesheet)

# Qt Designer Web functions for fragments.

def make_qt_template_fragment(template_name, output_name, widget_name, stylesheet_names=["QtDesignerExtract.xsl", "QtDesigner.xsl"], encoding=None):
    _make_document(template_name, output_name, stylesheet_names, encoding, parameters={"widget-name" : widget_name})

def ensure_qt_template_fragment(template_name, output_name, widget_name):
    _ensure_document(template_name, output_name, make_qt_template_fragment, widget_name)

def make_qt_stylesheet_fragment(template_name, output_name, widget_name,
    stylesheet_names=["QtDesignerExtract.xsl", "QtDesigner.xsl", "PrepareMacro.xsl", "Prepare.xsl"], encoding=None):

    _make_document(template_name, output_name, stylesheet_names, encoding, parameters={"widget-name" : widget_name})

def ensure_qt_stylesheet_fragment(template_name, output_name, widget_name):
    _ensure_document(template_name, output_name, make_qt_stylesheet_fragment, widget_name)

# vim: tabstop=4 expandtab shiftwidth=4

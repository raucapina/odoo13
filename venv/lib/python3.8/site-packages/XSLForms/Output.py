#!/usr/bin/env python

"""
XSL-based form templating.

Copyright (C) 2005, 2007 Paul Boddie <paul@boddie.org.uk>

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

import Constants

# Try the conventional import first.

try:
    import libxsltmod, libxml2mod
except ImportError:
    from libxmlmods import libxml2mod
    from libxmlmods import libxsltmod

import libxml2dom
import urllib

libxml2_encoding = "utf-8"

def path_to_node(node, attribute_ref, name, multivalue=0):

    """
    Generate an XSLForms path to the given 'node', producing an attribute
    reference if 'attribute_ref' is true; for example:

    /package$1/discriminators$5/discriminator$1/category

    Otherwise an element reference is produced; for example:

    /package$1/discriminators$5/discriminator$1

    Use the given 'name' to complete the path if an attribute reference is
    required (and if a genuine attribute is found at the context node -
    otherwise 'name' will be None and the context node will be treated like an
    attribute).

    If 'multivalue' is true and 'attribute_ref' is set, produce an attribute
    reference using the given 'name':

    /package$1/categories$1/category$$name

    If 'multivalue' is true and 'attribute_ref' is not set, produce an attribute
    reference using the given 'name' of form (element, attribute):

    /package$1/categories$1/element$$attribute
    """

    l = []
    # Skip attribute reference.
    if node.nodeType == node.ATTRIBUTE_NODE:
        node = node.parentNode
    # Manually insert the attribute name if defined.
    if attribute_ref:
        # A real attribute is referenced.
        if name is not None:
            l.insert(0, name)
            if multivalue:
                l.insert(0, Constants.multi_separator)
                l.insert(0, node.nodeName)
                node = node.parentNode
            l.insert(0, Constants.path_separator)
        # Otherwise, treat the element name as an attribute name.
        # NOTE: Not sure how useful this is.
        else:
            l.insert(0, node.nodeName)
            l.insert(0, Constants.path_separator)
            node = node.parentNode
    # Otherwise insert any multivalue references (eg. list-attribute).
    elif multivalue:
        element_name, attribute_name = name
        l.insert(0, attribute_name)
        l.insert(0, Constants.multi_separator)
        l.insert(0, element_name)
        l.insert(0, Constants.path_separator)

    # Element references.
    while node is not None and node.nodeType != node.DOCUMENT_NODE:
        l.insert(0, str(int(node.xpath("count(preceding-sibling::*) + 1"))))
        l.insert(0, Constants.pair_separator)
        l.insert(0, node.nodeName)
        l.insert(0, Constants.path_separator)
        node = node.parentNode
    return "".join(l)

def path_to_context(context, attribute_ref, multivalue_name=None):

    """
    As a libxslt extension function, return a string containing the XSLForms
    path to the 'context' node, using the special "this-name" variable to
    complete the path if an attribute reference is required (as indicated by
    'attribute_ref' being set to true). If 'multivalue_name' is set, produce a
    reference to a multivalued field using the given string as the attribute
    name.
    """

    context = libxml2mod.xmlXPathParserGetContext(context)
    transform_context = libxsltmod.xsltXPathGetTransformContext(context)
    name_var = libxsltmod.xsltVariableLookup(transform_context, "this-name", None)
    if multivalue_name is not None:
        name = multivalue_name
        multivalue = 1
    elif name_var is not None:
        name = libxml2mod.xmlNodeGetContent(name_var[0])
        name = unicode(name, libxml2_encoding)
        multivalue = 0
    else:
        name = None
        multivalue = 0
    node = libxml2dom.Node(libxml2mod.xmlXPathGetContextNode(context))
    return path_to_node(node, attribute_ref, name, multivalue)

# Exposed extension functions.

def this_element(context):

    """
    Exposed as {template:this-element()}.

    Provides a reference to the current element in the form data structure.
    """

    #print "this_element"
    r = path_to_context(context, 0)
    return r.encode(libxml2_encoding)

def this_attribute(context):

    """
    Exposed as {template:this-attribute()}.

    Provides a reference to the current attribute in the form data structure.
    """

    #print "this_attribute"
    r = path_to_context(context, 1)
    return r.encode(libxml2_encoding)

def new_attribute(context, name):

    """
    Exposed as {template:new-attribute(name)}.

    Provides a reference to a new attribute of the given 'name' on the current
    element in the form data structure.
    """

    #print "new_attribute"
    name = unicode(name, libxml2_encoding)
    r = path_to_context(context, 0) + "/" + name
    return r.encode(libxml2_encoding)

def other_elements(context, nodes):

    """
    Exposed as {template:other-elements(nodes)}.

    Provides a reference to other elements in the form data structure according
    to the specified 'nodes' parameter (an XPath expression in the template).
    """

    #print "other_elements"
    names = []
    for node in nodes:
        name = path_to_node(libxml2dom.Node(node), 0, None, 0)
        if name not in names:
            names.append(name)
    r = ",".join(names)
    return r.encode(libxml2_encoding)

def list_attribute(context, element_name, attribute_name):

    """
    Exposed as {template:list-attribute(element_name, attribute_name)}.

    Provides a reference to one or many elements of the given 'element_name'
    found under the current element in the form data structure having
    attributes with the given 'attribute_name'.
    """

    #print "list_attribute"
    element_name = unicode(element_name, libxml2_encoding)
    attribute_name = unicode(attribute_name, libxml2_encoding)
    r = path_to_context(context, 0, (element_name, attribute_name))
    return r.encode(libxml2_encoding)

def other_list_attributes(context, element_name, attribute_name, nodes):

    """
    Exposed as {template:other-list-attributes(element_name, attribute_name, nodes)}.

    Provides a reference to other elements in the form data structure, found
    under the specified 'nodes' (described using an XPath expression in the
    template) having the given 'element_name' and bearing attributes of the
    given 'attribute_name'.
    """

    #print "other_list_attributes"
    element_name = unicode(element_name, libxml2_encoding)
    attribute_name = unicode(attribute_name, libxml2_encoding)
    names = []
    for node in nodes:
        name = path_to_node(libxml2dom.Node(node), 0, (element_name, attribute_name), 1)
        if name not in names:
            names.append(name)
    r = ",".join(names)
    return r.encode(libxml2_encoding)

def other_attributes(context, attribute_name, nodes):

    """
    Exposed as {template:other-attributes(name, nodes)}.

    Provides a reference to attributes in the form data structure of the given
    'attribute_name' residing on the specified 'nodes' (described using an XPath
    expression in the template).
    """

    #print "other_attributes"
    attribute_name = unicode(attribute_name, libxml2_encoding)
    # NOTE: Cannot directly reference attributes in the nodes list because
    # NOTE: libxml2dom does not yet support parent element discovery on
    # NOTE: attributes.
    names = []
    for node in nodes:
        name = path_to_node(libxml2dom.Node(node), 1, attribute_name, 0)
        if name not in names:
            names.append(name)
    r = ",".join(names)
    return r.encode(libxml2_encoding)

def child_element(context, element_name, position, node_paths):

    """
    Exposed as {template:child-element(element_name, position, node_paths)}.

    Provides relative paths to the specifed 'element_name', having the given
    'position' (1-based) under each element specified in 'node_paths' (provided
    by calls to other extension functions in the template). For example:

    template:child-element('comment', 1, template:this-element()) -> '.../comment$1'
    """

    element_name = unicode(element_name, libxml2_encoding)
    l = []
    for node_path in node_paths.split(","):
        l.append(node_path + Constants.path_separator + element_name
            + Constants.pair_separator + str(int(position)))
    return ",".join(l).encode(libxml2_encoding)

def child_attribute(context, attribute_name, node_paths):

    """
    Exposed as {template:child-attribute(attribute_name, node_paths)}.

    Provides a relative path to the specifed 'attribute_name' for each element
    specified in 'node_paths' (provided by calls to other extension functions in
    the template). For example:

    template:child-attribute('value', template:this-element()) -> '.../value'
    """

    attribute_name = unicode(attribute_name, libxml2_encoding)
    l = []
    for node_path in node_paths.split(","):
        l.append(node_path + Constants.path_separator + attribute_name)
    return ",".join(l).encode(libxml2_encoding)

def selector_name(context, field_name, nodes):

    """
    Exposed as {template:selector-name(field_name, nodes)}.

    Provides a selector field name defined using 'field_name' and referring to
    the given 'nodes'. For example:

    template:selector-name('add-platform', package/platforms) -> 'add-platform=/package$1/platforms$1'

    NOTE: The 'nodes' must be element references.
    """

    #print "selector_name"
    names = []
    for node in nodes:
        name = path_to_node(libxml2dom.Node(node), 0, None, 0)
        if name not in names:
            names.append(field_name + "=" + name)
    r = ",".join(names)
    return r.encode(libxml2_encoding)

# Old implementations.

def multi_field_name(context, multivalue_name):
    #print "multi_field_name"
    multivalue_name = unicode(multivalue_name, libxml2_encoding)
    r = path_to_context(context, 1, multivalue_name)
    return r.encode(libxml2_encoding)

def other_multi_field_names(context, multivalue_name, nodes):
    #print "other_multi_field_names"
    multivalue_name = unicode(multivalue_name, libxml2_encoding)
    names = []
    for node in nodes:
        name = path_to_node(libxml2dom.Node(node), 1, multivalue_name, 1)
        if name not in names:
            names.append(name)
    r = ",".join(names)
    return r.encode(libxml2_encoding)

# Utility functions.

def xslforms_range(context, range_spec):

    """
    Exposed as {template:range(range_spec)}.

    The 'range_spec' is split up into 'start', 'finish' and 'step' according to
    the following format:

    start...finish...step

    Provides the Python range function by producing a list of numbers, starting
    at 'start', ending one step before 'finish', and employing the optional
    'step' to indicate the magnitude of the difference between successive
    elements in the list as well as the "direction" of the sequence. By default,
    'step' is set to 1.

    NOTE: This uses a single string because template:element and other
    NOTE: annotations use commas to separate fields, thus making the usage of
    NOTE: this function impossible if each range parameter is exposed as a
    NOTE: function parameter.
    NOTE: The returning of values from this function is not fully verified, and
    NOTE: it is probably better to use other extension functions instead of this
    NOTE: one to achieve simple results (such as str:split from EXSLT).
    """

    parts = range_spec.split("...")
    start, finish = parts[:2]
    if len(parts) > 2:
        step = parts[2]
    else:
        step = None

    start = int(start)
    finish = int(finish)
    if step is not None:
        step = int(step)
    else:
        step = 1

    # Create a list of elements.
    # NOTE: libxslt complains: "Got a CObject"

    range_elements = libxml2mod.xmlXPathNewNodeSet(None)
    for i in range(start, finish, step):
        range_elements.append(libxml2mod.xmlNewText(str(i)))
    return range_elements

def i18n(context, value):

    """
    Exposed as {template:i18n(value)}.

    Provides a translation of the given 'value' using the 'translations' and
    'locale' variables defined in the output stylesheet. The 'value' may be a
    string or a collection of nodes, each having a textual value, where such
    values are then concatenated to produce a single string value.
    """

    if isinstance(value, str):
        value = unicode(value, libxml2_encoding)
    else:
        l = []
        for node in value:
            s = libxml2dom.Node(node).nodeValue
            l.append(s)
        value = "".join(l)

    context = libxml2mod.xmlXPathParserGetContext(context)
    transform_context = libxsltmod.xsltXPathGetTransformContext(context)
    translations_var = libxsltmod.xsltVariableLookup(transform_context, "translations", None)
    locale_var = libxsltmod.xsltVariableLookup(transform_context, "locale", None)
    if translations_var is not None and translations_var and locale_var is not None:
        translations = libxml2dom.Node(translations_var[0])
        results = translations.xpath("/translations/locale[code/@value='%s']/translation[@value='%s']/text()" % (locale_var, value))
        if not results:
            results = translations.xpath("/translations/locale[1]/translation[@value='%s']/text()" % value)
        if results:
            return results[0].nodeValue.encode(libxml2_encoding)
    return value.encode(libxml2_encoding)

def choice(context, value, true_string, false_string=None):

    """
    Exposed as {template:choice(value, true_string, false_string)}.

    Using the given boolean 'value', which may itself be an expression evaluated
    by the XSLT processor, return the 'true_string' if 'value' is true or the
    'false_string' if 'value' is false. If 'false_string' is omitted and if
    'value' evaluates to a false value, an empty string is returned.
    """

    if value:
        return true_string
    else:
        return false_string or ""

def url_encode(context, nodes, charset=libxml2_encoding):

    """
    Exposed as {template:url-encode(nodes)}.

    Provides a "URL encoded" string created from the merged textual contents of
    the given 'nodes', with the encoded character values representing characters
    in the optional 'charset' (UTF-8 if not specified). Note that / and #
    characters are replaced with their "URL encoded" character values.

    If a string value is supplied for 'nodes', this will be translated instead.

    template:url-encode(./text(), 'iso-8859-1')
    """

    l = []
    if isinstance(nodes, str):
        return urllib.quote(nodes.encode(libxml2_encoding)).replace("/", "%2F").replace("#", "%23")

    for node in nodes:
        s = libxml2dom.Node(node).nodeValue
        l.append(urllib.quote(s.encode(libxml2_encoding)).replace("/", "%2F").replace("#", "%23"))
    output = "".join(l)
    return output

def element_path(context, field_names):

    """
    Exposed as {template:element-path(field_names)}.

    Convert the given 'field_names' back to XPath references.
    For example:

    /configuration$1/details$1/base-system$$value -> /*[position() = 1]/*[position() = 1]/base-system

    If more than one field name is given - ie. 'field_names' contains a
    comma-separated list of names - then only the first name is used.

    To use this function effectively, use the result of another function as the
    argument. For example:

    template:element-path(template:this-element())
    template:element-path(template:other-elements(matches))
    template:element-path(template:other-elements(..))
    """

    field_name = field_names.split(",")[0]

    # Get the main part of the name (where a multivalue reference was given).

    field_name = get_field_name(field_name)

    # Build the XPath expression.

    parts = field_name.split(Constants.path_separator)
    new_parts = []
    for part in parts:
        path_parts = part.split(Constants.pair_separator)
        if len(path_parts) == 2:
            new_parts.append("*[position() = " + path_parts[1] + "]")
        else:
            new_parts.append(path_parts[0])
    return "/".join(new_parts)

# New functions.

libxsltmod.xsltRegisterExtModuleFunction("list-attribute", "http://www.boddie.org.uk/ns/xmltools/template", list_attribute)
libxsltmod.xsltRegisterExtModuleFunction("other-list-attributes", "http://www.boddie.org.uk/ns/xmltools/template", other_list_attributes)
libxsltmod.xsltRegisterExtModuleFunction("other-attributes", "http://www.boddie.org.uk/ns/xmltools/template", other_attributes)
libxsltmod.xsltRegisterExtModuleFunction("child-element", "http://www.boddie.org.uk/ns/xmltools/template", child_element)
libxsltmod.xsltRegisterExtModuleFunction("child-attribute", "http://www.boddie.org.uk/ns/xmltools/template", child_attribute)
libxsltmod.xsltRegisterExtModuleFunction("selector-name", "http://www.boddie.org.uk/ns/xmltools/template", selector_name)

# New names.

libxsltmod.xsltRegisterExtModuleFunction("this-element", "http://www.boddie.org.uk/ns/xmltools/template", this_element)
libxsltmod.xsltRegisterExtModuleFunction("this-attribute", "http://www.boddie.org.uk/ns/xmltools/template", this_attribute)
libxsltmod.xsltRegisterExtModuleFunction("new-attribute", "http://www.boddie.org.uk/ns/xmltools/template", new_attribute)
libxsltmod.xsltRegisterExtModuleFunction("other-elements", "http://www.boddie.org.uk/ns/xmltools/template", other_elements)

# Old names.

libxsltmod.xsltRegisterExtModuleFunction("this-position", "http://www.boddie.org.uk/ns/xmltools/template", this_element)
libxsltmod.xsltRegisterExtModuleFunction("field-name", "http://www.boddie.org.uk/ns/xmltools/template", this_attribute)
libxsltmod.xsltRegisterExtModuleFunction("new-field", "http://www.boddie.org.uk/ns/xmltools/template", new_attribute)
libxsltmod.xsltRegisterExtModuleFunction("other-field-names", "http://www.boddie.org.uk/ns/xmltools/template", other_elements)

# Old functions.

libxsltmod.xsltRegisterExtModuleFunction("multi-field-name", "http://www.boddie.org.uk/ns/xmltools/template", multi_field_name)
libxsltmod.xsltRegisterExtModuleFunction("other-multi-field-names", "http://www.boddie.org.uk/ns/xmltools/template", other_multi_field_names)

# Utility functions.

libxsltmod.xsltRegisterExtModuleFunction("range", "http://www.boddie.org.uk/ns/xmltools/template", xslforms_range)
libxsltmod.xsltRegisterExtModuleFunction("i18n", "http://www.boddie.org.uk/ns/xmltools/template", i18n)
libxsltmod.xsltRegisterExtModuleFunction("choice", "http://www.boddie.org.uk/ns/xmltools/template", choice)
libxsltmod.xsltRegisterExtModuleFunction("url-encode", "http://www.boddie.org.uk/ns/xmltools/template", url_encode)
libxsltmod.xsltRegisterExtModuleFunction("element-path", "http://www.boddie.org.uk/ns/xmltools/template", element_path)

def get_field_name(field_or_multi_name):
    return field_or_multi_name.split(Constants.multi_separator)[0]

# vim: tabstop=4 expandtab shiftwidth=4

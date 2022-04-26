#!/usr/bin/env python

"""
PyQt-compatible resources for use with WebStack.

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

import XSLForms.Prepare
import XSLForms.Resources.PyQtCommon
import XSLForms.Resources.WebResources
import WebStack.Generic
import os
import libxml2dom

class XSLFormsResource(XSLForms.Resources.WebResources.XSLFormsResource,
    XSLForms.Resources.PyQtCommon.PyQtCommonResource):

    """
    An XSLForms resource supporting PyQt-compatible Web applications for use
    with WebStack.
    """

    encoding = "utf-8"
    widget_resources = {}

    def __init__(self, design_identifier):
        self.factory = Factory()
        self.default_design = design_identifier

        # NOTE: Filenames extended by string concatenation.

        self.template_resources = {}
        self.init_resources = {}
        for design_identifier, design_name in self.design_resources.items():
            self.template_resources[design_identifier] = (design_name + "_template.xhtml", design_name + "_output.xsl")
            self.init_resources[design_identifier] = (design_name + "_template.xhtml", design_name + "_input.xsl")

        # Initialisation of connections - just a mapping from field names to
        # methods in the Web version.

        self.method_resources = {}
        for design_identifier, design_name in self.design_resources.items():
            design_path = self.prepare_design(design_identifier)
            design_doc = libxml2dom.parse(design_path)
            connections = {}
            for connection in design_doc.xpath("UI/connections/connection"):
                receiver = "".join([n.nodeValue for n in connection.xpath("receiver/text()")])
                if receiver == design_identifier:
                    sender = "".join([n.nodeValue for n in connection.xpath("sender/text()")])
                    slot = "".join([n.nodeValue for n in connection.xpath("slot/text()")])
                    slot = slot.split("(")[0]
                    connections[sender] = slot
            self.method_resources[design_identifier] = connections

        # Initialisation of template fragments.

        self.in_page_resources = {}
        for widget_identifier, (design_name, fragment_id) in self.widget_resources.items():
            self.in_page_resources[widget_identifier] = (design_name + "_output.xsl", fragment_id)

        # Refresh status - avoiding multiple refresh calls.

        self._refreshed = 0

    # Resource methods.

    def prepare_output(self, design_identifier):

        """
        Prepare the output stylesheets using the given 'design_identifier' to
        indicate which templates and stylesheets are to be employed in the
        production of output from the resource.

        The 'design_identifier' is used as a key to the 'design_resources' and
        'template_resources' dictionary attributes.

        Return the full path to the output stylesheet for use with 'send_output'
        or 'get_result'.
        """

        design_path = self.prepare_design(design_identifier)
        template_filename, output_filename = self.template_resources[design_identifier]
        output_path = os.path.abspath(os.path.join(self.resource_dir, output_filename))
        template_path = os.path.abspath(os.path.join(self.resource_dir, template_filename))
        XSLForms.Prepare.ensure_qt_template(design_path, template_path)
        XSLForms.Prepare.ensure_stylesheet(template_path, output_path)
        return output_path

    # PyQt compatibility methods.

    def get_document(self, document_identifier):
        return libxml2dom.parse(self.prepare_document(document_identifier))

    def prepare_widget(self, design_identifier, widget_identifier, parent=None):
        fragment_name, widget_name = self.widget_resources[widget_identifier]
        element = UINode(self.doc._node.ownerDocument.createElement(widget_name))

        # NOTE: Creating an element which may not be appropriate.

        element._node.appendChild(self.doc._node.ownerDocument.createElement(widget_name + "_value"))
        return element

    def child(self, name):
        return self.doc.child(name)

    def sender(self):
        return self._sender

    # PyQt structural methods.

    def form_init(self):

        "Initialise a newly-created form."

        raise NotImplementedError, "form_init"

    def form_populate(self):

        "Populate the values in a form."

        raise NotImplementedError, "form_populate"

    def form_refresh(self):

        "Refresh the form."

        raise NotImplementedError, "form_refresh"

    def request_refresh(self, *args, **kw):

        "Request a refresh of the form."

        if not self._refreshed:
            self._refreshed = 1
            self.form_refresh(*args, **kw)

    # Standard XSLFormsResource method, overridden to handle presentation.

    def respond_to_form(self, trans, form):

        """
        Respond to the request described by the given transaction 'trans', using
        the given 'form' object to conveniently retrieve field (request
        parameter) information and structured form information (as DOM-style XML
        documents).
        """

        self._refreshed = 0

        # Ensure the presence of the template.

        self.prepare_output(self.default_design)

        # Remember the document since it is accessed independently elsewhere.

        doc = form.get_document(self.default_design)
        if doc is None:
            doc = form.new_document(self.default_design)
            doc = self._get_initialised_form(doc)
            self.doc = UINode(doc.xpath("*")[0])
            self.form_init()
        else:
            doc = self._get_initialised_form(doc)
            self.doc = UINode(doc.xpath("*")[0])

        self.form_populate()

        # Updates happen here.

        form.set_document(self.default_design, doc)
        selectors = form.get_selectors()
        connections = self.method_resources[self.default_design]
        for selector_name, selector_values in selectors.items():
            if connections.has_key(selector_name):
                slot = connections[selector_name]
                if hasattr(self, slot):

                    # Initialise the sender.

                    for selector_value in selector_values:
                        # NOTE: Fake a special element to simulate the Qt widget hierarchy.
                        # NOTE: We could instead have set the underlying annotations for
                        # NOTE: selector-field differently, but that would be more work.
                        # NOTE: An alternative which works in certain cases is a new
                        # NOTE: attribute whose node is retained.
                        _sender = self.doc._node.ownerDocument.createElement("_sender")
                        self._sender = UINode(selector_value.appendChild(_sender))
                        getattr(self, slot)()

        # Consistency is ensured and filtering enforced.

        self.request_refresh()
        #print self.doc._node.toString("iso-8859-1")

        # Output is produced.

        trans.set_content_type(WebStack.Generic.ContentType("application/xhtml+xml", self.encoding))
        design_xsl = self.prepare_output(self.default_design)
        self.send_output(trans, [design_xsl], doc._node)

    def _get_initialised_form(self, doc):
        input_xsl = self.prepare_initialiser(self.default_design, init_enumerations=0)
        return self.get_result([input_xsl], doc)

class UINode:

    "A PyQt widget tree emulation node."

    def __init__(self, node):
        self._node = node

    def add(self, node):
        self._node.appendChild(node._node)

    def child(self, name):
        nodes = self._node.xpath(name)
        if len(nodes) > 0:
            return UINode(nodes[0])
        else:
            return None

    def children(self):
        return [UINode(node) for node in self._node.childNodes]

    def count(self):
        return len(self._node.childNodes)

    def currentText(self):
        return self._node.getAttribute("value")

    def currentItem(self):
        found = self._node.xpath("*[@value=current()/@value]")
        if found:
            return int(found.xpath("count(preceding-sibling::*)"))
        else:
            return 0

    def deleteLater(self):
        pass

    def insertItem(self, item, position=-1):
        # NOTE: Names invented rather than being extracted from the schema.
        new_element = self._node.ownerDocument.createElement(self._node.localName + "_enum")
        new_element.setAttribute("value", item)
        if position == -1:
            self._node.appendChild(new_element)
        else:
            elements = self._node.xpath("*")
            if position < len(elements) - 1:
                self._node.insertBefore(new_element, elements[position])
            else:
                self._node.appendChild(new_element)

    def layout(self):
        return self

    def parent(self):
        return UINode(self._node.parentNode)

    def removeItem(self, item):
        elements = self._node.xpath("*")
        if item < len(elements):
            self._node.removeChild(elements[item])

    def remove(self, item):
        self._node.removeChild(item._node)

    def setCurrentItem(self, index):
        pass # NOTE: Not implemented yet!

    def show(self):
        pass

class Factory:

    "A widget factory helper class."

    def connect(self, widget, obj):

        """
        Connection is done all at once by mapping field names to method names in
        the resource object.
        """

        pass

    def find_widgets(self, widget, name):

        """
        Find within the given 'widget' (a DOM node) the widget with the given
        'name'.
        """

        return [UINode(node) for node in widget.doc._node.getElementsByTagName(name)]

# vim: tabstop=4 expandtab shiftwidth=4

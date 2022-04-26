#!/usr/bin/env python

"""
Resources for use with PyQt.

Copyright (C) 2005 Paul Boddie <paul@boddie.org.uk>

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
import qt, qtui, qtxmldom
import os

class XSLFormsResource(XSLForms.Resources.PyQtCommon.PyQtCommonResource):

    "An XSLForms resource for use with PyQt."

    widget_resources = {}

    def __init__(self, design_identifier):
        self.factory = Factory(self.prepare_design(design_identifier))

    def get_document(self, document_identifier):
        return qtxmldom.parse(self.prepare_document(document_identifier))

    def prepare_widget(self, design_identifier, widget_identifier, parent=None):
        design_path = self.prepare_design(design_identifier)
        fragment_name, widget_name = self.widget_resources[widget_identifier]
        fragment_path = os.path.abspath(os.path.join(self.resource_dir, fragment_name))
        XSLForms.Prepare.ensure_qt_fragment(design_path, fragment_path, widget_name)
        return qtui.QWidgetFactory.create(fragment_path, None, parent)

    def request_refresh(self, *kw, **args):
        self.form_refresh(*kw, **args)

class Factory:

    "A widget factory helper class."

    def __init__(self, ui_filename):
        self.ui_filename = ui_filename
        self.ui_doc = qtxmldom.parse(ui_filename)

    def connect(self, widget, obj):

        for connection in self.ui_doc.getElementsByTagName("connection"):
            sender_name = self.get_text(connection.getElementsByTagName("sender")[0]).encode("utf-8")
            signal_name = self.get_text(connection.getElementsByTagName("signal")[0]).encode("utf-8")
            slot_name = self.get_text(connection.getElementsByTagName("slot")[0]).encode("utf-8")

            if widget.name() == sender_name:
                senders = [widget]
            else:
                senders = self.find_widgets(widget, sender_name)

            slot = slot_name.split("(")[0]
            if hasattr(obj, slot):
                signal = qt.SIGNAL(signal_name)
                for sender in senders:
                    qt.QObject.connect(sender, signal, getattr(obj, slot))

    def get_text(self, node):
        node.normalize()
        return node.childNodes[0].nodeValue

    def find_widgets(self, widget, name):
        widgets = []
        found = widget.child(name)
        if found:
            widgets.append(found)
        for child in widget.children() or []:
            widgets += self.find_widgets(child, name)
        return widgets

# vim: tabstop=4 expandtab shiftwidth=4

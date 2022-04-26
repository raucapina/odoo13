#!/usr/bin/env python

"""
Common resource class functionality for PyQt-related applications.

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

import os
from XSLForms.Resources.Common import CommonResource

class PyQtCommonResource(CommonResource):

    "Common PyQt-compatible resource methods."

    design_resources = {}

    def get_document(self, document_identifier):

        """
        Return a DOM-style document retrieved using the given
        'document_identifier'.

        Each implementation is free to choose its own DOM library.
        """

        raise NotImplementedError, "get_document"

    def get_elements(self, document_identifier):
        doc = self.get_document(document_identifier)

        # NOTE: Using special suffix.

        return doc.getElementsByTagName(document_identifier + "-enum")

    def prepare_design(self, design_identifier):
        filename = self.design_resources[design_identifier]
        return os.path.abspath(os.path.join(self.resource_dir, filename))

    def populate_list(self, field, elements):

        "Populate the given 'field' using a list of DOM 'elements'."

        current_text = field.currentText()
        while field.count() > 0:
            field.removeItem(0)
        item = 0
        set = 0
        for element in elements:
            text = element.getAttribute("value")
            field.insertItem(text)
            if text == current_text:
                field.setCurrentItem(item)
                set = 1
            item += 1
        if not set:
            field.setCurrentItem(0)

    def reset_collection(self, field):

        "Empty the given collection 'field'."

        layout = field.layout()
        for child in field.children():
            if child is not layout:
                layout.remove(child)
                child.deleteLater()

# vim: tabstop=4 expandtab shiftwidth=4

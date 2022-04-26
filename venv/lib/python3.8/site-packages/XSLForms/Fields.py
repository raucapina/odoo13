#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

"""
Interpretation of field collections from sources such as HTTP request parameter
dictionaries.

Copyright (C) 2005, 2006, 2007 Paul Boddie <paul@boddie.org.uk>

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

--------

Classes which process field collections, producing instance documents. Each
field entry consists of a field name mapped to a string value, where the field
name may have the following formats:

    /name1$n1/name2
    /name1$n1/name2$n2/name3
    /name1$n1/name2$n2/name3$n3/name4
    ...

The indexes n1, n2, n3, ... indicate the position of elements (starting from 1)
in the entire element list, whose elements may have different names. For
example:

    /zoo$1/name
    /zoo$1/cage$1/name
    /zoo$1/cage$2/name
    /zoo$1/funding$3/contributor$1/name

Where multiple values can be collected for a given field, the following notation
is employed:

    /package$1/categories$1/category$$value

Some fields may contain the "=" string. This string is reserved and all text
following it is meant to specify a path into a particular document. For example:

    _action_add_animal=/zoo$1/cage$2
"""

import Constants
import libxml2dom
from xml.dom import EMPTY_NAMESPACE

class FieldsError(Exception):
    pass

class FieldProcessor:

    """
    A class which converts fields in the documented form to XML
    instance documents.
    """

    def __init__(self, encoding="utf-8", values_are_lists=0):

        """
        Initialise the fields processor with the given 'encoding',
        which is optional and which only applies to field data in
        Python string form (and not Unicode objects).

        If the optional 'values_are_lists' parameter is set to true
        then each actual field value will be obtained by taking the
        first element from each supplied field value.
        """

        self.encoding = encoding
        self.values_are_lists = values_are_lists

    def complete_documents(self, documents, fields):

        """
        Complete the given 'documents' using the 'fields' items list.
        """

        for field, value in fields:

            # Ignore selectors.

            if field.find(Constants.selector_indicator) != -1:
                continue

            model_name, components = self._get_model_name_and_components(field)
            if model_name is None:
                continue

            # Get a new instance document if none has been made for the
            # model.

            if not documents.has_key(model_name):
                documents[model_name] = self.new_instance(model_name)
            node = documents[model_name]

            # Traverse the components within the instance.

            for component in components:
                t = component.split(Constants.pair_separator)
                if len(t) == 1:

                    # Convert from lists if necessary.

                    if self.values_are_lists:
                        value = value[0]

                    # Convert the value to Unicode if necessary.

                    if type(value) == type(""):
                        value = unicode(value, encoding=self.encoding)

                    # Remove CR characters.

                    node.setAttributeNS(EMPTY_NAMESPACE, t[0], value.replace("\r", ""))
                    break

                elif len(t) == 2:

                    # Convert from one-based indexing (the position()
                    # function) to zero-based indexing.

                    name, index = t[0], int(t[1]) - 1
                    if index < 0:
                        break
                    try:
                        node = self._enter_element(node, name, index)
                    except FieldsError, exc:
                        raise FieldsError, "In field '%s', name '%s' and index '%s' could not be added, since '%s' was found." % (
                            field, name, index, exc.args[0])

                elif len(t) == 3 and t[1] == "":

                    # Multivalued fields.

                    if not self.values_are_lists:
                        values = [value]
                    else:
                        values = value

                    name = t[0]
                    for subvalue in values:
                        subnode = self._append_element(node, name)

                        # Convert the value to Unicode if necessary.

                        if type(subvalue) == type(""):
                            subvalue = unicode(subvalue, encoding=self.encoding)

                        # Remove CR characters.

                        subnode.setAttributeNS(EMPTY_NAMESPACE, t[2], subvalue.replace("\r", ""))

    def complete_selectors(self, selectors, fields, documents, create):

        """
        Fill in the given 'selectors' dictionary using the given
        'fields' so that it contains mappings from selector names to
        parts of the specified 'documents'. If 'create' is set to a
        true value, selected elements will be created if not already
        present; otherwise, ignore such selectors.
        """

        for field, value in fields:

            # Process selectors only.

            selector_components = field.split(Constants.selector_indicator)
            if len(selector_components) < 2:
                continue

            # Get the selector name and path.
            # Note that the joining of the components uses the separator,
            # but the separator really should not exist in the path.

            selector_name = selector_components[0]
            path = Constants.selector_indicator.join(selector_components[1:])

            model_name, components = self._get_model_name_and_components(path)
            if model_name is None:
                continue

            # Go to the instance element.

            if not documents.has_key(model_name) or documents[model_name] is None:
                continue
 
            node = documents[model_name]

            # Traverse the path to find the part of the document to be
            # selected.

            for component in components:
                t = component.split(Constants.pair_separator)
                if len(t) == 1:

                    # Select attribute.

                    node = node.getAttributeNodeNS(EMPTY_NAMESPACE, t[0])
                    break

                elif len(t) == 2:

                    # Convert from one-based indexing (the position() function)
                    # to zero-based indexing.

                    name, index = t[0], int(t[1]) - 1
                    if index < 0:
                        break

                    # If create is set, create selected elements.

                    if create:
                        try:
                            node = self._enter_element(node, name, index)
                        except FieldsError, exc:
                            raise FieldsError, "In field '%s', name '%s' and index '%s' could not be added, since '%s' was found." % (
                                field, name, index, exc.args[0])

                    # Where a node cannot be found, do not create a selector.

                    else:
                        node = self._find_element(node, name, index)
                        if node is None:
                            break

            if not selectors.has_key(selector_name):
                selectors[selector_name] = []
            if node is not None:
                selectors[selector_name].append(node)

    def _append_element(self, node, name):

        """
        Within 'node' append an element with the given 'name'.
        """

        new_node = node.ownerDocument.createElementNS(EMPTY_NAMESPACE, name)
        node.appendChild(new_node)
        return new_node

    def _enter_element(self, node, name, index):

        """
        From 'node' enter the element with the given 'name' at the
        given 'index' position amongst the child elements. Create
        missing child elements if necessary.
        """

        self._ensure_elements(node, index)

        elements = node.xpath("*")
        if elements[index].localName == "placeholder":
            new_node = node.ownerDocument.createElementNS(EMPTY_NAMESPACE, name)
            node.replaceChild(new_node, elements[index])
        else:
            new_node = elements[index]
            if new_node.localName != name:
                raise FieldsError, (new_node.localName, name, elements, index)

        # Enter the newly-created element.

        return new_node

    def _find_element(self, node, name, index):

        """
        From 'node' find the element with the given 'name' at the
        given 'index' position amongst the child elements. Return
        None if no such element exists.
        """

        elements = node.xpath("*")
        try:
            new_node = elements[index]
            if new_node.localName != name:
                return None
        except IndexError:
            return None
        return new_node

    def _get_model_name_and_components(self, field):

        """
        From 'field', return the model name and components which
        describe the path within the instance document associated
        with that model.
        """

        # Get the components of the field name.
        # Example:  /name1#n1/name2#n2/name3
        # Expected: ['', 'name1#n1', 'name2#n2', 'name3']

        components = field.split(Constants.path_separator)
        if len(components) < 2:
            return None, None

        # Extract the model name from the top-level element
        # specification.
        # Expected: ['name1', 'n1']

        model_name_and_index = components[1].split(Constants.pair_separator)
        if len(model_name_and_index) != 2:
            return None, None

        # Expected: 'name1', ['', 'name1#n1', 'name2#n2', 'name3']

        return model_name_and_index[0], components[1:]

    def _ensure_elements(self, document, index):

        """
        In the given 'document', extend the child elements list
        so that a node can be stored at the given 'index'.
        """

        elements = document.xpath("*")
        i = len(elements)
        while i <= index:
            new_node = document.ownerDocument.createElementNS(EMPTY_NAMESPACE, "placeholder")
            document.appendChild(new_node)
            i += 1

    def make_documents(self, fields):

        """
        Make a dictionary mapping model names to new documents prepared
        from the given 'fields' dictionary.
        """

        documents = {}
        self.complete_documents(documents, fields)

        # Fix the dictionary to return the actual document root.

        for model_name, instance_root in documents.items():
            documents[model_name] = instance_root
        return documents

    def get_selectors(self, fields, documents, create=0):

        """
        Get a dictionary containing a mapping of selector names to
        selected parts of the given 'documents'. If 'create' is set
        to a true value, selected elements will be created if not
        already present.
        """

        selectors = {}
        self.complete_selectors(selectors, fields, documents, create)
        return selectors

    def new_instance(self, name):

        "Return an instance root of the given 'name' in a new document."

        return libxml2dom.createDocument(EMPTY_NAMESPACE, name, None)

    # An alias for the older method name.

    new_document = new_instance

# NOTE: Legacy name exposure.

Fields = FieldProcessor

class Form(FieldProcessor):

    "A collection of documents processed from form fields."

    def __init__(self, *args, **kw):

        """
        Initialise the form data container with the general 'args' and 'kw'
        parameters.
        """

        FieldProcessor.__init__(self, *args, **kw)
        self.parameters = {}
        self.documents = {}

    def set_parameters(self, parameters):

        "Set the request 'parameters' (or fields) in the container."

        self.parameters = parameters
        self.documents = self.make_documents(self.parameters.items())

    def get_parameters(self):

        """
        Get the request parameters (or fields) from the container. Note that
        these parameters comprise the raw form field values submitted in a
        request rather than the structured form data.

        Return a dictionary mapping parameter names to values.
        """

        return self.parameters

    def get_documents(self):

        """
        Get the form data documents from the container, returning a dictionary
        mapping document names to DOM-style document objects.
        """

        return self.documents

    def get_document(self, name):

        """
        Get the form data document with the given 'name' from the container,
        returning a DOM-style document object if such a document exists, or None
        if no such document can be found.
        """

        return self.documents.get(name)

    def get_selectors(self, create=0):

        """
        Get the form data selectors from the container, returning a dictionary
        mapping selector names to collections of selected elements. If 'create'
        is set to a true value (unlike the default), the selected elements will
        be created in the form data document if not already present.
        """

        return FieldProcessor.get_selectors(self, self.parameters.items(), self.documents, create)

    def get_selector(self, name, create=0):

        """
        Get the form data selectors for the given 'name', returning a collection
        of selected elements. If 'create' is set to a true value (unlike the
        default), the selected elements will be created in the form data
        document if not already present.
        """

        parameters = []
        for parameter_name, value in parameters.items():
            if parameter_name.startswith(name + Constants.selector_indicator):
                parameters.append((parameter_name, value))
        return FieldProcessor.get_selectors(self, parameters, self.documents, create)

    def new_instance(self, name):

        """
        Make a new document with the given 'name', storing it in the container
        and returning the document.
        """

        doc = FieldProcessor.new_instance(self, name)
        self.documents[name] = doc
        return doc

    # An alias for the older method name.

    new_document = new_instance

    def set_document(self, name, doc):

        """
        Store in the container under the given 'name' the supplied document
        'doc'.
        """

        self.documents[name] = doc

if __name__ == "__main__":

    items = [
            ("_action_update", "Some value"),
            ("_action_delete=/zoo$1/cage$2", "Some value"),
            ("_action_nasty=/zoo$1/cage$3", "Some value"),
            ("/actions$1/update$1/selected", "Some value"), # Not actually used in output documents or input.
            ("/zoo$1/name", "The Zoo æøå"),
            ("/zoo$1/cage$1/name", "reptiles"),
            ("/zoo$1/cage$1/capacity", "5"),
            ("/zoo$1/cage$1/animal$1/name", "Monty"),
            ("/zoo$1/cage$1/animal$1/species$1/name", "Python"),
            ("/zoo$1/cage$1/animal$1/property$2/name", "texture"),
            ("/zoo$1/cage$1/animal$1/property$2/value", "scaled"),
            ("/zoo$1/cage$1/animal$1/property$3/name", "length"),
            ("/zoo$1/cage$1/animal$1/property$3/value", "5m"),
            ("/zoo$1/cage$1/animal$2/name", "Vincent"),
            ("/zoo$1/cage$1/animal$2/species$1/name", "Lizard"),
            ("/zoo$1/cage$1/animal$2/property$2/name", "colour"),
            ("/zoo$1/cage$1/animal$2/property$2/value", "variable"),
            ("/zoo$1/cage$1/animal$2/property$3/name", "length"),
            ("/zoo$1/cage$1/animal$2/property$3/value", "1m"),
            ("/zoo$1/cage$2/name", "mammals"),
            ("/zoo$1/cage$2/capacity", "25"),
            ("/zoo$1/cage$2/animal$1/name", "Simon"),
            ("/zoo$1/cage$2/animal$1/species$1/name", "Giraffe"),
            ("/zoo$1/cage$2/animal$2/name", "Leonard"),
            ("/zoo$1/cage$2/animal$2/species$1/name", "Lion"),
            ("/zoo$1/cage$2/animal$2/property$2/name", "danger"),
            ("/zoo$1/cage$2/animal$2/property$2/value", "high"),
            ("/zoo$1/funding$3/type", "private"),
            ("/zoo$1/funding$3/contributor$1/name", "Animal Corporation"),
            ("/zoo$1/funding$3/contributor$1/amount", "543210.987"),
            ("/zoo$1/funding$3/contributor$1/industry$$type", "animals")
        ]

    import time
    import sys, cmdsyntax

    # Find the documents.

    syntax = cmdsyntax.Syntax("""
        --plain-output=OUTPUT_FILE
        --instance-name=NAME
        """)

    syntax_matches = syntax.get_args(sys.argv[1:])

    try:
        args = syntax_matches[0]
    except IndexError:
        print syntax.syntax
        sys.exit(1)

    # Create an object to interpret the test data.

    fields = FieldProcessor("iso-8859-1")

    t = time.time()
    documents = fields.make_documents(items)
    print "Building time", time.time() - t

    t = time.time()
    documents[args["instance-name"]].toStream(stream=open(args["plain-output"], "wb"), encoding="utf-8")
    print "Prettyprinting time", time.time() - t

    print "Selectors", repr(fields.get_selectors(items, documents))

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

"""
A list of tuples to XML document converter.

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

import libxml2dom
from UserDict import UserDict

class OrderedDict(UserDict):

    "A dictionary with keys in the order in which they were given."

    def __init__(self, *args):
        UserDict.__init__(self, *args)
        self._keys = self.data.keys()

    def __setitem__(self, key, value):
        UserDict.__setitem__(self, key, value)
        if key not in self._keys:
            self._keys.append(key)

    def __delitem__(self, key):
        UserDict.__delitem__(self, key)
        del self._keys[key]

    def keys(self):
        return self._keys

    def items(self):
        l = []
        for key in self._keys:
            l.append((key, self.data[key]))
        return l

    def values(self):
        return [value for key, value in self.items()]

class Converter:
    def __init__(self, ns=None, prefix="", doc=None, root=None):
        self.ns = ns
        self.prefix = prefix
        if doc is not None:
            self.doc = doc
        else:
            self.doc = libxml2dom.createDocument(ns, prefix+"table", None)
        if root is not None:
            self.root = root
        else:
            self.root = self.doc.xpath("*")[0]

        # Remember the last row element.

        self.last_row_element = None

    def add_rows(self, rows):
        for row in rows:
            self.add_row(row)

    def add_row(self, row, index=-1, row_element_name="row", use_key_as_element_name=0):
        self.last_row_element = self.doc.createElementNS(self.ns, self.prefix+row_element_name)
        if index == -1:
            self.root.appendChild(self.last_row_element)
        else:
            self.root.insertBefore(self.last_row_element, self.root.xpath("*[%s]" % (index + 1))[0])

        # Permit dictionaries.

        if hasattr(row, "items"):
            for name, value in row.items():
                if use_key_as_element_name:
                    column_element = self.doc.createElementNS(self.ns, self.prefix+unicode(name))
                else:
                    column_element = self.doc.createElementNS(self.ns, self.prefix+"column")
                    column_element.setAttributeNS(self.ns, self.prefix+"name", unicode(name))
                self.last_row_element.appendChild(column_element)
                text = self.doc.createTextNode(unicode(value))
                column_element.appendChild(text)

        # As well as sequences.

        else:
            for column in row:
                column_element = self.doc.createElementNS(self.ns, self.prefix+"column")
                self.last_row_element.appendChild(column_element)
                text = self.doc.createTextNode(unicode(column))
                column_element.appendChild(text)

    def last_row(self):
        if self.last_row_element is not None:
            return Converter(self.ns, self.prefix, self.doc, self.last_row_element)
        else:
            return None

if __name__ == "__main__":
    from rdflib.TripleStore import TripleStore
    import sys
    s = TripleStore()
    s.load(sys.argv[1])
    converter = Converter()
    converter.add_rows(s.triples((None, None, None)))
    libxml2dom.toStream(converter.doc, sys.stdout)

# vim: tabstop=4 expandtab shiftwidth=4

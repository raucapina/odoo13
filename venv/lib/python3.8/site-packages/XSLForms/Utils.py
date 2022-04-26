#!/usr/bin/env python

"""
Utility functions for XSLForms documents.

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

def add_elements(positions, *element_names):

    """
    At the specified 'positions' in a document, add a new element using the
    first of the given 'element_names' inside any subsequent element named in
    the 'element_names' list, in turn creating new parent elements for each
    element name found.
    """

    if not positions:
        return
    reversed_element_names = list(element_names)[:]
    reversed_element_names.reverse()
    for position in positions:
        element = position
        for element_name in reversed_element_names[:-1]:
            found_elements = element.xpath(element_name)
            if not found_elements:
                new_element = element.ownerDocument.createElementNS(None, element_name)
                element.appendChild(new_element)
            else:
                new_element = found_elements[0]
            element = new_element
        new_element = element.ownerDocument.createElementNS(None, reversed_element_names[-1])
        element.appendChild(new_element)

def remove_elements(positions):

    """
    Remove the elements located at the given 'positions'.
    """

    if not positions:
        return
    for position in positions:
        position.parentNode.removeChild(position)

# vim: tabstop=4 expandtab shiftwidth=4

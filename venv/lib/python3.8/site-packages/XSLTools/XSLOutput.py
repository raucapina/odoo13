#!/usr/bin/env python

"""
XSL output classes and functions.

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
"""

# NOTE: Make this use other XSLT implementations, too.

# Try the conventional import first.

try:
    import libxsltmod
except ImportError:
    from libxmlmods import libxsltmod

import libxml2dom
import os, tempfile

class OutputError(Exception):
    pass

class Processor:

    """
    A handler which can prepare output for an XMLTools2 template.
    """

    def __init__(self, filenames, references=None, parameters=None, expressions=None):

        """
        Initialise the handler with the 'filenames' of stylesheets producing the
        final output, a 'references' dictionary indicating related stylesheets.
        Additional 'parameters' may be specified as a dictionary whose values
        are converted to string values; additional 'expressions' may also be
        specified as a dictionary - such expressions are actually evaluated in
        stylesheet.
        """

        self.references = references or {}
        self.parameters = parameters or {}
        self.expressions = expressions or {}

        # Remember the stylesheet documents.

        self.stylesheets = []
        for filename in filenames:
            #doc = libxml2dom.macrolib.parseFile(filename)
            #self.stylesheets.append(libxsltmod.xsltParseStylesheetDoc(doc))
            self.stylesheets.append(libxsltmod.xsltParseStylesheetFile(filename))

    def __del__(self):

        """
        Tidy up the stylesheet documents.
        """

        for stylesheet in self.stylesheets:
            libxsltmod.xsltFreeStylesheet(stylesheet)

    def send_output(self, stream, encoding, document):

        """
        Send output to the given 'stream' using the given output encoding for
        the given 'document'.
        """

        # Where an encoding is specified, get an libxml2dom document and
        # serialise it.
        # NOTE: This is not satisfactory where indented output is desired.

        if encoding:
            result = self.get_result(document)
            stream.write(result.toString(encoding))
            return

        # Otherwise, get a libxml2mod document and use the libxsltmod API.

        result = self._get_result(document)
        if result is None:
            raise OutputError, "Transformation failed."

        # Attempt to get the correctly formatted document.

        if hasattr(stream, "fileno"):
            stream.flush()
            fd = stream.fileno()
            str_result = libxsltmod.xsltSaveResultToFd(fd, result, self.stylesheets[-1])
        else:
            fd, name = tempfile.mkstemp()
            str_result = libxsltmod.xsltSaveResultToFd(fd, result, self.stylesheets[-1])
            f = os.fdopen(fd)
            f.seek(0)
            stream.write(f.read())
            f.close()
            os.remove(name)

    def get_result(self, document):

        """
        Return a transformed document produced from the object's stylesheets and
        the given 'document'.
        """

        result = self._get_result(document)

        if result is not None:
            return libxml2dom.getDOMImplementation().adoptDocument(result)
        else:
            raise OutputError, "Transformation failed."

    def _get_result(self, document):

        """
        Return a transformation of the given 'document'.
        """

        if hasattr(document, "as_native_node"):
            document = document.as_native_node()

        # Transform the localised instance into the final output.

        parameters = {}
        for name, reference in self.references.items():
            parameters[name.encode("utf-8")] = ("document('%s')" % self._quote(reference)).encode("utf-8")
        for name, parameter in self.parameters.items():
            parameters[name.encode("utf-8")] = ("'%s'" % self._quote(parameter)).encode("utf-8")
        for name, parameter in self.expressions.items():
            parameters[name.encode("utf-8")] = self._quote(parameter).encode("utf-8")

        last_result = document
        for stylesheet in self.stylesheets:
            result = libxsltmod.xsltApplyStylesheet(stylesheet, last_result, parameters)
            if last_result is not None:
                last_result = result
            else:
                raise OutputError, "Transformation failed."

        return result

    def _quote(self, s):

        "Make the given parameter string 's' palatable for libxslt."

        return s.replace("'", "%27")

# vim: tabstop=4 expandtab shiftwidth=4

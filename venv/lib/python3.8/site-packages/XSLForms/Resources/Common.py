#!/usr/bin/env python

"""
Common resource class functionality.

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

class CommonResource:

    "Common resource methods."

    document_resources = {}
    resource_dir = None

    def prepare_document(self, document_identifier):

        """
        Prepare a document using the given 'document_identifier'.

        Return the full path of the document for use either as the source
        document or as a reference with 'send_output' or 'get_result'.
        """

        filename = self.document_resources[document_identifier]
        return os.path.abspath(os.path.join(self.resource_dir, filename))

# vim: tabstop=4 expandtab shiftwidth=4

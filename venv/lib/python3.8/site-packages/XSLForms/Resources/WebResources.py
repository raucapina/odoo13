#!/usr/bin/env python

"""
Resources for use with WebStack.

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

import WebStack.Generic
import XSLForms.Fields
import XSLForms.Prepare
import XSLForms.Output
import XSLForms.Resources.Common
from XSLTools import XSLOutput
import os

class XSLFormsResource(XSLForms.Resources.Common.CommonResource):

    """
    A generic XSLForms resource for use with WebStack.

    When overriding this class, define the following attributes appropriately:

      * template_resources    - a dictionary mapping output identifiers to
                                (template_filename, output_filename) tuples,
                                indicating the template and stylesheet filenames
                                to be employed

      * in_page_resources     - a dictionary mapping fragment identifiers to
                                (output_identifier, output_filename,
                                node_identifier) tuples, indicating the output
                                identifier for which the fragment applies, the
                                stylesheet filename to be employed, along with
                                the node identifier used in the original
                                template and output documents to mark a region
                                of those documents as the fragment to be updated
                                upon "in-page" requests

      * init_resources        - a dictionary mapping initialiser/input
                                identifiers to (template_filename,
                                input_filename) tuples, indicating the template
                                and initialiser/input stylesheet filenames to be
                                employed
                                
      * transform_resources   - a dictionary mapping transform identifiers to
                                lists of stylesheet filenames for use with the
                                transformation methods

      * document_resources    - a dictionary mapping document identifiers to
                                single filenames for use as source documents or
                                as references with the transformation methods

      * resource_dir          - the absolute path of the directory in which
                                stylesheet resources are to reside

    All filenames shall be simple leafnames for files residing in the resource's
    special resource directory 'resource_dir'.

    The following attributes may also be specified:

      * path_encoding         - the assumed encoding of characters in request
                                paths

      * encoding              - the assumed encoding of characters in request
                                bodies
    """

    #path_encoding = "utf-8"
    #encoding = "utf-8"
    template_resources = {}
    in_page_resources = {}
    init_resources = {}
    transform_resources = {}

    def clean_parameters(self, parameters):

        """
        Workaround stray zero value characters from Konqueror in XMLHttpRequest
        communications.
        """

        for name, values in parameters.items():
            new_values = []
            for value in values:
                if value.endswith("\x00"):
                    new_values.append(value[:-1])
                else:
                    new_values.append(value)
            parameters[name] = new_values

    def prepare_output(self, output_identifier):

        """
        Prepare the output stylesheets using the given 'output_identifier' to
        indicate which templates and stylesheets are to be employed in the
        production of output from the resource.

        The 'output_identifier' is used as a key to the 'template_resources'
        dictionary attribute.

        Return the full path to the output stylesheet for use with 'send_output'
        or 'get_result'.
        """

        template_path, output_path = prepare_output(self, output_identifier)
        return output_path

    def prepare_fragment(self, fragment_identifier):

        """
        Prepare the output stylesheets for the given 'fragment_identifier',
        indicating which templates and stylesheets are to be employed in the
        production of output from the resource.

        The 'fragment_identifier' is used as a key to the 'in_page_resources'
        dictionary attribute which in turn obtains an 'output_identifier', which
        is used as a key to the 'template_resources' dictionary attribute.

        Return the full path to the output stylesheet for use with 'send_output'
        or 'get_result'.
        """

        template_path, fragment_path = prepare_fragment(self, fragment_identifier)
        return fragment_path

    def prepare_parameters(self, parameters):

        """
        Prepare the stylesheet parameters from the given request 'parameters'.
        This is most useful when preparing fragments for in-page update output.
        """

        element_path = parameters.get("element-path", [""])[0]
        if element_path:
            return {"element-path" : element_path}
        else:
            return {}

    def send_output(self, trans, stylesheet_filenames, document, stylesheet_parameters=None,
        stylesheet_expressions=None, references=None):

        """
        Send the output from the resource to the user employing the transaction
        'trans', stylesheets having the given 'stylesheet_filenames', the
        'document' upon which the output will be based, the optional parameters
        as defined in the 'stylesheet_parameters' dictionary, the optional
        expressions are defined in the 'stylesheet_expressions' dictionary, and
        the optional 'references' to external documents.
        """

        # Sanity check for the filenames list.

        if isinstance(stylesheet_filenames, str) or isinstance(stylesheet_filenames, unicode):
            raise ValueError, stylesheet_filenames

        proc = XSLOutput.Processor(stylesheet_filenames, parameters=stylesheet_parameters,
            expressions=stylesheet_expressions, references=references)
        proc.send_output(trans.get_response_stream(), trans.get_response_stream_encoding(),
            document)

    def get_result(self, stylesheet_filenames, document, stylesheet_parameters=None,
        stylesheet_expressions=None, references=None):

        """
        Get the result of applying a transformation using stylesheets with the
        given 'stylesheet_filenames', the 'document' upon which the result will
        be based, the optional parameters as defined in the
        'stylesheet_parameters' dictionary, the optional parameters as defined
        in the 'stylesheet_parameters' dictionary and the optional 'references'
        to external documents.
        """

        # Sanity check for the filenames list.

        if isinstance(stylesheet_filenames, str) or isinstance(stylesheet_filenames, unicode):
            raise ValueError, stylesheet_filenames

        proc = XSLOutput.Processor(stylesheet_filenames, parameters=stylesheet_parameters,
            expressions=stylesheet_expressions, references=references)
        return proc.get_result(document)

    def prepare_initialiser(self, input_identifier, init_enumerations=1):

        """
        Prepare an initialiser/input transformation using the given
        'input_identifier'. The optional 'init_enumerations' (defaulting to
        true) may be used to indicate whether enumerations are to be initialised
        from external documents.

        Return the full path to the input stylesheet for use with 'send_output'
        or 'get_result'.
        """

        template_path, input_path = prepare_initialiser(self, input_identifier, init_enumerations)
        return input_path

    def prepare_transform(self, transform_identifier):

        """
        Prepare a transformation using the given 'transform_identifier'.

        Return a list of full paths to the output stylesheets for use with
        'send_output' or 'get_result'.
        """

        filenames = self.transform_resources[transform_identifier]

        # Sanity check for the filenames list.

        if isinstance(filenames, str) or isinstance(filenames, unicode):
            raise ValueError, filenames

        paths = []
        for filename in filenames:
            paths.append(os.path.abspath(os.path.join(self.resource_dir, filename)))
        return paths

    def get_in_page_resource(self, trans):

        """
        Return the in-page resource being referred to in the given transaction
        'trans'.
        """

        if hasattr(self, "path_encoding"):
            return trans.get_path_info(self.path_encoding).split("/")[-1]
        else:
            return trans.get_path_info().split("/")[-1]

    def respond(self, trans):

        """
        Respond to the request described by the given transaction 'trans'.
        """

        # Only obtain field information according to the stated method.

        content_type = trans.get_content_type()
        method = trans.get_request_method()
        in_page_resource = self.get_in_page_resource(trans)

        # Handle typical request methods, processing request information.

        if method == "GET":

            # Get the fields from the request path (URL).

            form = XSLForms.Fields.Form(encoding=None, values_are_lists=1)
            parameters = trans.get_fields_from_path()
            form.set_parameters(parameters)

        elif method == "POST" and content_type.media_type == "application/x-www-form-urlencoded":

            # Get the fields from the request body.

            form = XSLForms.Fields.Form(encoding=None, values_are_lists=1)
            if hasattr(self, "encoding"):
                parameters = trans.get_fields_from_body(self.encoding)
            else:
                parameters = trans.get_fields_from_body()

            # NOTE: Konqueror workaround.
            self.clean_parameters(parameters)

            form.set_parameters(parameters)

        else:

            # Initialise empty container.

            form = XSLForms.Fields.Form(encoding=None, values_are_lists=1)

        # Call an overridden method with the processed request information.

        self.respond_to_form(trans, form)

    def respond_to_form(self, trans, form):

        """
        Respond to the request described by the given transaction 'trans', using
        the given 'form' object to conveniently retrieve field (request
        parameter) information and structured form information (as DOM-style XML
        documents).
        """

        trans.set_response_code(500)
        trans.set_content_type(WebStack.Generic.ContentType("text/plain"))
        out = trans.get_response_stream()
        out.write("Resource not fully defined to respond.")
        raise WebStack.Generic.EndOfResponse

def prepare_output(self, output_identifier):

    """
    Prepare the output stylesheet for the resource class or object 'self'
    corresponding to the given 'output_identifier'. Return the template path
    and the output stylesheet path in a 2-tuple.
    """

    template_filename, output_filename = self.template_resources[output_identifier]
    output_path = os.path.abspath(os.path.join(self.resource_dir, output_filename))
    template_path = os.path.abspath(os.path.join(self.resource_dir, template_filename))
    XSLForms.Prepare.ensure_stylesheet(template_path, output_path)
    return template_path, output_path

def prepare_fragment(self, fragment_identifier):

    """
    Prepare the output stylesheet for the resource class or object 'self'
    corresponding to the given 'fragment_identifier'. Return the template path
    and the output stylesheet path in a 2-tuple.
    """

    output_identifier, fragment_filename, node_identifier = self.in_page_resources[fragment_identifier]
    fragment_path = os.path.abspath(os.path.join(self.resource_dir, fragment_filename))
    template_filename, output_filename = self.template_resources[output_identifier]
    template_path = os.path.abspath(os.path.join(self.resource_dir, template_filename))
    XSLForms.Prepare.ensure_stylesheet_fragment(template_path, fragment_path, node_identifier)
    return template_path, fragment_path

def prepare_initialiser(self, input_identifier, init_enumerations):

    """
    Prepare the initialising stylesheet for the resource class or object 'self'
    corresponding to the given 'input_identifier' and 'init_enumerations' flag.
    Return the template path and the initialising stylesheet path in a 2-tuple.
    """

    template_filename, input_filename = self.init_resources[input_identifier]
    input_path = os.path.abspath(os.path.join(self.resource_dir, input_filename))
    template_path = os.path.abspath(os.path.join(self.resource_dir, template_filename))
    XSLForms.Prepare.ensure_input_stylesheet(template_path, input_path, init_enumerations)
    return template_path, input_path

def prepare_resources(cls):

    "Prepare the resources associated with the class 'cls'."

    for output_identifier in cls.template_resources.keys():
        prepare_output(cls, output_identifier)
    for fragment_identifier in cls.in_page_resources.keys():
        prepare_fragment(cls, fragment_identifier)

    # NOTE: Using init_enumerations=1 here.

    for input_identifier in cls.init_resources.keys():
        prepare_initialiser(cls, input_identifier, 1)

# vim: tabstop=4 expandtab shiftwidth=4

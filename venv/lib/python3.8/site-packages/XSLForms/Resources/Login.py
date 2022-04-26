#!/usr/bin/env python

"""
Login resources for XSLForms applications. These resources use "root" attributes
on transaction objects, and therefore should be defined within the appropriate
resources in site maps.

Copyright (C) 2006, 2007 Paul Boddie <paul@boddie.org.uk>

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

from WebStack.Generic import ContentType, EndOfResponse
import XSLForms.Resources.WebResources

import WebStack.Resources.LoginRedirect # LoginRedirectResource
import WebStack.Resources.Login # get_target

class LoginResource(XSLForms.Resources.WebResources.XSLFormsResource):

    """
    A login screen resource which should be modified or subclassed to define the
    following attributes:

      * resource_dir
      * template_resources - including a "login" entry for the login screen and
                             a "success" entry for a screen indicating a
                             successful login (used when redirects are not in
                             use)
      * document_resources - including a "translations" entry

    The latter attribute is optional.

    The login template must define a "login" action, and provide a document
    structure where the login credentials can be found through this class's
    'path_to_login_element' attribute (which can be overridden or modified).
    Such a structure would be as follows for the default configuration:

    <login username="..." password="..."/>

    The success template must provide a document structure where the location of
    the application can be found through this class's 'path_to_success_element'
    attribute (which can be overridden or modified). Such a structure would be
    as follows for the default configuration:

    <success location="..."/>
    """

    path_to_login_element = "/login"
    path_to_success_element = "/success"

    def __init__(self, authenticator, use_redirect=1):

        """
        Initialise the resource with an 'authenticator'. If the optional
        'use_redirect' parameter is specified and set to a false value (unlike
        the default), 

        To get the root of the application, this resource needs an attribute on
        the transaction called "root".
        """

        self.authenticator = authenticator
        self.use_redirect = use_redirect

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        parameters = form.get_parameters()
        documents = form.get_documents()
        attributes = trans.get_attributes()

        # Ensure the presence of a document.

        if documents.has_key("login"):
            doc = documents["login"]
        else:
            doc = form.new_instance("login")

        template_name = "login"

        # NOTE: Consider initialisation of both the login and success documents.

        # Test for login.

        if parameters.has_key("login"):
            logelem = doc.xpath(self.path_to_login_element)[0]
            username = logelem.getAttribute("username")
            password = logelem.getAttribute("password")

            if self.authenticator.authenticate(trans, username, password):
                app, path, qs = WebStack.Resources.Login.get_target(trans)

                # Either redirect or switch to the success template.

                if self.use_redirect:
                    trans.redirect(app + trans.encode_path(path) + qs)
                else:
                    template_name = "success"
                    doc = form.new_instance("success")
                    successelem = doc.xpath(self.path_to_success_element)[0]
                    successelem.setAttribute("location", app + trans.encode_path(path) + qs)
            else:
                error = doc.createElement("error")
                logelem.appendChild(error)
                error.setAttribute("message", "Username or password not valid")

        # Start the response.

        trans.set_content_type(ContentType("application/xhtml+xml"))
        stylesheet_parameters = {}
        references = {}

        # Set up translations.

        if self.document_resources.has_key("translations"):
            translations_xml = self.prepare_document("translations")

            try:
                language = trans.get_content_languages()[0]
            except IndexError:
                language = "en"

            stylesheet_parameters["locale"] = language
            references["translations"] = translations_xml

        # Complete the response.

        trans_xsl = self.prepare_output(template_name)
        stylesheet_parameters["root"] = attributes["root"]
        self.send_output(trans, [trans_xsl], doc, stylesheet_parameters, references=references)

class LoginRedirectResource(WebStack.Resources.LoginRedirect.LoginRedirectResource):

    "A redirect resource which uses dynamic knowledge about the URL space."

    def __init__(self, host, path_to_login, *args, **kw):

        """
        Initialise the resource with the 'host', 'path_to_login' (the path from
        the root of the application to the login screen), and other
        LoginRedirectResource details.

        To get the root of the application, this resource needs an attribute on
        the transaction called "root".

        Examples of 'path_to_login' with "root" attribute and result:

        "login", "/" -> "/login"
        "login", "/app/" -> "/app/login"
        "app/login", "/" -> "/app/login"
        """

        self.host = host
        self.path_to_login = path_to_login
        WebStack.Resources.LoginRedirect.LoginRedirectResource.__init__(self, *args, **kw)

    def get_app_url(self, trans):
        return self.host

    def get_login_url(self, trans):
        return self.host + trans.get_attributes()["root"] + self.path_to_login

# vim: tabstop=4 expandtab shiftwidth=4

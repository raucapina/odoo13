#!/home/ricardoab/code/odoo13/venv/bin/python

"Fix a template document's namespaces."

import XSLForms.Prepare
import sys

if __name__ == "__main__":
    try:
        input_xml = sys.argv[1]
        output_xml = sys.argv[2]
    except IndexError:
        print "Please specify template input and result filenames."
        print "For example:"
        print "xslform_fix.py template.xhtml template_new.xhtml"
        sys.exit(1)

    XSLForms.Prepare.fix_namespaces(input_xml, output_xml)

# vim: tabstop=4 expandtab shiftwidth=4

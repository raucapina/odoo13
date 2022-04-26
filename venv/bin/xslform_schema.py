#!/home/ricardoab/code/odoo13/venv/bin/python

"Prepare a template schema."

import XSLForms.Prepare
import sys

if __name__ == "__main__":
    try:
        input_xml = sys.argv[1]
        output_xml = sys.argv[2]
    except IndexError:
        print "Please specify a template and an schema filename."
        print "For example:"
        print "xslform_schema.py template.xhtml schema.xml"
        sys.exit(1)

    XSLForms.Prepare.make_schema(input_xml, output_xml)

# vim: tabstop=4 expandtab shiftwidth=4

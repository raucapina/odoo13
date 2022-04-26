#!/home/ricardoab/code/odoo13/venv/bin/python

"Prepare a templating stylesheet from a Qt Designer file."

import XSLForms.Prepare
import sys

if __name__ == "__main__":
    try:
        input_xml = sys.argv[1]
        output_xml = sys.argv[2]
    except IndexError:
        print "Please specify a template and an output filename."
        print "For example:"
        print "xslform_qt_prepare.py template.ui output.xsl"
        sys.exit(1)

    XSLForms.Prepare.make_qt_stylesheet(input_xml, output_xml)

# vim: tabstop=4 expandtab shiftwidth=4

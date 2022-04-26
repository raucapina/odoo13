#!/home/ricardoab/code/odoo13/venv/bin/python

"Prepare an input stylesheet."

import XSLForms.Prepare
import sys

if __name__ == "__main__":
    try:
        input_xml = sys.argv[1]
        output_xml = sys.argv[2]
    except IndexError:
        print "Please specify a template and an output filename."
        print "To suppress the initialisation of enumerations, specify --noenum last."
        print "For example:"
        print "xslform_input.py template.xhtml output.xsl --noenum"
        sys.exit(1)

    XSLForms.Prepare.make_input_stylesheet(input_xml, output_xml, "--noenum" not in sys.argv)

# vim: tabstop=4 expandtab shiftwidth=4

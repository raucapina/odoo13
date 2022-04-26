#!/home/ricardoab/code/odoo13/venv/bin/python

"Prepare a template with expanded macros."

import XSLForms.Prepare
import sys

if __name__ == "__main__":
    try:
        input_xml = sys.argv[1]
        output_xml = sys.argv[2]
    except IndexError:
        print "Please specify a template and an output filename."
        print "For example:"
        print "xslform_preparemacro.py template.xhtml output.xhtml"
        sys.exit(1)

    XSLForms.Prepare.make_stylesheet(input_xml, output_xml, ["PrepareMacro.xsl"])

# vim: tabstop=4 expandtab shiftwidth=4

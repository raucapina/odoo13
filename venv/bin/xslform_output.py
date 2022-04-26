#!/home/ricardoab/code/odoo13/venv/bin/python

"Prepare a templating stylesheet."

import XSLForms.Output
from XSLTools import XSLOutput
import libxml2dom
import sys

def get_dict(marker):
    d = {}
    if marker in sys.argv:
        i = sys.argv.index(marker) + 1
        while i < len(sys.argv) and not sys.argv[i].startswith("--"):
            d[sys.argv[i]] = sys.argv[i+1]
            i += 2
    return d

if __name__ == "__main__":
    try:
        input_xml = sys.argv[1]
        trans_xsl = sys.argv[2]
        output_xml = sys.argv[3]
    except IndexError:
        print "Please specify an input filename, a template filename and an output filename."
        print "For example:"
        print "xslform_output.py input.xml output.xsl output.xhtml"
        print
        print "Additional references may be specified in parameter name and value pairs."
        print "For example:"
        print "--references translations translations.xml"
        print "--parameters locale en_GB"
        sys.exit(1)

    references = get_dict("--references")
    parameters = get_dict("--parameters")

    proc = XSLOutput.Processor([trans_xsl], references=references, parameters=parameters)
    proc.send_output(open(output_xml, "wb"), "utf-8", libxml2dom.parse(input_xml))

# vim: tabstop=4 expandtab shiftwidth=4

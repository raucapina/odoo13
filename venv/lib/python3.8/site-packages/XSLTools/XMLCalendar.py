#!/usr/bin/env python

"""
Copyright (C) 2005, 2007 Paul Boddie <paul@boddie.org.uk>

Additional copyrights for the monthcalendar function:

Copyright (c) 2001, 2002, 2003, 2004, 2005 Python Software Foundation.
Copyright (c) 2000 BeOpen.com.
Copyright (c) 1995-2001 Corporation for National Research Initiatives.
Copyright (c) 1991-1995 Stichting Mathematisch Centrum.

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

import libxml2dom
import calendar

# Borrowed from calendar, but with a non-global first weekday variable.

def monthcalendar(year, month, firstweekday=0):
    """Return a matrix representing a month's calendar.
       Each row represents a week; days outside this month are zero."""
    day1, ndays = calendar.monthrange(year, month)
    rows = []
    r7 = range(7)
    day = (firstweekday - day1 + 6) % 7 - 5   # for leading 0's in first week
    while day <= ndays:
        row = [0, 0, 0, 0, 0, 0, 0]
        for i in r7:
            if 1 <= day <= ndays: row[i] = day
            day = day + 1
        rows.append(row)
    return rows

# Helper functions.

def get_previous_year_and_month(year, month):
    if month - 1 == 0:
        return year - 1, 12
    else:
        return year, month - 1

def get_next_year_and_month(year, month):
    if month + 1 == 13:
        return year + 1, 1
    else:
        return year, month + 1

# XML production functions.

def write_month_to_document(doc, root, year, month):

    """
    Write into the document 'doc' appending to the child elements of the 'root'
    element, inserting a month calendar based on the specified 'year' and
    'month'.
    """

    weeks = monthcalendar(year, month)
    month_element = root.appendChild(doc.createElement("month"))

    # Add navigational attributes.

    month_element.setAttribute("number", str(month))
    month_element.setAttribute("year", str(year))
    yp, mp = get_previous_year_and_month(year, month)
    month_element.setAttribute("number-previous", str(mp))
    month_element.setAttribute("year-previous", str(yp))
    yn, mn = get_next_year_and_month(year, month)
    month_element.setAttribute("number-next", str(mn))
    month_element.setAttribute("year-next", str(yn))

    # Add weeks and days.

    for numbers in weeks:
        week_element = month_element.appendChild(doc.createElement("week"))
        for number in numbers:
            day_element = week_element.appendChild(doc.createElement("day"))
            if number != 0:
                day_element.setAttribute("date", "%04d%02d%02d" % (year, month, number))
                day_element.setAttribute("number", str(number))

    return month_element

def get_calendar_for_month(year, month):
    doc = libxml2dom.createDocument(None, "calendar", None)
    write_month_to_document(doc, doc.childNodes[-1], year, month)
    return doc

if __name__ == "__main__":
    import sys
    try:
        print get_calendar_for_month(int(sys.argv[1]), int(sys.argv[2])).toString()
    except (IndexError, ValueError):
        print "Please specify a year and a month (numeric, 1-12)."

# vim: tabstop=4 expandtab shiftwidth=4

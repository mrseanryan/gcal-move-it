"""
Clean description of annoying duplicate URLs.

Cause: the mobile version of Google Calendar cannot parse the 'markdown-like' text format,
and so on edit, the URLs get 'doubled out' with braces.

Subsequent edits between the browser and mobile Calendar cause further duplication.
"""
NEW_LINE = "\n"


def fix_line(line):
    parts = line.split(" ")

    line_fixed = ""

    prev_part = None
    for part in parts:
        if (prev_part != None):
            with_braces = "(" + prev_part + ")"
            if (with_braces in part):
                part = part.replace(with_braces, "")
                line_fixed += part
                prev_part = None
                continue
            with_braces = "(mailto:" + prev_part + ")"
            if (with_braces in part):
                part = part.replace(with_braces, " ")
                line_fixed += part
                prev_part = None
                continue

        if (len(line_fixed) > 0):
            line_fixed += " "

        line_fixed += part
        prev_part = part

    return line_fixed


def clean_description(desc):
    lines = desc.split(NEW_LINE)

    lines_fixed = map(fix_line, lines)

    return NEW_LINE.join(lines_fixed)

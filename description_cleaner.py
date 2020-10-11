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
    did_replace = False
    for part in parts:
        if (prev_part != None):
            with_braces = "(" + prev_part + ")"
            if (with_braces in part):
                part = part.replace(with_braces, "")
                line_fixed += part
                prev_part = None
                did_replace = True
                continue
            with_braces = "(mailto:" + prev_part + ")"
            if (with_braces in part):
                part = part.replace(with_braces, " ")
                line_fixed += part
                prev_part = None
                did_replace = True
                continue

        if (len(line_fixed) > 0):
            line_fixed += " "

        line_fixed += part
        prev_part = part

    # Avoid updating when the only change is loss of whitespace:
    if (did_replace):
        return line_fixed  # some whitespace lost

    return line


def clean_description(desc):
    lines = desc.split(NEW_LINE)

    lines_fixed = map(fix_line, lines)

    return NEW_LINE.join(lines_fixed)

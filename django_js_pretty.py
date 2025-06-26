#!/usr/bin/env python3

import os
import re

import jsbeautifier
from identify.identify import tags_from_filename


def preserve_django_tags(content):
    """Replace Django tags with placeholders to protect them during formatting."""
    django_pattern = r"({%.*?%}|{{.*?}})"
    preserved_tags = []

    def replace_tag(match):
        tag = match.group(0)
        placeholder = f"__DJANGO_TAG_{len(preserved_tags)}__"
        preserved_tags.append(tag)
        return placeholder

    modified_content = re.sub(django_pattern, replace_tag, content, flags=re.DOTALL)
    return modified_content, preserved_tags


def restore_django_tags(content, preserved_tags):
    """Restore Django tags from placeholders."""
    for i, tag in enumerate(preserved_tags):
        placeholder = f"__DJANGO_TAG_{i}__"
        content = content.replace(placeholder, tag)
    return content


def format_js(content):
    """Format JavaScript code with standard indentation and spacing."""
    content, preserved_tags = preserve_django_tags(content)

    # Remove extra newlines
    content = re.sub(r"\n{3,}", "\n\n", content)

    opts = jsbeautifier.default_options()
    opts.indent_size = 4
    content = jsbeautifier.beautify(content, opts)

    return restore_django_tags(content, preserved_tags)


def format_js_file(file_path):
    """Format a JavaScript file."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    formatted = format_js(content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(formatted)


def format_html_file(file_path):
    """Format JavaScript inside an HTML file while preserving HTML structure."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Split the HTML content into parts: non-script and script sections
    parts = []
    current_pos = 0

    while current_pos < len(content):
        opening_tag_start = content.find("<script", current_pos)
        if opening_tag_start == -1:
            # No more script tags
            parts.append((False, content[current_pos:]))
            break

        # Add content before script tag
        if opening_tag_start > current_pos:
            parts.append((False, content[current_pos:opening_tag_start]))

        # Find the end of opening script tag
        opening_tag_end = content.find(">", opening_tag_start)
        if opening_tag_end == -1:
            # Malformed HTML
            parts.append((False, content[current_pos:]))
            break

        # Find closing script tag
        closing_tag_text = "</script>"
        closing_tag_start = content.find(closing_tag_text, opening_tag_end)
        if closing_tag_start == -1:
            # Malformed HTML
            parts.append((False, content[current_pos:]))
            break

        # Expand the script_end to include any whitespace BEFORE the closing tag
        closing_tag_end = closing_tag_start + len(closing_tag_text)
        closing_tag_start -= 1
        while content[closing_tag_start].isspace():
            closing_tag_start -= 1
        closing_tag_start += 1

        # Split into opening tag, content, and closing tag
        opening_tag = content[opening_tag_start : opening_tag_end + 1]
        script_content = content[opening_tag_end + 1 : closing_tag_start]
        closing_tag = content[closing_tag_start:closing_tag_end]

        parts.append((False, opening_tag))
        parts.append((True, script_content))
        parts.append((False, closing_tag))

        current_pos = closing_tag_end

    # Format only the script parts
    formatted_parts = []
    for is_script, part in parts:
        if is_script and part.strip():
            formatted_part = format_js(part)
            if "\n" in formatted_part:
                # Ensure a multiline formatted part starts with a newline
                formatted_part = "\n" + formatted_part
                pass
            formatted_parts.append(formatted_part)
        else:
            formatted_parts.append(part)

    formatted_content = "".join(formatted_parts)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(formatted_content)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Format JS/HTML files, preserving Django template tags.")
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to format",
    )
    args = parser.parse_args()

    for file_path in args.files:
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            continue

        file_tags = tags_from_filename(file_path)
        print(f"Formatting: {file_path}")
        if "javascript" in file_tags:
            format_js_file(file_path)
        elif "html" in file_tags:
            format_html_file(file_path)
        else:
            print(f"Unsupported file type: {file_path}")


if __name__ == "__main__":
    main()

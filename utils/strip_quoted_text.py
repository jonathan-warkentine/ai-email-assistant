import re

def strip_quoted_text(text):
    lines = text.split('\n')
    stripped_lines = list()
    for line in lines:
        line_stripped = line.strip() # Remove leading/trailing whitespaces
        if line_stripped.startswith('>'):
            continue
        # Remove 'On ... wrote: ... \n' using regex, anywhere in the line
        line_stripped = re.sub(r'On .+ wrote:.+\n', '', line_stripped, flags=re.IGNORECASE).strip()
        if line_stripped:  # Exclude empty lines
            stripped_lines.append(line_stripped)
    return '\n'.join(stripped_lines)
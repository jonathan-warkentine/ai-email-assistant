def is_text_part(part):
    # Return True if the part is plain text, False otherwise
    return part.get("mimeType") == "text/plain"
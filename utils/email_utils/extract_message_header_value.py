def extract_message_header_value(message, header_name):
    """
    Extracts the value of a specific header from a Gmail message.

    :param message: Gmail message object.
    :param header_name: Name of the header to extract.
    :return: Value of the specified header or None if not found.
    """
    headers = message['payload']['headers']
    for header in headers:
        if header['name'] == header_name:
            return header['value']
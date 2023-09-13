def parse_new_messages_from_histories(histories):
    """
    Extracts new messages from the provided Gmail histories.

    :param histories: List of Gmail history objects.
    :return: List of new Gmail messages.
    """
    messages = list()
    for history in histories:
        messages_added = history.get('messagesAdded')
        
        # Check if there are any messages added in the current history
        if messages_added:
            for message in messages_added:
                messages.append(message.get('message'))
    
    return messages
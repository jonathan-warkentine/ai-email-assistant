from utils import email_utils

def filter_threads_awaiting_response(user, threads):
    """
    Filters Gmail threads that have not yet been replied to.

    :param threads: List of Gmail threads.
    :return: Filtered list of Gmail threads that need a response.
    """
    threads_awaiting_response = list()

    for thread in threads:
        last_message = email_utils.extract_last_message_in_thread(thread)
        
        sender_email = email_utils.extract_email_address_from_text(
            email_utils.extract_message_header_value(
                message=last_message,
                header_name='From'
            )
        )

        # Check if the sender is not the authenticated user
        if sender_email != user:
            threads_awaiting_response.append(thread)

    return threads_awaiting_response
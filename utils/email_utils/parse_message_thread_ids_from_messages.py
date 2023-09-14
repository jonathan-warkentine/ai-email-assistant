from utils import deduplicate_list

def parse_message_thread_ids_from_messages(messages):
    message_thread_ids = list()
    for message in messages:
        message_thread_ids.append(message.get('threadId'))
    
    return deduplicate_list(message_thread_ids)
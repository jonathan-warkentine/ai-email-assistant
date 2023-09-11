def process_new_emails():
    threads_with_new_messages = gmail_client.fetch_threads_with_new_messages()
    threads_needing_response = gmail_client.filter_threads_needing_response(threads_with_new_messages)

    # Prepare thread as conversation for ChatGPT API call ('messages' parameter)
    jobs = list()
    for thread in threads_needing_response:
        messages = gmail_client.parse_thread_for_messages(thread)
        prepared_messages = gmail_client.prepare_messages_for_chatgpt(messages=messages)
        messages_regard_job_chatgpt_response = chatgpt_client.decide_if_messages_regard_job(prepared_messages)
        messages_regard_job_as_boolean = convert_string_to_boolean(messages_regard_job_chatgpt_response.get('choices')[0].get('message').get('content'))

        if messages_regard_job_as_boolean == False:
            continue

        last_email_in_thread = gmail_client.extract_last_message_in_thread(thread)
        message_id_of_last_email = gmail_client.extract_message_header_value(
            message = last_email_in_thread,
            header_name = 'Message-Id'
        )
        subject_of_last_email = gmail_client.extract_message_header_value(
            message = last_email_in_thread,
            header_name = 'Subject'
        )
        email_address_of_sender_of_last_email = extract_email_from_text(
            gmail_client.extract_message_header_value(
                message = last_email_in_thread,
                header_name = 'From'
            )
        )
        job = Job(
            recipient = email_address_of_sender_of_last_email, 
            subject = subject_of_last_email, 
            conversation = prepared_messages, 
            thread = thread,
            in_reply_to = message_id_of_last_email
        )
        jobs.append(job)
        ################################################
        #####      PRINT FOR DEBUGGING PURPOSES    #####
        ################################################
        print(f'\n"{subject_of_last_email}" from {email_address_of_sender_of_last_email} (message_id = {message_id_of_last_email})')
        ################################################

    for job in jobs:
        chatgpt_response = chatgpt_client.fetch_chatgpt_response(messages = job.conversation, custom_system_content = scheduling_parameters)
        message_text = chatgpt_response.get('choices')[0].get('message').get('content')
        email_draft = gmail_client.compose_email(
            recipient = job.recipient, 
            subject = job.subject, 
            message_text = message_text, 
            thread_id = job.thread.get('id'),
            in_reply_to = job.in_reply_to
        )
        gmail_client.save_email_draft(email_draft)

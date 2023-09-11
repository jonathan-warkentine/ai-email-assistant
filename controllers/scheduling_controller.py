from controllers.scheduling_helpers import _get_availability_string


def get_scheduling_parameters_as_chatgpt_system_prompt(workiz_client):
    """
    Get scheduling parameters for chatGPT system prompt.

    :param workiz_client: Client instance for Workiz service
    :return: Dictionary with scheduling parameters
    """
    scheduled_appointments = workiz_client.get_scheduled_appointments()
    availability_string = _get_availability_string(scheduled_appointments)
    scheduling_parameters = {
        'role': 'system',
        'content': f'Your business hours are 8AM - 6PM Monday through Saturday. Here are your available slots:\n{availability_string}\n\nWhen responding to customers, refer to tomorrow\'s date as "tomorrow", and specify "this week" or "next week" as necessary.'
    }
    return scheduling_parameters


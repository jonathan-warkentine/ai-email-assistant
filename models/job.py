class Job:
    def __init__(self, recipient, subject, conversation = [], thread = [], in_reply_to = None, chatgpt_completed_conversation=""):
        self.recipient = recipient
        self.subject = subject
        self.conversation = conversation
        self.thread = thread
        self.in_reply_to = in_reply_to
        self.chatgpt_completed_conversation = chatgpt_completed_conversation

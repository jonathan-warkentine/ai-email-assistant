class Job:
    def __init__(self, recipient, subject, conversation = [], thread = [], in_reply_to = None):
        self.recipient = recipient
        self.subject = subject
        self.conversation = conversation
        self.thread = thread
        self.in_reply_to = in_reply_to

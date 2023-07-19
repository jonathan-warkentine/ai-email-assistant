class Job:
    def __init__(self, recipient, subject, conversation = [], thread = []):
        self.recipient = recipient
        self.subject = subject
        self.conversation = conversation
        self.thread = thread

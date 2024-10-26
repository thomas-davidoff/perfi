class CustomException(Exception):
    code = 500

    def __init__(self, msg=None):
        # Set the message to the provided value or default to the class-level msg
        self.msg = msg or getattr(self, "msg", "An error occurred")
        super().__init__(self.msg)

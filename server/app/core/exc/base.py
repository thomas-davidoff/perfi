class CustomException(Exception):
    code = 500

    def __init__(self, msg=None, code=None):
        # Set the message to the provided value or default to the class-level msg
        self.msg = msg or getattr(self, "msg", "An error occurred")
        super().__init__(self.msg)

        if code is not None:
            self.code = code

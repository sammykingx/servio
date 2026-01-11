class GigError(Exception):
    def __init__(self, message, type="warning", status_code=400, code=None):
        self.error = "Operation not allowed"
        self.type = type
        self.message = message
        self.status_code = status_code
        self.code = code
        
        super().__init__(message)

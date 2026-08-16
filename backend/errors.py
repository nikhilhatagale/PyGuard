class ValidationError(Exception):
    """
    Raised when user gives invalid input, unsafe file,
    corrupted ZIP, unsupported extension etc.
    """
    def __init__(self, message="Invalid input"):
        self.message = message
        super().__init__(self.message)


class AnalysisError(Exception):
    """
    Raised when static analyzer / AST fails.
    """
    def __init__(self, message="Analysis failed"):
        self.message = message
        super().__init__(self.message)


class AIServiceError(Exception):
    """
    Raised when AI model fails or API response is invalid.
    """
    def __init__(self, message="AI processing failed"):
        self.message = message
        super().__init__(self.message)

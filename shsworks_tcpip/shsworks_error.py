class SHSWorksError(Exception):
    """Exception class for the handling of Errors within SHSWorks.
    """

class UnknownCommandError(Exception):
    """Exception class for the handling of Errors caused by commands not available in SHSWorks.
    """

class UnexpectedAnswerFormatError(Exception):
    """Custom exception to be raised when an answer has an unexpected format.
    """
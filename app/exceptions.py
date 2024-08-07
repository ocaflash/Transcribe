class AppException(Exception):
    """Base exception for the application."""
    pass

class FileProcessingError(AppException):
    """Raised when there's an error processing a file."""
    pass

class TranscriptionError(AppException):
    """Raised when there's an error during transcription."""
    pass

class TranslationError(AppException):
    """Raised when there's an error during translation."""
    pass

class GoogleDriveError(AppException):
    """Raised when there's an error interacting with Google Drive."""
    pass

class DatabaseError(AppException):
    """Raised when there's an error interacting with the database."""
    pass
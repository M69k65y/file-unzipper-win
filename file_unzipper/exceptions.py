class UnzipperException(Exception):
    """ Base exception
    """

    message = "Unknown error occurred"
    
    def __init__(self):
        """ Initialise the exception
        """


    def __str__(self):
        return self.message


class UnzipperNotZipFile(UnzipperException):
    """ Exception raised when file is not a zip file
    """
    message = "The provided file is not a zip file"


class UnzipperPasswordProtected(UnzipperException):
    """ Exception raised when file is password protected or password provided is invalid
    """
    message = "The zip file is either password protected or the provided password is invalid"


class UnzipperFileTooLarge(UnzipperException):
    """ Exception raised when file size is larger than the allowed file size (if set)
    """
    message = "The size of the zip file is larger than the allowed file size"


class UnzipperImageCompression(UnzipperException):
    """ Exception raised when file to be compressed is not an image (when Unzipper initialised to compress images)
    """
    message = "The file to be compressed is not an image"


class UnzipperFileSizeLimitFormat(UnzipperException):
    """ Exception raised when file size limit is incorrectly formatted
    """
    message = "The file size limit is not properly formatted. Try set it as '1 KB'"
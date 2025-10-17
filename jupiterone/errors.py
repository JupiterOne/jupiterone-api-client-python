
class JupiterOneClientError(Exception):
    """ Raised when error creating client """
    pass


class JupiterOneApiRetryError(Exception):
    """ Used to trigger retry on rate limit """
    pass


class JupiterOneApiError(Exception):
    """ Raised when API returns error response """
    pass

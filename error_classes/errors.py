class TerminationError(Exception):
    def __init__(self):
        super().__init__("Session terminated prematurely, gracefully.")

class QueryError(Exception):
    def __init__(self, *args):
        super().__init__("Querying did not yield any results.")


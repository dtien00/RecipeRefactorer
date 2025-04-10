class TerminationError(Exception):
    def __init__(self):
        super().__init__("Session terminated prematurely, gracefully.")
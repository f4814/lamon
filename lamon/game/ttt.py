from .source import Source

class TTT(Source):
    """ Trouble in terrorist town game object """
    def __init__(self, config):
        self.name = "Trouble in Terrorist Town"
        super().__init__(config)

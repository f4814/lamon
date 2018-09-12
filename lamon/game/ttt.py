from .source import Source

class TTT(Source):
    """ Trouble in terrorist town game object """
    def __init__(self, config):
        self.name = "TTT"
        self.internalName = "Trouble in terrorist town"
        super().__init__(config)

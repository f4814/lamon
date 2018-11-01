from .source import Source

class TTT(Source):
    """ Trouble in terrorist town game object """
    def __init__(self, players, config):
        super().__init__(players, config)
        self.name = "ttt"
        self.internalName = "Trouble in Terrorist Town"

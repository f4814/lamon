from .source import source

class CSGO(source):
    """ CS:GO game obejct """
    def __init__(self, config):
        self.name = "Counter Strike: Global Offensive"
        super().__init__(config)

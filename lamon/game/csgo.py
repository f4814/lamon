from .source import source

class CSGO(source):
    """ CS:GO game obejct """
    def __init__(self, config):
        self.name = "CSGO"
        self.internalName = "Counter Strike: Global Offensive"
        super().__init__(config)

class Player:
    def __init__(self, number, color, name):
        self.number = number
        self.color = color
        self.name = name
        self.owned_objects = []
        self.power_projection = 0
        self.supply = 0 # Our Shepherd will supply our needs if on him we relyyyy
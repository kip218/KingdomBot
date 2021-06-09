from .unit import Unit

class Scout(Unit):
    def __init__(self):
        self.name = 'Scout'
        self.emoji = ':dagger:'
        self.cost = 100
        self.dmg = 30
        self.max_hp = 70
        self.health = self.max_hp
        self.speed = 0.8
        self.gauge = 0
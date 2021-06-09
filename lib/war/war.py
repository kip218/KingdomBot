class War():
    def __init__(self, army1, army2):
        self.army1 = army1
        self.army2 = army2

    def process_turn(self):
        self.army1.attack(self.army2)
        self.army2.attack(self.army1)
        self.army1.remove_dead()
        self.army2.remove_dead()

    def fill_gauge(self):
        self.army1.fill_gauge()
        self.army2.fill_gauge()

    def war_over(self):
        return self.army1.army_empty() or self.army2.army_empty()
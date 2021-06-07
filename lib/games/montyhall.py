from random import choices

class MontyHall():
    def __init__(self):
        self.options = {
                    1:{'n':1, 'is_open':False, 'emote':':one:', 'is_coin':False},
                    2:{'n':2, 'is_open':False, 'emote':':two:', 'is_coin':False},
                    3:{'n':3, 'is_open':False, 'emote':':three:', 'is_coin':False}
                    }
        self.coin = choices((1, 2, 3))[0]
        self.options[self.coin]['is_coin'] = True
        self.guess = None

        #emotes
        self.coin_emote = ':coin:'
        self.x_emote = ':x:'
        self.package_emote = ':package:'
        self.arrow_emote = ':arrow_down:'


    def display(self):
        res = ''
        for k in sorted(self.options):
            pkg = self.options[k]
            if k == self.guess:
                res += self.arrow_emote
            else:
                res += pkg['emote']
        res += '\n'
        for k in sorted(self.options):
            pkg = self.options[k]
            if pkg['is_open']:
                if pkg['is_coin']:
                    res += self.coin_emote
                else:
                    res += self.x_emote
            else:
                res += self.package_emote
        return res


    def take_guess(self, n):
        self.guess = n


    def reveal_pkg(self):
        lst = [1, 2, 3]
        lst.remove(self.coin)
        if self.guess in lst:
            lst.remove(self.guess)
        rand_n = choices(lst)[0]
        self.options[rand_n]['is_open'] = True
        return rand_n


    def switch(self, switch):
        if self.guess is None:
            return
        if switch == 'n':
            return
        if switch == 'y':
            old_guess = self.guess
            for pkg in self.options.values():
                if not pkg['is_open'] and pkg['n'] != old_guess:
                    self.guess = pkg['n']


    def reveal_all(self):
        for pkg in self.options.values():
            pkg['is_open'] = True

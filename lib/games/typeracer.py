from random_word import RandomWords
from random import shuffle, randint
from discord import Embed

r = RandomWords()


class TypeRacer():
    def __init__(self, num_words):
        self.ready = False
        self.num_words = num_words
        self.word_lst = self.get_words_lst()
        self.i = 0
        self.curr_word = self.word_lst[self.i]
        self.scoreboard = {}


    def get_words_lst(self):
        found = False
        while not found:
            words_lst = r.get_random_words(limit=self.num_words, hasDictionaryDef="true")
            found = bool(words_lst)
        #convert to lowercase & shuffle
        words_lst = [word.lower() for word in words_lst]
        shuffle(words_lst)
        self.ready = True
        return words_lst


    def is_correct(self, answer):
        return answer == self.curr_word


    def is_copypaste(self, answer):
        return answer == self.get_word_display()


    def get_word(self):
        return self.curr_word


    def get_word_display(self):
        return self.curr_word[0] + "\u200b" + self.curr_word[1:]


    def next_word(self):
        self.i += 1
        if not self.game_over():
            self.curr_word = self.word_lst[self.i]


    def game_over(self):
        return self.i >= len(self.word_lst)


    def update_scoreboard(self, userID, username):
        if userID in self.scoreboard.keys():
            self.scoreboard[userID]['score'] += 1
            self.scoreboard[userID]['payment'] += self.payment_per_word()
        else:
            self.scoreboard[userID] = {'username':username, 'score':1, 'payment':self.payment_per_word()}


    def process_answer(self, msg):
        answer = msg.content
        userID = msg.author.id
        username = msg.author.name
        embed = Embed(title="The word was:", description=self.curr_word)\
                .set_author(name=f"{username} got it right!", icon_url=msg.author.avatar_url)\
                .set_footer(text=f"{self.i+1}/{self.num_words}")
        self.update_scoreboard(userID, username)
        self.next_word()
        return embed


    def get_word_embed(self):
        word_display = self.get_word_display()
        embed = Embed(title="The word is:", description="`" + word_display + "`")\
                .set_author(name="Type the word!", icon_url="http://www.law.uj.edu.pl/kpk/strona/wp-content/uploads/2016/03/52646-200.png")\
                .set_footer(text=f"{self.i+1}/{self.num_words}")
        return embed


    def get_scoreboard_embed(self):
        if self.scoreboard is None:
            return None
        embed = Embed(title='Final Scoreboard')
        temp = None
        #sorting scoreboard by score
        scoreboard_lst = [self.scoreboard[userID] for userID in self.scoreboard.keys()]
        scoreboard_lst = sorted(scoreboard_lst, key=lambda k: k['score'])
        for i in range(len(scoreboard_lst)):
            score = scoreboard_lst[i]['score']
            username = scoreboard_lst[i]['username']
            payment = scoreboard_lst[i]['payment']
            # checking to make sure people don't have same scores
            if score == temp:
                offset += 1
            else:
                offset = 0
            temp = score
            embed.add_field(name=f"{i+1-offset}. {username}", value=f"**{score} words** *+{payment} Coins*", inline=False)
        return embed


    def get_scoreboard(self):
        return self.scoreboard


    def payment_per_word(self):
        return randint(10, 20)
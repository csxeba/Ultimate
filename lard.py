import random
from typing import List


def pop_from(hand: List):
    return hand.pop(random.randrange(0, len(hand)))


def argmax(x: List):
    return x.index(max(x))


class Card:

    def __init__(self, color, figure, place, value):

        self.color = color
        self.figure = figure
        self.place = place
        self.value = value

    @classmethod
    def create_deck(cls) -> List["Card"]:
        result = []
        for color in "PZMT":
            for i, figure in enumerate(["7", "8", "9", "10", "a", "f", "k", "A"], start=1):
                result.append(cls(color, figure, place=None, value=i))
        return result

    def __repr__(self):
        return "<Card {}{}>".format(self.color, self.figure)


class LardGame:

    def __init__(self):
        self.deck = Card.create_deck()
        self.hands = [[], []]  # type: List[List[int], List[int]]
        self.wins = [[], []]  # type: List[List[int], List[int]]
        self.talon = []
        self.hit = None
        self.lead = None
        self.play = None
        self.indices = None

    def deal(self):
        self.indices = list(range(len(self.deck)))
        self.hands = [[], []]
        random.shuffle(self.indices)
        self.hands[0] = self.indices[:4]
        self.hands[1] = self.indices[4:8]
        self.indices = self.indices[8:]

    def pull(self):
        assert len(self.hands[0]) == len(self.hands[1])
        missing = 4 - len(self.hands[0])
        self.hands[self.lead].extend(self.indices[:missing])
        self.hands[not self.lead].extend(self.indices[missing:missing+missing])
        self.indices = self.indices[missing*2:]

    def attack(self, card: Card):
        figure_hand = [self.deck[idx].figure for idx in self.hands[self.play]]
        valuable = card.figure in ("10", "A")
        can_trick_normal = card.figure in figure_hand
        can_trick_7 = "7" in figure_hand
        if valuable and can_trick_normal:
            selected = self.hands[self.play].pop(figure_hand.index(card.figure))
        elif valuable and can_trick_7:
            selected = self.hands[self.play].pop(figure_hand.index("7"))
        else:
            selected = self.throw()
        return selected

    def initiate(self):
        candidates = [idx for idx in self.hands[self.play] if self.deck[idx].figure != "7"]
        if len(candidates) == 0:
            return pop_from(self.hands[self.play])
        play = random.choice(candidates)
        idx = self.hands[self.play].index(play)
        return self.hands[self.play].pop(idx)

    def throw(self):
        player = self.hands[self.play]
        candidates = [idx for idx in player if self.deck[idx].figure not in {"7", "A", "10"}]
        if len(candidates) == 0:
            return pop_from(player)
        play = random.choice(candidates)
        return player.pop(player.index(play))

    def switch_player(self):
        self.play = abs(self.play - 1)

    def trick(self):
        table = []  # type: List[int]
        if self.play is None:
            self.play = self.lead = 0
        else:
            self.play = self.lead
        play = self.initiate()
        table.append(play)
        for rnd in range(1, 8):
            self.switch_player()
            play = self.attack(self.deck[play])
            table.append(play)
            deff = self.deck[table[0]]
            off = self.deck[table[-1]]
            if off.figure == "7" or off.figure == deff.figure:
                self.lead = self.play
                continue
            if rnd % 2 == 0:
                self.switch_player()
                throw = self.throw()
                table.append(throw)
            break
        self.wins[self.lead].extend(table)

    def game(self):
        self.deal()
        while self.hands[0] or self.hands[1]:
            self.trick()
            self.pull()
        scores = (
            sum(self.deck[card].figure in {"A", "10"} for card in self.wins[0]),
            sum(self.deck[card].figure in {"A", "10"} for card in self.wins[1])
        )
        if scores[0] == scores[1]:
            print("Draw!")
            return
        winner = int(scores[1] > scores[0])
        print("Player {} won {}:{}".format(winner, *scores))


if __name__ == '__main__':
    lard = LardGame()
    lard.game()

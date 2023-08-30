import random
from typing import List
from operator import attrgetter

DEBUG = False


class Player:
    def __init__(self, dice_pool :int, number :int):
        self.dice_pool = dice_pool
        self.number = number
        self.rolled = ["⬜" * self.dice_pool]
        self.bamboos = 0
        self.pandas = 0
        self.waters = 0
        self.stats = {"bamboos": 0, "pandas": 0, "waters": 0}

    def roll(self):
        D = Dice()
        self.rolled = []
        for i in range(self.dice_pool):
            self.rolled.append(D.roll())
        self.bamboos = self.rolled.count("🎋")
        #     self.stats[]
        self.pandas = self.rolled.count("🐼")
        self.waters = self.rolled.count("💧")

    def add_dice(self, num: int):
        self.dice_pool += num
        for i in range(num):
            self.rolled.append(Dice.get_icon("add"))

    def remove_dice(self, num: int, type: str):
        while type in self.rolled:
            self.rolled.remove(type)
        self.dice_pool -= num
        if self.dice_pool < 0:
            self.dice_pool = 0


class Dice:
    faces = ["⬜", "⬜", "⬜", "🐼", "🎋", "💧"]

    def roll(self):
        r = random.randint(0, 5)
        return self.faces[r]

    @staticmethod
    def get_icon(face: str) -> str:
        match face:
            case "blank":
                return "⬜"
            case "panda":
                return "🐼"
            case "bamboo":
                return "🎋"
            case "water":
                return "💧"
            case "add":
                return "➕"
            case _:
                return "error"


class Game:
    players: List[Player] = []
    lowest: Player = Player(6, -1)
    round: int = 0
    finished: bool = False
    winner: int = -1

    def __init__(self, n):
        self.nPlayers = n
        self.remaining = n
        if n < 4:
            dice = 6
        elif n == 4:
            dice = 5
        else:
            dice = 4
        for i in range(n):
            self.players.append(Player(dice, i))

    def play_round(self):
        if self.finished:
            print("The game is over.")
            return
        for i, p in enumerate(self.players):
            p.roll()
            self.print_state("before", i)
            self.update_dice(p)
            if (self.round == 0 and i > 0) or self.round > 0:
                self.bamboo_check(p, self.players[i - 1])
            self.update_lowest()
            self.print_state("after", i)
            winner = self.check_winner(p, self.players[i - 1])
            if winner is not None:
                print(f"The winner is player number {winner.number}")
                self.finished = True
                return
        self.round += 1

    def check_winner(self, current, previous):
        if self.lowest.dice_pool > 0:
            return None

        if self.lowest.number == previous.number:
            return previous
        else:
            return current

    def update_dice(self, player: Player, style: str = "lowest"):
        # print(player.dice_pool, "".join(player.rolled))
        player.remove_dice(player.waters, Dice.get_icon("water"))
        # print(player.dice_pool, "".join(player.rolled))

        if self.lowest.dice_pool == 0:
            self.lowest.add_dice(player.pandas)
        else:
            p = self.pick_player(player)
            p.add_dice(player.pandas)
        player.remove_dice(player.pandas, Dice.get_icon("panda"))
        # print(player.dice_pool, "".join(player.rolled))

    def update_lowest(self) -> None:
        self.lowest = min(self.players, key=attrgetter("dice_pool"))

    def bamboo_check(self, current: Player, previous: Player) -> None:
        delta = previous.bamboos - current.bamboos
        if delta > 0:
            if DEBUG:
                print(f"{previous.number} gave {delta} dice to {current.number}")
            current.add_dice(delta)
            previous.remove_dice(delta, Dice.get_icon("bamboo"))
            # print(current.dice_pool, "".join(current.rolled))

    def pick_player(self, player) -> Player:
        i = random.randint(0, self.nPlayers - 1)
        while i == player.number:
            i = random.randint(0, (self.nPlayers - 1))
        return self.players[i]

    def print_state(self, step: str, number: int) -> None:
        row = [self.round, number, step]
        format_string = "{:<3}{:<3}{:<7}"
        for p in self.players:
            format_string += "{:^15}"
            row.append("".join(p.rolled))
        # print(row)
        print(format_string.format(*row))


def main():
    G = Game(3)
    while not G.finished:
        G.play_round()


if __name__ == "__main__":
    main()

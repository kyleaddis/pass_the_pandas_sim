import random
from typing import List
from operator import attrgetter

DEBUG = False


class Player:
    def __init__(self, dice_pool: int, number: int):
        self.dice_pool = dice_pool
        self.number = number
        self.rolled = ["⬜" * self.dice_pool]
        self.bamboos = 0
        self.pandas = 0
        self.waters = 0
        self.roll_stats = {"bamboos": 0, "pandas": 0, "waters": 0, "blanks": 0}

    def roll(self):
        D = Dice()
        self.rolled = []
        for i in range(self.dice_pool):
            self.rolled.append(D.roll())
        self.update_stats(self.rolled)

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

    def update_stats(self, rolled_dice: List[str]):
        self.bamboos = rolled_dice.count("🎋")
        self.roll_stats["bamboos"] += self.bamboos
        self.pandas = rolled_dice.count("🐼")
        self.roll_stats["pandas"] += self.pandas
        self.waters = rolled_dice.count("💧")
        self.roll_stats["waters"] += self.waters
        self.roll_stats["blanks"] += rolled_dice.count("⬜")


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
    def __init__(self, n: int, print_rounds: bool):
        self.players: List[Player] = []
        self.lowest: Player = Player(6, -1)
        self.round: int = 0
        self.finished: bool = False
        self.winner: int = -1
        self.print_rounds = print_rounds
        self.nPlayers = n
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
                self.winner = winner
                return
        self.round += 1

    def check_winner(self, current: Player, previous: Player) -> Player:
        if self.lowest.dice_pool > 0:
            return None

        if self.lowest.number == previous.number:
            return previous
        else:
            return current

    def update_dice(self, player: Player, style: str = "lowest"):
        player.remove_dice(player.waters, Dice.get_icon("water"))

        if self.lowest.dice_pool == 0:
            self.lowest.add_dice(player.pandas)
        else:
            p = self.pick_player(player)
            p.add_dice(player.pandas)
        player.remove_dice(player.pandas, Dice.get_icon("panda"))

    def update_lowest(self) -> None:
        self.lowest = min(self.players, key=attrgetter("dice_pool"))

    def bamboo_check(self, current: Player, previous: Player) -> None:
        delta = previous.bamboos - current.bamboos
        if delta > 0:
            if DEBUG:
                print(f"{previous.number} gave {delta} dice to {current.number}")
            current.add_dice(delta)
            previous.remove_dice(delta, Dice.get_icon("bamboo"))

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
        if self.print_rounds:
            print(format_string.format(*row))


class Simulation:
    def __init__(self, n_players: int, n_games: int) -> None:
        self.n_players = n_players
        self.n_games = n_games
        self.log = []
        self.winner_count = [0] * n_players

    def simulate(self):
        for i in range(self.n_games):
            G = Game(self.n_players, False)
            while not G.finished:
                G.play_round()
            self.log.append([G.winner.number, G.round])
            self.winner_count[G.winner.number] += 1


def main():
    Sim = Simulation(6, 10000)
    Sim.simulate()
    print(Sim.winner_count)


if __name__ == "__main__":
    main()

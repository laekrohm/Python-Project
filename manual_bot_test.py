import logging
from basic_bot import BaseBot, MOVE_FORWARD, TURN_RIGHT, MOVE_BACKWARD, TURN_LEFT


TranslateMovements = {
    "W": MOVE_FORWARD,
    "A":TURN_LEFT,
    "S":MOVE_BACKWARD,
    "D":TURN_RIGHT
}

class ManualBot(BaseBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def next_move(self):
        for line in self.scan:
            print(line)
        moves = ""
        while moves not in ["W", "A", "S", "D"]:
            moves = input("Please enter a move(W; A; S; D): ").strip().upper()

        n = len(self.scan)
        middle = n//2
        inFront = self.scan[middle-1][middle]
        if inFront == "~" or inFront == "#" or inFront == "X":
            print(f"'{inFront*3}' blocks you, take another path.")
        return TranslateMovements[moves]

    #def recv_warning(self):


if __name__ == "__main__":
    bot = ManualBot()
    bot.run()



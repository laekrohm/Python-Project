import logging
import random
from basic_bot import BaseBot

OPPOSITE = {"^": "v", "v": "^", "<": ">", ">": "<"}

class AggressiveRumbleBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.last_scan = None
        self.repeat_counter = 0
        self.last_move = None
        self.escape_mode = False
        self.wall_follow_dir = "<"   # links-Hand-Regel

    # =========================
    # Wanddistanz (lokal)
    # =========================
    def wall_distance(self, scan, y, x, dy, dx):
        d = 0
        while 0 <= y < len(scan) and 0 <= x < len(scan):
            if scan[y][x] == "X":
                return d
            y += dy
            x += dx
            d += 1
        return d

    async def next_move(self):
        scan = self.scan
        c = len(scan) // 2

        BLOCKING = {"X", "#", "W", "R", "~"} | set("ABCDEFGH")

        # =========================
        # 0️⃣ Wiederholung erkennen
        # =========================
        key = tuple(scan)
        if key == self.last_scan:
            self.repeat_counter += 1
        else:
            self.repeat_counter = 0
        self.last_scan = key

        # 🔴 Escape-Mode aktivieren
        if self.repeat_counter >= 3:
            self.escape_mode = True

        # =========================
        # 1️⃣ SCHIESSEN
        # =========================
        for y in range(c - 1, -1, -1):
            if scan[y][c] == "X":
                break
            if scan[y][c].isalpha():
                self.last_move = "f"
                return "f"

        # =========================
        # 2️⃣ ESCAPE-MODE (WALL FOLLOWER)
        # =========================
        if self.escape_mode:
            # Reihenfolge: links → vor → rechts → zurück
            checks = [
                ("<", scan[c][c - 1]),
                ("^", scan[c - 1][c]),
                (">", scan[c][c + 1]),
                ("v", scan[c + 1][c]),
            ]

            for move, cell in checks:
                if cell not in BLOCKING:
                    self.last_move = move
                    self.repeat_counter = 0
                    # Wenn wieder Platz da ist → raus aus Escape
                    if sum(cell2 != "X" for row in scan for cell2 in row) > 15:
                        self.escape_mode = False
                    return move

            # absoluter Notfall
            return "<"

        # =========================
        # 3️⃣ NORMALMODUS (Anti-Shrink)
        # =========================
        moves = []
        if scan[c - 1][c] not in BLOCKING:
            moves.append("^")
        if scan[c + 1][c] not in BLOCKING:
            moves.append("v")
        if scan[c][c - 1] not in BLOCKING:
            moves.append("<")
        if scan[c][c + 1] not in BLOCKING:
            moves.append(">")

        if not moves:
            return random.choice(["<", ">"])

        # Anti-Pendel
        if self.last_move:
            moves = [m for m in moves if m != OPPOSITE.get(self.last_move)] or moves

        # Bewertung: weg von X
        def score(m):
            if m == "^":
                return self.wall_distance(scan, c - 1, c, -1, 0)
            if m == "v":
                return self.wall_distance(scan, c + 1, c, 1, 0)
            if m == "<":
                return self.wall_distance(scan, c, c - 1, 0, -1)
            if m == ">":
                return self.wall_distance(scan, c, c + 1, 0, 1)
            return 0

        best = max(moves, key=score)
        self.last_move = best
        return best


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    AggressiveRumbleBot().run()

import logging
from basic_bot import BaseBot
import asyncio

RIGHT = {"^": ">", ">": "v", "v": "<", "<": "^"}
LEFT  = {v: k for k, v in RIGHT.items()}
BACK  = {"^": "v", "v": "^", "<": ">", ">": "<"}

class WallFollowerBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.dir = "^"            # aktuelle Fahrtrichtung
        self.just_turned = False  # Marker für Richtungswechsel

    async def next_move(self):
        await asyncio.sleep(0.1)
        scan = self.scan
        size = len(scan)
        c = size // 2
        BLOCK = {"X", "#", "W", "R", "~"}

        # ==================================================
        # 🚨 KOLLISIONS-FIX (ORTHOGONAL, ABER ECKENSICHER)
        # ==================================================

        BLOCK = {"X", "#", "W", "R", "~"}

        def free(y, x):
            return scan[y][x] not in BLOCK and not scan[y][x].isalpha()

        # 1️⃣ Gegner vor oder hinter uns (vertikal)
        if scan[c - 1][c].isalpha() or scan[c + 1][c].isalpha():
            options = []
            if free(c, c + 1):
                options.append(">")
            if free(c, c - 1):
                options.append("<")

            if options:
                return options[0]  # nur ausweichen, wenn möglich

        # 2️⃣ Gegner links oder rechts von uns (horizontal)
        if scan[c][c - 1].isalpha() or scan[c][c + 1].isalpha():
            options = []
            if free(c - 1, c):
                options.append("^")
            if free(c + 1, c):
                options.append("v")

            if options:
                return options[0]
        # ==================================================
        # 🔫 SCHIESSEN (höchste Priorität)
        # ==================================================

        # 1️⃣ Einmal schießen nach Richtungswechsel
        if self.just_turned:
            self.just_turned = False
            return "f"

        # 2️⃣ Schießen, wenn Bot in Fahrtrichtung sichtbar ist
        if self.dir == "^":
            for y in range(c - 1, -1, -1):
                cell = scan[y][c]
                if cell == "X":
                    break
                if cell.isalpha():
                    return "f"

        elif self.dir == "v":
            for y in range(c + 1, size):
                cell = scan[y][c]
                if cell == "X":
                    break
                if cell.isalpha():
                    return "f"

        elif self.dir == "<":
            for x in range(c - 1, -1, -1):
                cell = scan[c][x]
                if cell == "X":
                    break
                if cell.isalpha():
                    return "f"

        elif self.dir == ">":
            for x in range(c + 1, size):
                cell = scan[c][x]
                if cell == "X":
                    break
                if cell.isalpha():
                    return "f"

        # ==================================================
        # 🧱 WALL-FOLLOWER (Rechts-Hand-Regel)
        # ==================================================
        def free(d):
            y, x = {
                "^": (c-1, c),
                "v": (c+1, c),
                "<": (c, c-1),
                ">": (c, c+1),
            }[d]
            cell = scan[y][x]
            return cell not in BLOCK and not cell.isalpha()

        for d in [RIGHT[self.dir], self.dir, LEFT[self.dir], BACK[self.dir]]:
            if free(d):
                if d != self.dir:
                    self.just_turned = True   # Richtungswechsel merken
                self.dir = d
                return d

        # Fallback (sollte praktisch nie passieren)
        return "<"


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    WallFollowerBot().run()
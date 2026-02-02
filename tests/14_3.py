import logging
import random
from basic_bot import BaseBot

# Richtungsabbildungen
LEFT  = {"^": "<", "<": "v", "v": ">", ">": "^"}
RIGHT = {v: k for k, v in LEFT.items()}
BACK  = {"^": "v", "v": "^", "<": ">", ">": "<"}

BLOCK = {"X", "#", "W", "R", "~"} | set("ABCDEFGH")


class WallSearchRumbleBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.dir = "^"                 # aktuelle Blickrichtung
        self.last_scan = None
        self.repeat_counter = 0
        self.min_wall_dist = None      # Shrink-Erkennung

    # --------------------------------------------------
    # Hilfsfunktionen
    # --------------------------------------------------
    def free(self, scan, c, move):
        if move == "^": return scan[c-1][c] not in BLOCK
        if move == "v": return scan[c+1][c] not in BLOCK
        if move == "<": return scan[c][c-1] not in BLOCK
        if move == ">": return scan[c][c+1] not in BLOCK
        return False

    def clear_path(self, scan, y1, x1, y2, x2):
        if y1 == y2:
            step = 1 if x2 > x1 else -1
            for x in range(x1 + step, x2, step):
                if scan[y1][x] == "X":
                    return False
            return True
        if x1 == x2:
            step = 1 if y2 > y1 else -1
            for y in range(y1 + step, y2, step):
                if scan[y][x1] == "X":
                    return False
            return True
        return False

    # 🔥 KORREKT: Kann mich ein Gegner IM NÄCHSTEN TICK treffen?
    def enemy_can_hit_next_tick(self, scan, c):
        size = len(scan)

        for y in range(size):
            for x in range(size):
                if (y, x) == (c, c):
                    continue
                if not scan[y][x].isalpha():
                    continue

                dy = c - y
                dx = c - x

                # gleiche Spalte
                if x == c and dy > 0:
                    if self.clear_path(scan, y, x, c, c):
                        return True

                # gleiche Zeile
                if y == c and dx > 0:
                    if self.clear_path(scan, y, x, c, c):
                        return True

        return False

    # Abstand zur nächsten X-Wand (Shrink-Erkennung)
    def nearest_wall_dist(self, scan, c):
        size = len(scan)
        best = size
        for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
            y, x = c, c
            d = 0
            while 0 <= y < size and 0 <= x < size:
                if scan[y][x] == "X":
                    best = min(best, d)
                    break
                y += dy
                x += dx
                d += 1
        return best

    # --------------------------------------------------
    # Hauptlogik
    # --------------------------------------------------
    async def next_move(self):
        scan = self.scan
        size = len(scan)
        c = size // 2

        # ========= Stillstand erkennen =========
        key = tuple(scan)
        if key == self.last_scan:
            self.repeat_counter += 1
        else:
            self.repeat_counter = 0
        self.last_scan = key

        # ========= Arena-Shrink erkennen =========
        wall_dist = self.nearest_wall_dist(scan, c)
        if self.min_wall_dist is None:
            self.min_wall_dist = wall_dist

        shrink = wall_dist < self.min_wall_dist
        self.min_wall_dist = min(self.min_wall_dist, wall_dist)

        # ========= 1️⃣ SCHIESSEN =========
        for y in range(c - 1, -1, -1):
            if scan[y][c] == "X":
                break
            if scan[y][c].isalpha():
                return "f"

        # ========= 2️⃣ AUSWEICHEN (NUR echte Treffergefahr) =========
        if self.enemy_can_hit_next_tick(scan, c):
            # orthogonal zur Schusslinie
            for move in ["<", ">", "^", "v"]:
                if self.free(scan, c, move):
                    self.dir = move
                    return move

        # ========= 3️⃣ SHRINK → RAUM GEWINNEN =========
        if shrink:
            moves = [m for m in ["^", "v", "<", ">"] if self.free(scan, c, m)]
            if moves:
                self.dir = random.choice(moves)
                return self.dir

        # ========= 4️⃣ WALL-FOLLOWER (RECHTS-HAND) =========
        for move in [
            RIGHT[self.dir],
            self.dir,
            LEFT[self.dir],
            BACK[self.dir]
        ]:
            if self.free(scan, c, move):
                self.dir = move
                return move

        # ========= 5️⃣ NOTFALL =========
        return random.choice(["<", ">"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    WallSearchRumbleBot().run()

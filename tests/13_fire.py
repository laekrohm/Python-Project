import logging
import time
from basic_bot import BaseBot
import asyncio

LEFT_TURN = {
    "^": "<",
    "<": "v",
    "v": ">",
    ">": "^"
}

RIGHT_TURN = {v: k for k, v in LEFT_TURN.items()}
BACK = {
    "^": "v",
    "v": "^",
    "<": ">",
    ">": "<"
}


class WallSearchRumbleBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.dir = "^"                 # Startblickrichtung
        self.last_shot_time = 0.0      # für 2-Sekunden-Schüsse
        self.just_turned = False       # Richtungswechsel-Marker

    async def next_move(self):
        await asyncio.sleep(0.1)
        scan = self.scan
        c = len(scan) // 2
        now = time.time()

        BLOCKING = {"X", "#", "W", "R", "~"} | set("ABCDEFGH")

        # =========================
        # 🔫 0️⃣ SCHIESSEN (Priorität)
        # =========================

        # Alle 2 Sekunden automatisch
        if now - self.last_shot_time >= 3:
            self.last_shot_time = now
            return "f"

        # Einmal schießen nach Richtungswechsel
        if self.just_turned:
            self.just_turned = False
            self.last_shot_time = now
            return "f"

        # Gegner in Blickrichtung (nach oben, da links-Hand-Follower)
        if self.dir == "^":
            for y in range(c - 1, -1, -1):
                if scan[y][c] == "X":
                    break
                if scan[y][c].isalpha():
                    self.last_shot_time = now
                    return "f"

        # =========================
        # 🧱 1️⃣ WALL-FOLLOWER (links-Hand)
        # =========================
        def cell_free(direction):
            if direction == "^":
                return scan[c - 1][c] not in BLOCKING
            if direction == "v":
                return scan[c + 1][c] not in BLOCKING
            if direction == "<":
                return scan[c][c - 1] not in BLOCKING
            if direction == ">":
                return scan[c][c + 1] not in BLOCKING

        # Priorität: links → vorne → rechts → zurück
        left = LEFT_TURN[self.dir]
        if cell_free(left):
            self.dir = left
            self.just_turned = True
            return left

        if cell_free(self.dir):
            return self.dir

        right = RIGHT_TURN[self.dir]
        if cell_free(right):
            self.dir = right
            self.just_turned = True
            return right

        back = BACK[self.dir]
        self.dir = back
        self.just_turned = True
        return back


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    WallSearchRumbleBot().run()

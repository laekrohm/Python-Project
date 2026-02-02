import logging
from basic_bot import BaseBot

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
        self.dir = "^"   # Startblickrichtung

    async def next_move(self):
        scan = self.scan
        c = len(scan) // 2

        BLOCKING = {"X", "#", "W", "R", "~"} | set("ABCDEFGH")

        # =========================
        # 1️⃣ SCHIESSEN (immer Priorität)
        # =========================
        for y in range(c - 1, -1, -1):
            if scan[y][c] == "X":
                break
            if scan[y][c].isalpha():
                return "f"

        # =========================
        # 2️⃣ WALL-FOLLOWER (links-Hand)
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
            return left

        if cell_free(self.dir):
            return self.dir

        right = RIGHT_TURN[self.dir]
        if cell_free(right):
            self.dir = right
            return right

        back = BACK[self.dir]
        self.dir = back
        return back


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    WallSearchRumbleBot().run()

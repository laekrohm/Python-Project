import logging
from basic_bot import BaseBot

RIGHT = {"^": ">", ">": "v", "v": "<", "<": "^"}
LEFT  = {v: k for k, v in RIGHT.items()}
BACK  = {"^": "v", "v": "^", "<": ">", ">": "<"}


class FinalDownwardSweepBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.mode = "SWEEP"              # SWEEP | WALL
        self.dir = "v"                   # aktuelle Richtung (für WALL)
        self.side = ">"                  # Spaltenrichtung im Sweep
        self.last_move = None
        self.just_vertical_escape = False
        self.bot_contact_ticks = 0

    async def next_move(self):
        scan = self.scan
        c = len(scan) // 2
        BLOCKING = {"X", "#", "W", "R", "~"} | set("ABCDEFGH")

        def free(d):
            return {
                "^": scan[c-1][c],
                "v": scan[c+1][c],
                "<": scan[c][c-1],
                ">": scan[c][c+1],
            }[d] not in BLOCKING

        up, down, left, right = map(lambda d: not free(d), ["^", "v", "<", ">"])

        # ==================================================
        # 🔒 0️⃣ VERTIKAL-OSZILLATION-FIX (höchste Priorität)
        # ==================================================
        if self.just_vertical_escape:
            self.just_vertical_escape = False
            if free(">"):
                self.last_move = ">"
                return ">"
            if free("<"):
                self.last_move = "<"
                return "<"

        # ==================================================
        # 🤖 1️⃣ BOT-KONTAKT → ORTHOGONALE TRENNUNG
        # ==================================================
        side_bot = scan[c][c-1].isalpha() or scan[c][c+1].isalpha()
        vert_bot = scan[c-1][c].isalpha() or scan[c+1][c].isalpha()

        if side_bot:
            if free("v"):
                self.just_vertical_escape = True
                self.last_move = "v"
                return "v"
            if free("^"):
                self.just_vertical_escape = True
                self.last_move = "^"
                return "^"

        if vert_bot:
            if free(">"):
                self.last_move = ">"
                return ">"
            if free("<"):
                self.last_move = "<"
                return "<"

        # ==================================================
        # 🔁 2️⃣ BOT-SYMMETRIEBRECHER (Cooldown)
        # ==================================================
        if side_bot or vert_bot:
            self.bot_contact_ticks += 1
        else:
            self.bot_contact_ticks = 0

        if self.bot_contact_ticks >= 2:
            self.mode = "WALL"
            self.dir = ">" if free(">") else "<"
            self.bot_contact_ticks = 0
            self.last_move = self.dir
            return self.dir

        # ==================================================
        # 🔴 3️⃣ ECKENERKENNUNG → WALL-FOLLOWER
        # ==================================================
        if self.mode == "SWEEP" and (
            (up and left) or (up and right) or
            (down and left) or (down and right)
        ):
            self.mode = "WALL"
            self.dir = ">" if left else "<"
            self.last_move = self.dir
            return self.dir

        # ==================================================
        # 🧱 4️⃣ WALL-FOLLOWER (rechts-Hand-Regel)
        # ==================================================
        if self.mode == "WALL":
            for d in [RIGHT[self.dir], self.dir, LEFT[self.dir], BACK[self.dir]]:
                if free(d):
                    self.dir = d
                    # zurück in Sweep, wenn nicht mehr am Rand
                    if not up and not left and not right:
                        self.mode = "SWEEP"
                    self.last_move = d
                    return d

        # ==================================================
        # ⬇️ 5️⃣ SWEEP-MODUS (Downward-first)
        # ==================================================
        if free("v"):
            self.last_move = "v"
            return "v"

        if self.side == ">" and free(">"):
            self.last_move = ">"
            return ">"
        if self.side == "<" and free("<"):
            self.last_move = "<"
            return "<"

        self.side = "<" if self.side == ">" else ">"
        self.last_move = self.side
        return self.side


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    FinalDownwardSweepBot().run()


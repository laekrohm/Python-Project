import logging
import asyncio
from basic_bot import BaseBot, MOVE_FORWARD, TURN_LEFT, MOVE_BACKWARD, TURN_RIGHT

TranslateMovements = {
    "W": MOVE_FORWARD,
    "A":TURN_LEFT,
    "S":MOVE_BACKWARD,
    "D":TURN_RIGHT
}
""" 32 x-Achse, 32 y-Achse, (o is on x=16, y=16 always)"""

"""TESTS:   1. max range 30: 6/10 (roughly 60 moves average) 
            2. max range 28: 9/10 (roughly 62 moves average)
            3. max range 27: 
            4. max range 26: 6/10 (roughly 29 moves average)
            5. max range 24: 5/10 (roughly 70 moves average)
            6. max range 22: 2/10 (roughly 35 moves average)
            7. max range 16: 1/10 (roughly 11 moves average)
            8. max range 10: 4/10 (roughly 21 moves average)
            38 is also really good"""

class EscapeBot(BaseBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rocket = "o"
        self.moves_made= 0
        self.move_limit = 28
        self.x_rocket = -1
        self.y_rocket = -1

        self.debug_square_repeat_pattern = 0

    async def next_move(self):
        await asyncio.sleep(0.01)
        n = len(self.scan)
        middle = n // 2

        inFront = self.scan[middle - 1][middle]
        rocket_found = any(self.rocket in row for row in self.scan)
        self.moves_made += 1

        # 1. ESCAPE HATCH (If stuck spinning)
        if self.debug_square_repeat_pattern >= 4:
            self.debug_square_repeat_pattern = 0
            self.moves_made = 0
            return TURN_RIGHT

        # 2. ROCKET SEEKING
        if rocket_found:
            self.moves_made = 0  # Reset search timer because we found the goal!
            for y, row in enumerate(self.scan):
                if self.rocket in row:
                    rocket_y, rocket_x = y, row.find(self.rocket)
                    break

            if rocket_x < (middle - 1):
                return TURN_LEFT
            elif rocket_x > (middle + 2):
                return TURN_RIGHT
            else:  # Centered
                if rocket_y < middle:  # In front
                    if inFront == "." or inFront == self.rocket:
                        return MOVE_FORWARD
                    else:
                        self.debug_square_repeat_pattern += 1
                        return TURN_RIGHT
                else:  # Behind
                    return TURN_LEFT

        # 3. SEARCHING (No rocket found)
        if self.moves_made >= self.move_limit:
            self.moves_made = 0
            return TURN_LEFT

        if inFront == ".":
            return MOVE_FORWARD  # This makes the bot actually walk!

        return TURN_RIGHT  # If a wall is in front, turn


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    bot = EscapeBot()
    bot.run()





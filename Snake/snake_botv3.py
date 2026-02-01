import logging
import asyncio
from basic_bot import BaseBot, MOVE_FORWARD, TURN_LEFT, MOVE_BACKWARD, TURN_RIGHT
"""
Strategy for winning,
    Should move in a pattern to maximize collection of fossils, 
    so start is ofc random everytime sadly, but we still  know
    how many "squares" are in a row, and we just tell him
    hey, go the whole range, than do a 180 turn around, 
    and go the next row, then the next row
"""

TranslateMovements = {
    "W": MOVE_FORWARD,
    "A":TURN_LEFT,
    "S":MOVE_BACKWARD,
    "D":TURN_RIGHT
}

class SnakeBot(BaseBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.step = "."
        self.fossil = "@"
        self.moves_made = 0
        self.maximum_moves = 32

    async def next_move(self):
        await asyncio.sleep(0.1)
        for line in self.scan:
            print(line)

        n = len(self.scan)
        middle = n // 2
        robo_front_view = self.scan[middle-1][middle]
        robo_back_view = self.scan[middle+1][middle]
        robo_left_view = self.scan[middle][middle+1]
        robo_right_view = self.scan[middle][middle-1]

#1. we first check if there is a self scan.
#2. if it is true we check if the next step is . or @
#3. if this is also true, we count 1 step, all of them will add to the limit
#4.therefore we check, and while te limit is not achieved we take a next
#step forward, hint return move forward
#5. when the moves made are the limit we return right,
# so we change the pattern of moving forward
#6.we set the moves made to 6 so the process can be repeated
#7.In the end, we turn right

        if self.scan:
            if robo_front_view == self.step or robo_front_view == self.fossil:
                self.moves_made += 1
                if self.moves_made <= self.maximum_moves:
                    return MOVE_FORWARD
                elif self.moves_made == self.maximum_moves:
                    return TURN_RIGHT
                self.moves_made = 0
                if robo_front_view == self.fossil:
                    return TURN_RIGHT
                return TURN_RIGHT
            return MOVE_FORWARD
        return TURN_RIGHT

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    bot = SnakeBot()
    bot.run()


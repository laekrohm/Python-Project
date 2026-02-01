import logging
import random
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
'''
PSEUDO CODE:
    if step(.) is in front MOVE_FORWARD:
        if fossil is in front MOVE_FORWARD:
'''


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


    async def next_move(self):
        await asyncio.sleep(0.01)
        for line in self.scan:
            print(line)
        n = len(self.scan)
        middle = n // 2
        robo_front_view = self.scan[middle-1][middle]
        robo_back_view = self.scan[middle+1][middle]
        robo_left_view = self.scan[middle+1][middle]
        robo_right_view = self.scan[middle-1][middle]


        if self.scan:
            if robo_front_view == self.step or robo_front_view == self.fossil:
                if (robo_front_view == self.fossil and robo_front_view != self.step) and (robo_right_view == self.fossil and robo_right_view != self.step ):
                    return TURN_RIGHT
                return MOVE_FORWARD
            return TURN_RIGHT




if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    bot = SnakeBot()
    bot.run()




        #if inFront == "~" or inFront == "#" or inFront == "X":
            #print(f"'{inFront * 3}' blocks you, take another path.")
        #return TranslateMovements[self.moves]


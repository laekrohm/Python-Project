import logging
import asyncio
from basic_bot import BaseBot, MOVE_FORWARD, TURN_LEFT, MOVE_BACKWARD, TURN_RIGHT



#TOMORROW TRYING BREADTH FIRST SEARCH IN FORM OF U
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
        for line in self.scan:
            print(line)

        n = len(self.scan)
        middle = n // 2

        inFront = self.scan[middle - 1][middle]
        onLeft = self.scan[middle][middle-1]
        onRight = self.scan[middle][middle+1]
        behind = self.scan[middle+1][middle]

        rocket_found = any(self.rocket in row for row in self.scan)

        self.moves_made += 1

        if self.debug_square_repeat_pattern >= 4:
            self.debug_square_repeat_pattern = 0
            #self.moves_made = 0
            return TURN_RIGHT

        if rocket_found:
            for y, row in enumerate(self.scan):
                if self.rocket in row:
                    rocket_y = y
                    rocket_x = row.find(self.rocket)
                    break
            if rocket_x < middle:
                self.debug_square_repeat_pattern += 1 #test
                return TURN_LEFT
            #""" Changed moves made to +2 (16+2 for example),
            #it doesn't seem to affect anything though"""
            #if rocket_x > middle:
                #self.moves_made += 2
                #return TURN_RIGHT
            else:
                if rocket_y < middle:
                    self.debug_square_repeat_pattern += 1 #test
                    return MOVE_FORWARD
                else:
                    return TURN_LEFT
        if self.moves_made >= self.move_limit:
            self.moves_made = 0
            return TURN_LEFT

        if inFront == "." or inFront == self.rocket:
            return MOVE_FORWARD


        #-------Trying Strategy for left, right, back
        #if onLeft == "." or onLeft == self.rocket:
            #return TURN_LEFT
        #if onRight == "." or onRight == self.rocket:
            #return TURN_RIGHT
        #if behind == "." or behind == self.rocket:
            #return MOVE_BACKWARD

        return TURN_RIGHT

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    bot = EscapeBot()
    bot.run()




        #if inFront == "~" or inFront == "#" or inFront == "X":
            #print(f"'{inFront * 3}' blocks you, take another path.")
        #return TranslateMovements[self.moves]


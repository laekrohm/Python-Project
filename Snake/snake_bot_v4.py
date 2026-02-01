import logging
import asyncio
from collections import deque
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
        self.turning_step = 0

    def bot_bfs_search(self, start_node, target_node, scan_data):
        """BFS: Finds quickest way, saves already visited paths"""
        n = len(scan_data)
        queue = deque([start_node])
        visited = {start_node}
        parent = {}

        while queue:
            curr = queue.popleft()
            if curr == target_node:
                #Change Path from backward to forward
                path = []
                while curr in parent:
                    path.append(curr)
                    curr = parent[curr]
                path.reverse()
                return path

            current_x, current_y = curr
            # Check neighbors (up, right, down, left)
            moves = [(0, -1), (1, 0), (0, 1), (-1, 0)]

            for dx, dy in moves:
                next_x, next_y = current_x + dx, current_y + dy

                # Check: On Grid?
                if 0 <= next_x < n and 0 <= next_y < n:
                    # Check: visited or not?
                    if (next_x, next_y) not in visited:
                        visited.add((next_x, next_y))
                        parent[(next_x, next_y)] = curr
                        queue.append((next_x, next_y))
        return None


    async def next_move(self):
        await asyncio.sleep(0.01)

        for line in self.scan:
            print(line)

        if not self.scan:
            return MOVE_FORWARD
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

        if self.turning_step == 0:
            if self.moves_made < self.maximum_moves:
                self.moves_made += 1
                return MOVE_FORWARD
            else:
                self.turning_step = 1
                return TURN_RIGHT
        elif self.turning_step == 1:
            self.turning_step = 2
            return MOVE_FORWARD
        elif self.turning_step == 2:
            self.turning_step = 3
            return TURN_LEFT
        elif self.turning_step == 3:
            self.turning_step = 0
            self.moves_made = 0
            return MOVE_FORWARD


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    bot = SnakeBot()
    bot.run()


import asyncio
import logging
import random
from collections import deque
from basic_bot import BaseBot, MOVE_FORWARD, TURN_LEFT, TURN_RIGHT, MOVE_BACKWARD


class EscapeBot(BaseBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_char = "o"

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

            curr_x, curr_y = curr
            # Check neighbors (up, right, down, left)
            moves = [(0, -1), (1, 0), (0, 1), (-1, 0)]

            for dx, dy in moves:
                nx, ny = curr_x + dx, curr_y + dy

                # Check: On Grid?
                if 0 <= nx < n and 0 <= ny < n:
                    # Check: visited or not?
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        parent[(nx, ny)] = curr
                        queue.append((nx, ny))
        return None

    async def next_move(self):
        """async method for next move, based on bfs, left, right, forward only"""
        await asyncio.sleep(0.1)

        for line in self.scan:
            print(line)

        if not self.scan:
            return MOVE_FORWARD

        n = len(self.scan)
        center = n // 2
        my_pos = (center, center)

        # 1. Target finding
        target_pos = None
        for y, row in enumerate(self.scan):
            for x, char in enumerate(row):
                if char == self.target_char:
                    target_pos = (x, y)
                    break
            if target_pos: break

        # 2. When target found -> bfs gives shortest path
        if target_pos:
            path = self.bot_bfs_search(my_pos, target_pos, self.scan)

            if path and len(path) > 0:
                next_step = path[0]  # next square, where we go
                nx, ny = next_step
                cx, cy = my_pos

                # Logic: how's the next square relative to my position which is always 3/3

                # Case A: Square one row above (smaller y-value)

                if ny < cy:
                    return MOVE_FORWARD

                # Case B: Square on my right (bigger x-value)
                elif nx > cx:
                    return TURN_RIGHT

                # Case C: square is on my left (smaller x-value)
                elif nx < cx:
                    return TURN_LEFT

                # Case D: Square under me (bigger y-value)
                elif ny > cy:
                    #left/ right doesn't matter
                    return TURN_RIGHT



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot = EscapeBot()
    bot.run()



"""
# 3. Wenn KEIN Ziel da ist oder kein Weg gefunden wurde -> Erkunden
        # Simple Logik: Wenn vorne frei ist, geh vorwärts. Sonst dreh dich.
        # scan[y][x] -> scan[center-1][center] ist das Feld direkt vor der Nase
        front_tile = self.scan[center - 1][center]

        if front_tile != '#':
            # Zufällig manchmal drehen, damit man nicht in Ecken hängen bleibt
            if random.random() < 0.1:
                return random.choice([TURN_LEFT, TURN_RIGHT])
            return MOVE_FORWARD
        else:
            # Wand vor der Nase -> Drehen
            return random.choice([TURN_LEFT, TURN_RIGHT])
"""

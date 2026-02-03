import logging
import asyncio
from collections import deque
import sys

# --- KONFIGURATION ---
TURN_LEFT = "<"
TURN_RIGHT = ">"
MOVE_FORWARD = "^"
MOVE_BACKWARD = "v"

class BaseBot:
    """Oberklasse für asynchrone Basis-Kommunikation mit dem Server."""

    def __init__(self, host="127.0.0.1", port=63187):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.scan = []

    async def connect(self):
        logging.info("Verbinde mit Server...")
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        except Exception as e:
            logging.error(f"Verbindungsfehler: {e}")
            sys.exit(-1)

    async def recv_scan(self):
        rows = []
        while True:
            try:
                line_bytes = await self.reader.readline()
                if not line_bytes: return None
                line = line_bytes.decode().strip()
                if not line: return None
                rows.append(line)
                if len(rows) > 0 and len(rows) >= len(rows[0]):
                    self.scan = rows[:len(rows[0])]
                    return self.scan
            except Exception:
                return None

    async def send_cmd(self, cmd):
        self.writer.write(cmd.encode())
        await self.writer.drain()

    async def close(self):
        if self.writer: self.writer.close()

    async def start(self):
        await self.connect()
        while True:
            if not await self.recv_scan(): break
            move = await self.next_move()
            if not move: break
            await self.send_cmd(move)
        await self.close()

    def next_move(self):
        raise NotImplementedError

    def run(self):
        asyncio.run(self.start())


class SnakeBot(BaseBot):
    def __init__(self, *args, **kwargs):
# Snake v9 führend mit alle fossilien gesammelt in 512 moves (5), in 509 moves (4), in 467 moves, in 488 moves(10), in 416 moves, in 462 moves (8)
#in 403 moves (12), in 444 moves (14)

        super().__init__(*args, **kwargs)
        self.fossil = "@"
        self.snake = "*"

        # Tracking
        self.history = []  # saving all made moves

        # settings for patroulling
        self.moves_made = 0
        self.maximum_moves = 32

        # Turn logic
        self.turning_step = 0
        self.turn_direction = "RIGHT"

        # after moving 32 moves turn right and move forward 10x, or 8x
        self.sideways_steps_needed = 10
        self.sideways_steps_done = 0
        #(8)-(10): 2-3

    def bot_bfs_search(self, start_node, target_node, scan_data):
        n = len(scan_data)
        queue = deque([start_node])
        visited = {start_node}
        parent = {}

        while queue:
            curr = queue.popleft()
            if curr == target_node:
                path = []
                while curr in parent:
                    path.append(curr)
                    curr = parent[curr]
                path.reverse()
                return path

            cx, cy = curr
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < n and 0 <= ny < n:
                    if (nx, ny) not in visited:
                        if scan_data[ny][nx] != self.snake or (nx, ny) == target_node:
                            visited.add((nx, ny))
                            parent[(nx, ny)] = curr
                            queue.append((nx, ny))
        return None

    def get_closest_fossil(self, my_pos):
        mx, my = my_pos
        targets = []
        for y, row in enumerate(self.scan):
            for x, char in enumerate(row):
                if char == self.fossil:
                    dist = abs(x - mx) + abs(y - my)
                    targets.append(((x, y), dist))

        if not targets: return None
        targets.sort(key=lambda k: k[1])
        return targets[0][0]

    def is_front_blocked(self):
        """Verifying the square straight in front of the snake."""
        n = len(self.scan)
        mid = n // 2
        front_y = mid - 1

        if front_y < 0: return True
        if self.scan[front_y][mid] == self.snake: return True
        return False

    async def next_move(self):
        await asyncio.sleep(0)
        if not self.scan: return None
        for line in self.scan:
            print(line)

        n = len(self.scan)
        mid = n // 2
        self.my_pos = (mid, mid)
        move_to_send = None

        # --- 1. Fossil Hunt---
        target_pos = self.get_closest_fossil(self.my_pos)

        #BFS with improved logic
        if target_pos:
            path = self.bot_bfs_search(self.my_pos, target_pos, self.scan)
            if path and len(path) > 0:
                next_x, next_y = path[0]
                curr_x, curr_y = self.my_pos

                # if fossil behind, turn around -> go to it
                if next_y > curr_y:
                    move_to_send = MOVE_BACKWARD
                elif next_y < curr_y:
                    move_to_send = MOVE_FORWARD
                elif next_x > curr_x:
                    move_to_send = TURN_RIGHT
                elif next_x < curr_x:
                    move_to_send = TURN_LEFT

        # --- 2. Pattrouling with 10 steps at a time
        if not move_to_send:
            move_to_send = self.get_patrol_move()

        # saving to history dict
        self.history.append(move_to_send)
        return move_to_send

    def get_patrol_move(self):
        blocked = self.is_front_blocked()

        # --- Step 0: the length of 32 moves
        if self.turning_step == 0:
            if self.moves_made < self.maximum_moves and not blocked:
                self.moves_made += 1
                return MOVE_FORWARD
            else:
                # 32 move finished, turn right/left
                self.turning_step = 1
                self.sideways_steps_done = 0  # Zähler für Seitenschritte resetten
                return TURN_RIGHT if self.turn_direction == "RIGHT" else TURN_LEFT

        # --- Step 1: walk 10 steps
        elif self.turning_step == 1:
            # turned 90 degrees
            # waling 10 steps to the side (of the map)

            #if front is blocked
            if blocked:
                self.turning_step = 2  # jump to last step
                # turn around to avoid crash in self
                return self.do_final_turn()

            # 5 steps made?
            if self.sideways_steps_done < self.sideways_steps_needed:
                self.sideways_steps_done += 1
                return MOVE_FORWARD
            else:
                # if 5 made, going in the main direction
                self.turning_step = 2
                return self.do_final_turn()

        # --- Step 2: End 180 turn
        elif self.turning_step == 2:
            return self.do_final_turn()

        return MOVE_FORWARD

    def do_final_turn(self):
        """leads to second turn and sets status back to normal."""
        self.turning_step = 0
        self.moves_made = 0

        cmd = TURN_RIGHT if self.turn_direction == "RIGHT" else TURN_LEFT

        # snake pattern movement
        if self.turn_direction == "RIGHT":
            self.turn_direction = "LEFT"
        else:
            self.turn_direction = "RIGHT"

        return cmd


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot = SnakeBot()
    bot.run()
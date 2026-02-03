import asyncio
from collections import deque
#from basic_bot import BaseBot, MOVE_FORWARD, TURN_LEFT, MOVE_BACKWARD, TURN_RIGHT

#import asyncio
import sys
import logging

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
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port
            )
        except ConnectionRefusedError:
            logging.error("Verbindung abgelehnt – Server läuft vermutlich nicht.")
            sys.exit(-1)
        except asyncio.TimeoutError:
            logging.error("Verbindungsversuch abgelaufen")
            sys.exit(-2)
        except OSError as e:
            logging.error(f"Netzwerkfehler: {e}")
            sys.exit(-3)
        except Exception as e:
            logging.error(f"Unbekannter Fehler: {e}")
            sys.exit(-4)
        logging.debug(f"Mit {self.host}:{self.port} verbunden.")

    async def recv_scan(self):
        """
        Non-blocking Version des Scan-Lesens mit readuntil().
        """
        logging.info("Empfange Scan...")
        rows = []

        while True:
            try:
                line_bytes = await self.reader.readline()

            except (asyncio.IncompleteReadError, ConnectionResetError):
                logging.info("Verbindung vom Server beendet.")
                self.scan = None
                return
            line = line_bytes.decode().strip()

            if not line:
                logging.info("Verbindung beendet.")
                self.scan = None
                return

            rows.append(line)
            logging.debug(f"{line} zu Scan hinzugefügt als {len(rows)}. Zeile.")

            # Sobald wir ein vollständiges Quadrat haben -> fertig
            n = len(rows[0])
            if len(rows) >= n:
                self.scan = rows[:n]
                logging.debug(f"Vollständiger Scan empfangen ({n}x{n}).")
                return self.scan

    async def send_cmd(self, cmd):
        logging.info(f"Sende Befehl: {cmd}")
        self.writer.write(cmd.encode())
        await self.writer.drain()

    async def close(self):
        logging.info("Schließe Verbindung...")
        try:
            self.writer.close()
            await self.writer.wait_closed()
        except Exception:
            pass

    async def start(self):
        msg = f"Starte {self.__class__.__name__}..."
        logging.info(msg)
        await self.connect()
        while True:
            await self.recv_scan()
            if not self.scan:
                logging.info("Keine Scan-Daten erhalten, beende Bot.")
                break

            next_move = await self.next_move()
            if not next_move:
                logging.info("Keine Bewegung ermittelt, beende Bot.")
                break
            try:
                await self.send_cmd(next_move)
            except ConnectionError:
                logging.info("Verbindung zum Server verloren, beende Bot.")
                break
        msg = f"Beende {self.__class__.__name__}..."
        logging.info(msg)
        await self.close()

    def next_move(self):
        """Muss in Unterklasse implementiert werden."""
        raise NotImplementedError

    def run(self):
        asyncio.run(self.start())




"""
Strategy for winning,
    Should move in a pattern to maximize collection of fossils, 
    so start is ofc random everytime sadly, but we still  know
    how many "squares" are in a row, and we just tell him
    hey, go the whole range, than do a 180 turn around, 
    and go the next row, then the next row, Well this doesnt work lol, 
    because we have a move limit of 512, its not enough to cover the whole map
"""

#Distance=∣x1−x2∣+∣y1−y2∣

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
        self.maximum_moves = 20
        self.turning_step = 0
        self.snake = "*"
        self.turn_direction = "RIGHT"

    def bot_bfs_search(self, start_node, target_node, scan_data):
        """BFS: Finds quickest way, saves already visited paths"""
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
                    # WICHTIG: Nur betreten, wenn es kein Körperteil ist (außer es ist das Ziel)
                    if (nx, ny) not in visited:
                        if scan_data[ny][nx] != self.snake or (nx, ny) == target_node:
                            visited.add((nx, ny))
                            parent[(nx, ny)] = curr
                            queue.append((nx, ny))
        return None

    async def next_move(self):
        await asyncio.sleep(0.01)
        if not self.scan:
            return MOVE_FORWARD

        for line in self.scan:
            print(line)
        n = len(self.scan)
        middle = n // 2
        self.my_pos = (middle, middle) #actual position, short viewed

        # 1. SEARCH LOGIC (Priority)
        target_pos = None
        for y, row in enumerate(self.scan):
            for x, char in enumerate(row):
                if char == self.fossil:
                    target_pos = (x, y)
                    break
            if target_pos: break

        if target_pos:
            path = self.bot_bfs_search(self.my_pos, target_pos, self.scan)
            if path:
                next_x, next_y = path[0]
                curr_x, curr_y = self.my_pos

                # Direct movement translation
                if next_y < curr_y: return MOVE_FORWARD
                if next_y > curr_y: return MOVE_BACKWARD
                if next_x > curr_x: return TURN_RIGHT
                if next_x < curr_x: return TURN_LEFT

        # 2. PATROL LOGIC (Fallback)
        # If no fossil was found, or BFS failed, perform the snake pattern
        return self.get_patrol_move()

    def get_patrol_move(self):
        mx, my = self.my_pos
        next_y = my - 1

        is_blocked = False
        if next_y < 0 or self.scan[next_y][mx] == self.snake:
            is_blocked = True

        if self.turning_step == 0:
            if self.moves_made < self.maximum_moves and not is_blocked:
                self.moves_made += 1
                return MOVE_FORWARD
            else:
                self.turning_step = 1
                # Wende einleiten basierend auf aktueller Schlangen-Richtung
                return TURN_RIGHT if self.turn_direction == "RIGHT" else TURN_LEFT

        elif self.turning_step == 1:
            self.turning_step = 2
            return MOVE_FORWARD  # Ein Schritt zur Seite

        elif self.turning_step == 2:
            self.turning_step = 3
            # Zweite Kurve in die GLEICHE Richtung, um die 180° voll zu machen
            return TURN_RIGHT if self.turn_direction == "RIGHT" else TURN_LEFT

        elif self.turning_step == 3:
            self.turning_step = 0
            self.moves_made = 0
            # WICHTIG: Nach der 180° Wende die Richtung für das NÄCHSTE Mal umkehren
            self.turn_direction = "LEFT" if self.turn_direction == "RIGHT" else "RIGHT"
            return MOVE_FORWARD

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    bot = SnakeBot()
    bot.run()



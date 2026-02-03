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
    """Deine funktionierende Basis-Klasse."""

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
        super().__init__(*args, **kwargs)
        self.fossil = "@"
        self.snake = "*"

        # Patrouillen-Einstellungen (Highscore Strategie)
        self.moves_made = 0
        self.maximum_moves = 32  # Dein erfolgreicher Wert
        self.turning_step = 0
        self.turn_direction = "RIGHT"

    def bot_bfs_search(self, start_node, target_node, scan_data):
        """Standard BFS."""
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
        """Verhindert Hin-und-Her Springen zwischen Fossilien."""
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
        """Prüft NUR das Feld direkt im Scan oben (y-1)."""
        # Annahme: Da Datei 1 funktioniert hat, ist 'vorne' im Scan meist y-1
        n = len(self.scan)
        mid = n // 2
        front_y = mid - 1

        if front_y < 0: return True  # Kartenende
        if self.scan[front_y][mid] == self.snake: return True
        return False

    async def next_move(self):
        await asyncio.sleep(0.01)
        if not self.scan: return None

        n = len(self.scan)
        mid = n // 2
        self.my_pos = (mid, mid)

        # --- 1. FOSSILIEN JAGD ---
        target_pos = self.get_closest_fossil(self.my_pos)

        if target_pos:
            path = self.bot_bfs_search(self.my_pos, target_pos, self.scan)
            if path and len(path) > 0:
                next_x, next_y = path[0]
                curr_x, curr_y = self.my_pos

                # Hier der 512-Move-Trick: Rückwärtsgang nutzen!
                # Da wir nicht wissen, wohin wir schauen, nutzen wir Relativ-Koordinaten des Scans.

                # Ziel ist hinter uns (im Scan unten)?
                if next_y > curr_y:
                    # Wenn wir Datei 1 Logik folgen:
                    # Wir wissen nicht ob wir gedreht sind.
                    # Aber wenn Fossil im Scan UNTEN ist, ist Rückwärts meist richtig.
                    return MOVE_BACKWARD

                if next_y < curr_y: return MOVE_FORWARD
                if next_x > curr_x: return TURN_RIGHT
                if next_x < curr_x: return TURN_LEFT

        # --- 2. PATROUILLE (Crash-Fix) ---
        return self.get_patrol_move()

    def get_patrol_move(self):
        # 1. Ist der Weg direkt vor mir blockiert?
        blocked = self.is_front_blocked()

        if self.turning_step == 0:
            # Geradeaus laufen
            if self.moves_made < self.maximum_moves and not blocked:
                self.moves_made += 1
                return MOVE_FORWARD
            else:
                # Hindernis oder Limit -> Wende einleiten
                self.turning_step = 1
                return TURN_RIGHT if self.turn_direction == "RIGHT" else TURN_LEFT

        elif self.turning_step == 1:
            self.turning_step = 2

            # CRASH FIX: Bevor wir den Schritt zur Seite machen, prüfen wir nochmal!
            # Wenn wir uns gedreht haben, ist vor uns vielleicht eine neue Wand (Ecke).
            if blocked:
                # Panik: Wir haben uns zur Wand gedreht.
                # Abbruch des Manövers, nochmal drehen (U-Turn komplettieren)
                self.turning_step = 0
                self.moves_made = 0
                return TURN_RIGHT if self.turn_direction == "RIGHT" else TURN_LEFT

            return MOVE_FORWARD

        elif self.turning_step == 2:
            self.turning_step = 0
            self.moves_made = 0

            # Richtung umkehren für nächstes Mal (Zick Zack)
            cmd = TURN_RIGHT if self.turn_direction == "RIGHT" else TURN_LEFT

            if self.turn_direction == "RIGHT":
                self.turn_direction = "LEFT"
            else:
                self.turn_direction = "RIGHT"

            return cmd

        return MOVE_FORWARD


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot = SnakeBot()
    bot.run()
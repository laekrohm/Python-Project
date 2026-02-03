import logging
import asyncio
from collections import deque
import sys



#____HIGHSCORES____#
#Bot 7: 31 mit 31 move_limit, 32 move_limit, 33 move_limit,
#Bot 7: 29
#Bot 6: 27
#Bot 7: 25
#Bot 7: 24
#Bot 7: 23
#Bot 6: 17
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

        # Patrol-Status
        self.moves_made = 0
        self.maximum_moves = 32  # Längere Bahnen laufen 22 Beste gewesen mit 25, 30
        self.turning_step = 0  # Wo im Wendemanöver sind wir?
        self.turn_direction = "RIGHT"  # Wir fangen mit Rechtskurven an

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
            # Standard-Nachbarn
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = cx + dx, cy + dy

                if 0 <= nx < n and 0 <= ny < n:
                    if (nx, ny) not in visited:
                        # Wir ignorieren den Körper ('*'), außer es ist das Ziel
                        if scan_data[ny][nx] != self.snake or (nx, ny) == target_node:
                            visited.add((nx, ny))
                            parent[(nx, ny)] = curr
                            queue.append((nx, ny))
        return None

    def get_closest_fossil(self, my_pos):
        """Findet das Fossil mit der geringsten Distanz, um Verwirrung zu vermeiden."""
        mx, my = my_pos
        targets = []

        for y, row in enumerate(self.scan):
            for x, char in enumerate(row):
                if char == self.fossil:
                    dist = abs(x - mx) + abs(y - my)
                    targets.append(((x, y), dist))

        if not targets:
            return None

        # Sortiere nach Distanz und gib das nächste zurück
        targets.sort(key=lambda k: k[1])
        return targets[0][0]

    async def next_move(self):
        await asyncio.sleep(0.01)
        if not self.scan: return None

        for line in self.scan:
            print(line)

        n = len(self.scan)
        mid = n // 2
        self.my_pos = (mid, mid)  # Wir sind immer in der Mitte des Arrays

        # 1. ZIELSUCHE (Verbessert: Nimm das NÄCHSTE Fossil)
        target_pos = self.get_closest_fossil(self.my_pos)

        # Wenn Fossil gefunden, navigiere hin (wie Datei 1, aber sauberer)
        if target_pos:
            path = self.bot_bfs_search(self.my_pos, target_pos, self.scan)

            if path and len(path) > 0:
                # Wohin geht der nächste Schritt im Array?
                next_x, next_y = path[0]
                curr_x, curr_y = self.my_pos

                # Relativ zum Bild entscheiden (Funktioniert immer!)
                if next_y < curr_y: return MOVE_FORWARD  # Ziel ist oben
                if next_x > curr_x: return TURN_RIGHT  # Ziel ist rechts
                if next_x < curr_x: return TURN_LEFT  # Ziel ist links
                if next_y > curr_y: return TURN_RIGHT  # Ziel ist hinter uns -> Umdrehen

        # 2. PATROUILLE (Zick-Zack statt Spirale)
        return self.get_patrol_move()

    def get_patrol_move(self):
        mx, my = self.my_pos

        # Blockiert Check: Ist vor mir (y-1) eine Wand oder Ende der Map?
        front_y = my - 1
        is_blocked = False
        if front_y < 0 or self.scan[front_y][mx] == self.snake:
            is_blocked = True

        # --- Schritt 0: Geradeaus laufen ---
        if self.turning_step == 0:
            # Lauf weiter, wenn Platz ist UND Limit nicht erreicht
            if self.moves_made < self.maximum_moves and not is_blocked:
                self.moves_made += 1
                return MOVE_FORWARD
            else:
                # Hindernis oder Limit erreicht -> Wende einleiten
                self.turning_step = 1
                # Entscheide Richtung basierend auf Zick-Zack-Status
                return TURN_RIGHT if self.turn_direction == "RIGHT" else TURN_LEFT

        # --- Schritt 1: Erste Drehung (90 Grad) ---
        elif self.turning_step == 1:
            self.turning_step = 2
            # Prüfen ob der Seit-Schritt sicher ist
            # Nach einer Drehung ist "vorne" im Array immer noch y-1,
            # aber in der Welt ist es eine neue Richtung.
            # Da wir aber "blind" fahren, probieren wir es einfach.
            return MOVE_FORWARD

            # --- Schritt 2: Zweite Drehung (180 Grad komplett machen) ---
        elif self.turning_step == 2:
            self.turning_step = 0  # Wende fertig
            self.moves_made = 0  # Zähler resetten

            cmd = TURN_RIGHT if self.turn_direction == "RIGHT" else TURN_LEFT

            # WICHTIG: Richtung für das NÄCHSTE Mal umkehren (Zick-Zack)
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
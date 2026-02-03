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

        # Tracking (Deine Frage nach Zugriff auf Positionen)
        self.history = []  # Hier speichern wir alle gemachten Züge

        # Patrouillen-Einstellungen
        self.moves_made = 0
        self.maximum_moves = 32

        # Wende-Logik
        self.turning_step = 0
        self.turn_direction = "RIGHT"

        # NEU: Breite der Bahnen
        self.sideways_steps_needed = 5  # So viele Schritte gehen wir zur Seite
        self.sideways_steps_done = 0

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
        """Prüft das Feld direkt vor der Nase."""
        n = len(self.scan)
        mid = n // 2
        front_y = mid - 1

        if front_y < 0: return True
        if self.scan[front_y][mid] == self.snake: return True
        return False

    async def next_move(self):
        await asyncio.sleep(0.01)
        if not self.scan: return None

        n = len(self.scan)
        mid = n // 2
        self.my_pos = (mid, mid)
        move_to_send = None

        # --- 1. FOSSILIEN JAGD ---
        target_pos = self.get_closest_fossil(self.my_pos)

        if target_pos:
            path = self.bot_bfs_search(self.my_pos, target_pos, self.scan)
            if path and len(path) > 0:
                next_x, next_y = path[0]
                curr_x, curr_y = self.my_pos

                # Wenn Fossil direkt dahinter, Rückwärtsgang
                if next_y > curr_y:
                    move_to_send = MOVE_BACKWARD
                elif next_y < curr_y:
                    move_to_send = MOVE_FORWARD
                elif next_x > curr_x:
                    move_to_send = TURN_RIGHT
                elif next_x < curr_x:
                    move_to_send = TURN_LEFT

        # --- 2. PATROUILLE (Mit 5er Schritten zur Seite) ---
        if not move_to_send:
            move_to_send = self.get_patrol_move()

        # Speichern in History (damit du Zugriff hast)
        self.history.append(move_to_send)
        return move_to_send

    def get_patrol_move(self):
        blocked = self.is_front_blocked()

        # --- SCHRITT 0: Die lange Bahn (32 Steps) ---
        if self.turning_step == 0:
            if self.moves_made < self.maximum_moves and not blocked:
                self.moves_made += 1
                return MOVE_FORWARD
            else:
                # Bahn zu Ende oder Wand -> Wende einleiten
                self.turning_step = 1
                self.sideways_steps_done = 0  # Zähler für Seitenschritte resetten
                return TURN_RIGHT if self.turn_direction == "RIGHT" else TURN_LEFT

        # --- SCHRITT 1: Zur Seite laufen (5 Steps) ---
        elif self.turning_step == 1:
            # Wir haben uns gerade um 90 Grad gedreht.
            # Jetzt laufen wir bis zu 5 Schritte geradeaus (was "zur Seite" auf der Map ist)

            # Ist vor uns eine Wand? (Wenn ja, brechen wir das Seitwärts-Laufen ab)
            if blocked:
                self.turning_step = 2  # Sofort zum finalen Turn springen
                # Wir müssen sofort drehen, sonst crashen wir
                return self.do_final_turn()

            # Haben wir schon 5 Schritte gemacht?
            if self.sideways_steps_done < self.sideways_steps_needed:
                self.sideways_steps_done += 1
                return MOVE_FORWARD
            else:
                # 5 Schritte erledigt, jetzt wieder in die Hauptrichtung drehen
                self.turning_step = 2
                return self.do_final_turn()

        # --- SCHRITT 2: Finaler Turn (180 Grad vollenden) ---
        elif self.turning_step == 2:
            return self.do_final_turn()

        return MOVE_FORWARD

    def do_final_turn(self):
        """Führt die zweite Drehung aus und setzt den Status zurück."""
        self.turning_step = 0
        self.moves_made = 0

        cmd = TURN_RIGHT if self.turn_direction == "RIGHT" else TURN_LEFT

        # Zick-Zack Richtung wechseln
        if self.turn_direction == "RIGHT":
            self.turn_direction = "LEFT"
        else:
            self.turn_direction = "RIGHT"

        return cmd


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot = SnakeBot()
    bot.run()
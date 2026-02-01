import asyncio
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



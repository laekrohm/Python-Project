import logging

from basic_bot import BaseBot, MOVE_FORWARD, TURN_RIGHT, MOVE_BACKWARD, TURN_LEFT

TRANSLATION_MAP = {
    'W': MOVE_FORWARD,
    'A': TURN_LEFT,
    'S': MOVE_BACKWARD,
    'D': TURN_RIGHT
}

class WASDBot(BaseBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def next_move(self):
        for line in self.scan:
            print(line)
        cmd = ""
        while cmd not in ["W", "A", "S", "D"]:
            cmd = input("Enter next move (W/A/S/D): ").strip().upper()
        return TRANSLATION_MAP[cmd]


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, format="%(asctime)s [%(levelname)s] %(message)s")
    bot = WASDBot()
    bot.run()

import logging
from basic_bot import BaseBot

class ProofShooterBot(BaseBot):
    async def next_move(self):
        scan = self.scan
        c = len(scan) // 2

        # DEBUG: Scan anzeigen
        print("\n".join(scan))
        print("-" * 30)

        # brutal einfache Schusslogik
        for y in range(c - 1, -1, -1):
            cell = scan[y][c]

            if cell == "X":
                break

            if cell.isalpha():
                print("SCHUSS AUF:", cell)
                return "f"

        return ">"


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    ProofShooterBot().run()
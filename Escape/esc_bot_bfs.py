from collections import defaultdict, deque
import time
import logging
import asyncio
from basic_bot import BaseBot, MOVE_FORWARD, TURN_LEFT, MOVE_BACKWARD, TURN_RIGHT
import random



class Graph:
    def __init__(self):

        self.graph = defaultdict(list)


    def addEdge(self, u, v):
        self.graph[u].append(v)

    def bfs(self, start):
        time.sleep(1)
        visited = set()

        queue =deque( [start] )
        visited.add(start)

        print("Starting BFS: ", end= " ", flush=True)

        while queue:
            current_node = queue.popleft()
            print(current_node, end = " ", flush=True)

            time.sleep(1)

            for neighbor in self.graph[current_node]:
                if neighbor not in visited:
                    queue.append(neighbor)
                    visited.add(neighbor)


#TOMORROW TRYING BREADTH FIRST SEARCH IN FORM OF U
TranslateMovements = {
    "W": MOVE_FORWARD,
    "A":TURN_LEFT,
    "S":MOVE_BACKWARD,
    "D":TURN_RIGHT
}

class EscapeBot(BaseBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rocket = "o"
        self.rocket_pos = (16, 16)  #start for BFS
        self.bot_relative_x = random.randint(1,32)    #my x pos is always random
        self.bot_relative_y = random.randint(1, 32)    #my y pos is always random
        self.map_grid = [[x for x in range(1,32)],[ y for y in range(1,32)]]    #grid of 32x32

        self.parent = {}

        self.start_rocket = None   #bot_pos
        self.target = None  #rocket pos
        self.visited = None #neighbors (4 (up, left, down, right))

        self.states = [MOVE_FORWARD, TURN_LEFT, MOVE_BACKWARD, TURN_RIGHT]

    def bot_bfs_search(self, relative_x, relative_y, target):
       

        self.start_rocket = (relative_x, relative_y )#as in normal BFS, we need a start
        self.target = self.rocket_pos #as in normal BFS, we need an end/target
        self.visited = set()    #for logic mathematical loop, put hash values in set
        self.queue = deque([self.start_rocket])    #also prepared queue for logic loop
        self.visited.add(self.start_rocket)

        self.parent = {}

        print("Starting BFS: \n", end= " ", flush=True)

        while self.queue:
            current_node = self.queue.popleft()

            if current_node == self.target:
                path = []
                temp = self.target
                while temp in self.parent:
                    path.append(temp)
                    temp = self.parent[temp]
                path.append(self.start_rocket)
                path.reverse()
                return path
                #print ("Target reached")
                #return True

            curr_x, curr_y = current_node
            neighbors = [(curr_x + 1, curr_y), (curr_x - 1, curr_y),
                         (curr_x, curr_y + 1), (curr_x, curr_y - 1), ]

            for next_node in neighbors:
                if 1 <= next_node[0] <= 32 and 1 <= next_node[1] <= 32:
                    if next_node not in self.visited:
                        self.visited.add(next_node)
                        self.queue.append(next_node)

                        self.parent[next_node] = current_node #remember path, to get to next node, need to be at current node
        return False


    async def next_move(self):
        await asyncio.sleep(0.01)
        for line in self.scan:
            print(line)
        n = len(self.scan)
        center = n // 2
        my_pos = (center, center)

        rocket_in_scan = None
        for y, row in enumerate(self.scan):
            for x, char in enumerate(row):
                if char == "o": #Bingo
                    rocket_in_scan = (x,y)
        if rocket_in_scan:
            path = self.bot_bfs_search(center, center,  rocket_in_scan)
            if path:
                print(f"Ich bin bei: ({self.bot_relative_x},{self.bot_relative_y})")

            else:
                print("bfs hat kein pfad gefunden!")
            if path and len(path) > 1:
                current_pos = path[0]   #bot pos (x,y)
                next_step = path[1] #bot target (x,y)

                if next_step[0] > self.bot_relative_x:
                    self.bot_relative_x += 1
                    return TURN_RIGHT

                elif next_step[0] < self.bot_relative_x:
                    self.bot_relative_x -= 1
                    return TURN_LEFT
                elif next_step[1] > self.bot_relative_y:
                    self.bot_relative_y += 1
                    return MOVE_FORWARD
                elif next_step[1] < self.bot_relative_y:
                    self.bot_relative_y -= 1
                    return MOVE_BACKWARD
        return MOVE_FORWARD

        #-------Trying Strategy for left, right, back
        #if onLeft == "." or onLeft == self.rocket:
            #return TURN_LEFT
        #if onRight == "." or onRight == self.rocket:
            #return TURN_RIGHT
        #if behind == "." or behind == self.rocket:
            #return MOVE_BACKWARD

        #return MOVE_FORWARD

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    bot = EscapeBot()
    bot.run()

#if __name__ == "__main__":
    #g = Graph()
    #g.addEdge(0, 1)
    #g.addEdge(0, 2)
    #g.addEdge(1, 2)
    #g.addEdge(2, 0)
    #g.addEdge(2, 3)
    #g.addEdge(3, 3)
    #g.addEdge(3, 4)
    #g.addEdge(3, 5)
    #g.addEdge(4, 5)
    #g.addEdge(5, 5)
    #g.addEdge(5, 6)
    #g.addEdge(6, 6)
    #g.addEdge(6, 7)
    #g.addEdge(7, 7)
    #g.addEdge(7, 8)
    #g.addEdge(8, 8)
    #g.addEdge(8, 9)
    #g.addEdge(9, 9)
    #g.addEdge(9, 10)

    #print("BFS Search: ", g.bfs(2))



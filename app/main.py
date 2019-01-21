import bottle
import os
import random
import json
import heapq
import sys
global direction
global allNodes

@bottle.route('/')
def static():
    return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    global direction
    data = bottle.request.json
    #print bottle
    #print "TEST"
    game_id = data.get('game_id')
    board_width = data.get('width')
    board_height = data.get('height')

    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': '#00FF00',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url,
        'name': 'dallas'
    }

def moveRight():
    global direction
    direction = 'right'

def moveLeft():
    global direction
    direction = 'left'

def moveUp():
    global direction
    direction = 'up'

def moveDown():
    global direction
    direction = 'down'


def neighbours(node):
    dirs = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    result = []
    global allNodes
    for dir in dirs:
        if ([node[0] + dir[0], node[1] + dir[1]]) in allNodes:
            result.append(((node[0] + dir[0]), (node[1] + dir[1])))
            #print "good"
    return result

def removeNode(node):
    global allNodes
    if node in allNodes:
        allNodes.remove(node)

def enemySnakeOneAway():
    return True


def heuristic(a,b):

    (x1, y1) = a
    (x2, y2) = b
    global data


    #avoid food if not hungry
    foodList = []
    for foods in data['food']['data']:
        foodList.append((foods['x'],foods['y']))

    if data.get('you').get('health') > 30:
        if b in foodList:
            return 100
    

    otherSnakesList = data.get('snakes').get('data')
    if data.get('you') in otherSnakesList:
        otherSnakesList.remove(data.get('you'))

    #avoid collisions
    for snakes in otherSnakesList:
        #print "TESTING REMOVAL NEAR HEAD"
        snakeHead = snakes.get('body').get('data')[0]



        if(b[0] == snakeHead.get('x')-1 and b[1] == snakeHead.get('y')-1):
            #print "dont collide!1"
            return 10

        if(b[0] == snakeHead.get('x')+1 and b[1] == snakeHead.get('y')+1):
            #print "dont collide!2"
            return 10

        if(b[0]+1 == snakeHead.get('x')-1 and b[1] == snakeHead.get('y')):
            #print "dont collide!2"
            return 10

        if(b[0]-1 == snakeHead.get('x')+1 and b[1] == snakeHead.get('y')):
            #print "dont collide!2"
            return 10        

        if(b[0] == snakeHead.get('x') and b[1]+1 == snakeHead.get('y')-1):
            #print "dont collide!2"
            return 10

        if(b[0] == snakeHead.get('x') and b[1]-1 == snakeHead.get('y')+1):
            #print "dont collide!2"
            return 10


        if(b[0] == snakeHead.get('x')+1 and b[1] == snakeHead.get('y')-1):
            #print "dont collide!3"
            return 10

        if(b[0] == snakeHead.get('x')-1 and b[1] == snakeHead.get('y')+1):
            #print "dont collide!4"
            return 10

    return abs(x1 - x2) + abs(y1 - y2)

class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]


def AStar(graph, start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0


    while not frontier.empty():
        current = frontier.get()
        
        if current == goal:
            break
        
        for next in neighbours(current):
            new_cost = cost_so_far[current] + heuristic(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(next, goal)
                frontier.put(next, priority)
                came_from[next] = current
                #print current
    
    return came_from, cost_so_far
@bottle.post('/move')
def move():
    global data
    data = bottle.request.json

    # TODO: Do things with data
    #print
    #print
    #x = json.loads(data)
    #for foods in data['food']['data']:
    #    print foods['x']
    #    print foods['y']
    #    print

    goalFood = data['food']['data'][0]
    goal = (goalFood['x'],goalFood['y'])
    boardHeight = data.get('height')
    boardWidth = data.get('width')
    #print boardHeight
    #print json.dumps(data,indent=4) 
    
    startX = data['you']['body']['data'][0]['x']
    startY = data['you']['body']['data'][0]['y']
    start = (startX, startY)
    currentPos = (start[0], start[1])

    currPosHeadX = data['you']['body']['data'][0]['x']
    currPosHeadY = data['you']['body']['data'][0]['y']

    directions = ['up', 'down', 'left', 'right']
    #direction = random.choice(directions)



    global allNodes
    global direction
    allNodes = []
    for x in range(boardWidth):
        for y in range(boardHeight):
            allNodes.append([x, y])

    for snakes in data.get('snakes').get('data'):
        for squares in snakes.get('body').get('data'):
            removeNode([squares.get('x'),squares.get('y')])
            #print "Node removed: (", squares.get('x'), ", ", squares.get('y'),")"
    
    foodCosts = []
    for foods in data['food']['data']:
        possibleGoal = (foods['x'],foods['y'])
        cameFrom, costSoFar = AStar(allNodes, start, possibleGoal)
        foodCosts.append(costSoFar)

    if data.get('you').get('health') <= 30:
        #search for food

        goal = (data['food']['data'][foodCosts.index(min(foodCosts))]['x'], data['food']['data'][foodCosts.index(min(foodCosts))]['y'])

    else:
        #pick a random safe spot 4 squares away
        safeSpots = []
        distance = 20

        li = []
        for i in range(distance+1):
            li.append((distance-i,i))
        #print li
        directionList = []
        for (x,y) in li:
            directionList.append(tuple((x,y)))
            if x != 0:
                directionList.append(tuple((x*-1,y)))
                if y != 0:
                    directionList.append(tuple((x*-1,y*-1)))
            if y != 0:
                directionList.append(tuple((x,y*-1)))

        spotCosts = []
        minCostSoFar = sys.maxint
        for spot in directionList:

            if ((start[0] + spot[0] >= 0) and (start[0] + spot[0] < boardWidth) and (start[1] + spot[1] >= 0) and (start[1] + spot[1] < boardHeight)):
                possibleGoal = (start[0] + spot[0], start[1] + spot[1])
                #print possibleGoal

                #print "Start: ", start
                #print "PG: ", possibleGoal

                cameFrom, costSoFar = AStar(allNodes, start, possibleGoal)

                #print cameFrom

                #print "cost: ", costSoFar[possibleGoal]
                #print "min: ", minCostSoFar
                currentCost = 0
                current = possibleGoal
                while current != start:
                    #print costSoFar[current]
                    prev = current
                    currentCost += costSoFar[current]
                    current = cameFrom[current]

                if currentCost < minCostSoFar:
                    #print goal
                    #print data.get('you').get('health')
                    minCostSoFar = currentCost
                    goal = possibleGoal
                
#                print spotCosts[min(spotCosts)]
                #print spotCosts[spotCosts.index(min(spotCosts))]
                #goal = (spotCosts[spotCosts.index(min(spotCosts))][0], spotCosts[spotCosts.index(min(spotCosts))[1]])

    cameFrom, costSoFar = AStar(allNodes, start, goal)
    #print cameFrom
    #print currentPos
    #print cameFrom[goal]
    current = goal
    while current != start:
        prev = current
        current = cameFrom[current]

    #print "DEBUG"
    #print currentPos[0]
    #print currentPos[1]
    #print
    #print prev[0]
    #print prev[1]


    if(currentPos[0] > prev[0]):
        moveLeft()
    
    if(currentPos[0] < prev[0]):
        moveRight()
    
    if(currentPos[1] > prev[1]):
        moveUp()
    
    if(currentPos[1] < prev[1]):
        moveDown()


    #print direction
    return {
        'move': direction,
        'taunt': 'For the Horde!'
    }
#test

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug = True)

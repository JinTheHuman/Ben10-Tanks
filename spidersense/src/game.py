import random
import math
import sys

import comms
from object_types import ObjectTypes

def getAngleFromVelocity(velocity):
    x, y = velocity
    if x == 0:
        if y == 0:
            return 0
        elif y > 0:
            return 90
        else: 
            return 270
    acute_angle = math.degrees(math.atan(y/x))
    if x > 0 and y > 0:
        angle = acute_angle
    elif x < 0:
        angle = 180 + acute_angle
    else:
        angle = 360 + acute_angle
    return angle

def calculateAngle(src, dst):
    dy = dst[1] - src[1]
    dx = dst[0] - src[0]

    if dx == 0:
        if dy > 0:
            angle = 90
        else:
            angle = 270
    else:
        acute_angle = math.degrees(math.atan(dy/dx))
        if dx > 0 and dy > 0:
            angle = acute_angle
        elif dx < 0:
            angle = 180 + acute_angle
        else:
            angle = 360 + acute_angle

    return angle


def getAngleLeway(src, dst):
    return math.degrees(math.atan(19.142/math.dist(src, dst)))


def canHit(src, dst, angle):
    leway = getAngleLeway(src, dst)
    return calculateAngle(src, dst) - leway <= angle <= calculateAngle(src, dst) + leway


def canhitwithbounce(src, wall, enemy):
    if math.dist(src, wall) + math.dist(wall, enemy) > 1.25 * math.dist(src, enemy):
        return None

    alpha = calculateAngle(src, wall)

    if alpha > 270:
        if canHit(wall, enemy, 540 - alpha):
            return alpha
    elif alpha > 180:
        if canHit(wall, enemy, 540 - alpha):
            return alpha
    elif alpha > 90:
        if canHit(wall, enemy, 180 - alpha):
            return alpha
    else:
        if canHit(wall, enemy, 180 - alpha):
            return alpha
    return None


def getpositive(angle):
    if angle < 0:
        return angle + 360
    return angle


def predictPos(src, dst, velocityTank, bulletSpeed):
    dist = math.dist(src, dst)
    time = dist/bulletSpeed
    newPos = []
    newPos.append(dst[0] + velocityTank[0] * time)
    newPos.append(dst[1] + velocityTank[1] * time)

    return newPos

class Game:
    """
    Stores all information about the game and manages the communication cycle.
    Available attributes after initialization will be:
    - tank_id: your tank id
    - objects: a dict of all objects on the map like {object-id: object-dict}.
    - width: the width of the map as a floating point number.
    - height: the height of the map as a floating point number.
    - current_turn_message: a copy of the message received this turn. It will be updated everytime `read_next_turn_data`
        is called and will be available to be used in `respond_to_turn` if needed.
    """
    def __init__(self):
        tank_id_message: dict = comms.read_message()
        print("Init: ", tank_id_message, file=sys.stderr)
        self.tank_id = tank_id_message["message"]["your-tank-id"]
        self.enemy_tank_id = tank_id_message["message"]["enemy-tank-id"]

        self.current_turn_message = None

        # We will store all game objects here
        self.objects = {}

        next_init_message = comms.read_message()
        print("next_Init: ", next_init_message, file=sys.stderr)
        while next_init_message != comms.END_INIT_SIGNAL:
            # At this stage, there won't be any "events" in the message. So we only care about the object_info.
            object_info: dict = next_init_message["message"]["updated_objects"]

            # Store them in the objects dict
            self.objects.update(object_info)

            # Read the next message
            next_init_message = comms.read_message()

        # We are outside the loop, which means we must've received the END_INIT signal

        # Let's figure out the map size based on the given boundaries

        # Read all the objects and find the boundary objects
        boundaries = []
        self.walls = []
        for game_object in self.objects.values():
            if game_object["type"] == ObjectTypes.BOUNDARY.value:
                boundaries.append(game_object)
            elif game_object["type"] == ObjectTypes.WALL.value:
                self.walls.append(game_object["position"])

        print(self.objects, file=sys.stderr)

        # The biggest X and the biggest Y among all Xs and Ys of boundaries must be the top right corner of the map.

        # Let's find them. This might seem complicated, but you will learn about its details in the tech workshop.
        biggest_x, biggest_y = [
            max(
                [
                    max(
                        map(
                            lambda single_position: single_position[i],
                            boundary["position"],
                        )
                    )
                    for boundary in boundaries
                ]
            )
            for i in range(2)
        ]

        self.width = biggest_x
        self.height = biggest_y
        self.centre = [biggest_x / 2, biggest_y / 2]
        print(biggest_x, biggest_y, file=sys.stderr)

        self.bulletSpeed = None
        self.isDodging = False
        self.isComingBack = False
        self.count = 0
        self.hp = 5
        self.bulletSpeed = 450

    def read_next_turn_data(self):
        """
        It's our turn! Read what the game has sent us and update the game info.
        :returns True if the game continues, False if the end game signal is received and the bot should be terminated
        """
        # Read and save the message
        self.current_turn_message = comms.read_message()

        if self.current_turn_message == comms.END_SIGNAL:
            return False


        # Update your records of the new and updated objects in the game
        # NOTE: you might want to do some additional logic here. For example check if a new bullet has been shot or a
        # new powerup is now spawned, etc.
        self.objects.update(self.current_turn_message["message"]["updated_objects"])

        # Delete the objects that have been deleted
        # NOTE: You might want to do some additional logic here. For example check if a powerup you were moving towards
        # is already deleted, etc.
        for deleted_object_id in self.current_turn_message["message"]["deleted_objects"]:
            try:
                del self.objects[deleted_object_id]
            except KeyError:
                pass

        return True

    def respond_to_turn(self):
        """
        This is where you should write your bot code to process the data and respond to the game.
        """
        # Get position of my tank and enemy tank
        print("NEWTURN", self.count, file=sys.stderr)
        
        # MOVE DATA
        angle_to_move = -1

        if self.hp != self.objects[self.tank_id]['hp']:
            self.hp = self.objects[self.tank_id]['hp']
            print("I GOT HIT BY A BULLET", file=sys.stderr)
        
        self.count += 1
        mypos = self.objects[self.tank_id]['position']
        enemypos = self.objects[self.enemy_tank_id]['position']

        myvelocity = self.objects[self.tank_id]['velocity']

        # GET BULLET DATA
        bullets = []
        walls = self.walls
        for name, game_object in self.objects.items():
            if game_object["type"] == ObjectTypes.BULLET.value:
                bullets.append([name, game_object])
            elif game_object["type"] == ObjectTypes.CLOSING_BOUNDARY.value:
                corners = game_object["position"]
                corners_velocity = game_object["velocity"]
        # DODGING LOGIC
        closestBullet = None
        bullets_who_can_hit_me = []
        for name, bullet in bullets:
            pos = bullet['position']
            vel = bullet['velocity']
            ang = getAngleFromVelocity(vel)
            dist = math.dist(pos, mypos)
            print(name, " shooting at angle: ", ang, "from pos", pos, "and is ", dist, "from me", file=sys.stderr)
            if canHit(bullet['position'], mypos, ang):
                bullets_who_can_hit_me.append(name)
                if dist < 200:
                    if closestBullet == None or dist < math.dist(closestBullet[1]['position'], mypos):
                        closestBullet = [name, bullet]
        print("Bullets who can hit me", bullets_who_can_hit_me, file=sys.stderr)

        if closestBullet != None:
            name = closestBullet[0]
            pos = closestBullet[1]['position']
            vel = closestBullet[1]['velocity']
            ang = getAngleFromVelocity(vel)
            dist = math.dist(pos, mypos)
            print("dodging", name, "it is ", dist, "from me", file=sys.stderr)
            r = -1

            angle_to_centre = calculateAngle(mypos, self.centre)
            angle_to_centre = (angle_to_centre + 90 + 180) % 360 - 180
            a = (ang + 90 + 180) % 360 - 180
            b = (ang - 90 + 180) % 360 - 180
            
            if abs(a - angle_to_centre) < abs(b - angle_to_centre):
                r = 1
            angle_to_move = ang + (45 * r)
            # comms.post_message({ "move": ang + (45 * r) })
            # return
        
        ### SHOOTING

        # GET ENEMY POSITION
        predictedPos = enemypos
        enemy_velocity = self.objects[self.enemy_tank_id]['velocity']

        if enemy_velocity[0] == 0 and enemy_velocity[1] == 0:
            predictedPos = enemypos
        else:
            predictedPos = predictPos(
                mypos, enemypos, enemy_velocity, self.bulletSpeed)


        r = random.randint(0, 4)

        angle = calculateAngle(mypos, predictedPos)

        print("Shooting at angle", angle, " to hit enemy at",
              predictedPos, "from mypost at", mypos, file=sys.stderr)

        if r != 4:
            closest_wall_dist = abs(corners[0][0] - mypos[0])
            closest_wall = 1

            if abs(corners[2][0] - mypos[0]) < closest_wall_dist:
                closest_wall_dist = abs(corners[2][0] - mypos[0])
                closest_wall = 3
            if abs(corners[0][1] - mypos[1]) + 40 < closest_wall_dist:
                closest_wall_dist = abs(corners[0][1] - mypos[1])
                closest_wall = 0
            if abs(corners[1][1] - mypos[1]) + 40 < closest_wall_dist:
                closest_wall_dist = abs(corners[1][1] - mypos[1])
                closest_wall = 2

            # while (r == closest_wall or r == (closest_wall + 2) % 4):
            #     r = random.randint(0, 3)

            newX, newY = predictedPos[0], predictedPos[1]
            if r == 0:
                newY = corners[0][1] + (corners[0][1] - predictedPos[1])
            elif r == 1:
                newX = corners[0][0] + (corners[0][0] - predictedPos[0])
            elif r == 2:
                newY = corners[1][1] + (corners[1][1] - predictedPos[1])
            elif r == 3:
                newX = corners[2][0] + (corners[2][0] - predictedPos[0])

            time = (math.dist(mypos, [newX, newY])/2) / self.bulletSpeed
            d = abs(corners_velocity[1][1] * time)

            if r == 0:
                newY = (corners[0][1] - d) + \
                    ((corners[0][1] - d) - predictedPos[1])
            elif r == 1:
                newX = (corners[0][0] + d) + \
                    ((corners[0][0] + d) - predictedPos[0])
            elif r == 2:
                newY = (corners[1][1] + d) + \
                    ((corners[1][1] + d) - predictedPos[1])
            elif r == 3:
                newX = (corners[2][0] - d) + \
                    ((corners[2][0] - d) - predictedPos[0])

            predictedPos = [newX, newY]

            noise = random.uniform(-0.8, 0.8)
            angle = calculateAngle(mypos, predictedPos) + noise
            print("Bouncing off wall", r, file=sys.stderr)

        comms.post_message({"shoot": angle, "move": angle_to_move})


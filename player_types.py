# -*- coding: utf-8 -*-

from player import Player
from ball import status

import numpy as np

class Pitcher(Player):
    def __init__(self, f, p, mw):
        super().__init__(f, p, mw)

        self.range = 60
        self.radians = 30
        self.kyori = 150

    def pitchTheBall(self, ball):
        print('pitch!')
        if self.hasBall and not self.top:
            ball.thrown(0, 12)
            ball.mode = status.PITCHED
            self.hasBall = False
            ball.isCaught = False

class Catcher(Player):
    def __init__(self, f, p, mw):
        super().__init__(f, p, mw)

        self.range = 180
        self.radians = 30
        self.kyori = 30

    def nearestToBall(self, ball, ground):
        if ball.isFair or ball.mode == status.FRYING and ball.pos[2] > 3:
            super().nearestToBall(ball, ground)

    def move_defence(self, ball, ground):
        if (ball.isFair or ball.mode == status.FRYING) and ground.bases[3].runner != -1:
            self.goToBase(ground.bases[0], ball)
        elif ball.isFair or ball.mode == status.FRYING and ball.pos[2] > 3:
            super().move_defence(ball, ground)

    def catchThePitch(self, ball):
        x = ball.pos[0] + ball.vel[0] - self.pos[0]
        y = ball.pos[1] + ball.vel[1] - self.pos[1]
        dis = np.sqrt(x * x + y * y)

        if ball.pos[2] + ball.vel[2] < 3 and dis <= 5:
            self.catch(ball) # 捕球
            ball.mode = status.TIME
            self.hasBall = True

class First(Player):
    def __init__(self, f, p, mw):
        super().__init__(f, p, mw)

        self.range = 15
        self.radians = 100
        self.kyori = 200

    def move_defence(self, ball, ground):
        super().move_defence(ball, ground)
        if ball.mode == status.HITTED or ball.mode == status.FRYING and not ground.bases[1].isSteped:
            self.goToBase(ground.bases[1], ball)

class Second(Player):
    def __init__(self, f, p, mw):
        super().__init__(f, p, mw)

        self.range = 15
        self.radians = 200
        self.kyori = 250

    def move_defence(self, ball, ground):
        super().move_defence(ball, ground)
        if (ball.isFair or ball.mode == status.FRYING) and ground.bases[1].runner != -1 and not ground.bases[2].isSteped:
            self.goToBase(ground.bases[2], ball)


class Third(Player):
    def __init__(self, f, p, mw):
        super().__init__(f, p, mw)

        self.range = 15
        self.radians = 200
        self.kyori = 200

    def move_defence(self, ball, ground):
        if (ball.isFair or ball.mode == status.FRYING) and ground.bases[2].runner != -1:
            self.goToBase(ground.bases[3], ball)
        else:
            super().move_defence(ball, ground)

class Short(Player):
    def __init__(self, f, p, mw):
        super().__init__(f, p, mw)

        self.range = 15
        self.radians = 200
        self.kyori = 250

    def move_defence(self, ball, ground):
        if (ball.isFair or ball.mode == status.FRYING) and ground.bases[1].runner != -1 and not ground.bases[2].isSteped:
            self.goToBase(ground.bases[2], ball)
        else:
            super().move_defence(ball, ground)

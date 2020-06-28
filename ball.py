# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import numpy as np

from enum import Enum

class status(Enum):
    TIME = 0
    PITCHED = 1
    HITTED = 2
    LOOKED = 3
    FRYING = 4
    FRYCAUGHT = 5
    HOMERUN = 6

## z座標について
## 0: グランドの高さ， 1: 人が取りやすい高さ, 2: 人がジャンプすれば取れる高さ, 3以上: 人が届かない高さ

b_default = 10
homebase = [305, 498]   ## 要修正
first_line = [1, -1] ## 一塁線の方向ベクトル
g = -0.05
air_resist = 0.02

class Ball():
    def __init__(self, mw):
        self.initialize()

        #self.label = QLabel(mw)
        #self.pixmap = QPixmap('img/ball.png')
        #s = b_default + self.pos[2]
        #self.label.setPixmap(self.pixmap.scaled(s, s, Qt.KeepAspectRatio))

    def initialize(self):
        self.pos = [300, 350, 1]    ##初期座標はマウンドに直す
        self.stop()
        self.mode = status.TIME
        self.isFair = False
        self.isCaught = False   ## 守備側の誰かが触ったかどうか
        self.drop = [0, 0]
        self.hittedBy = -1

    def move(self):
        #print('(ball) : x = ' + str(self.pos[0]) + ', y = ' + str(self.pos[1]) + ', z = ' + str(self.pos[2]))
        for i in range(3):
            self.pos[i] += self.vel[i]  ##移動
            self.vel[i] += self.acc[i]  ##速度を更新
        if self.pos[2] < 0:
            if self.mode == status.FRYING:
                self.mode = status.HITTED
            self.pos[2] = abs(self.pos[2]) / 10
            self.vel[2] /= 2
        self.decelaration() ##加速度を更新
        self.setDropPoint()

    def status(self):   ##ボールの状態を判定する
        d, deg, p = self.getBallPositionOnGround(first_line)
        if self.mode == status.FRYING or self.mode == status.HOMERUN:
            if (deg > 90 or p <= 0) and d > 100 and not self.isFair:
                print('foul')
                return 'foul'
            elif deg <= 90 and p >= 0 and d > 420:
                ## ホームランの処理
                print('homerun')
                #self.stop()
                self.mode = status.HOMERUN
                return 'homerun'
            return 'wait'
        elif deg <= 90 and p >= 0:
            if self.pos[2] + self.vel[2] <= 2 and d > 420:
                self.pos[0] -= self.vel[0]
                self.pos[1] -= self.vel[1]
                self.vel[0] = -self.vel[0]/10
                self.vel[1] = -self.vel[1]/10
                self.isFair = True
                print('fair')
            if self.pos[2] + self.vel[2] < 0 and d > 150:
                self.isFair = True
            return 'fair'
        else:
            if self.isFair:
                if d > 420:
                    self.pos[0] -= self.vel[0]
                    self.pos[1] -= self.vel[1]
                    self.vel[0] = -self.vel[0]/10
                    self.vel[1] = -self.vel[1]/10
                    return 'fair'
                #print('fair')
            elif (deg > 100 or p <= 5 or deg > 90 and p <= 0) and d > 300:
                self.ball.mode == status.TIME
                return 'balldead'
            print('foul')
            return 'foul'

    def getBallPositionOnGround(self, line):
        x = self.pos[0] - homebase[0]
        y = self.pos[1] - homebase[1]
        d = np.sqrt( x * x + y * y )

        pos = [x, y]
        i = np.inner(pos, line)
        theta = np.arccos(i / (np.linalg.norm(pos) * np.linalg.norm(line)))
        deg = np.degrees(theta)
        line_y = -self.pos[0] + homebase[0] + homebase[1]
        #print('distance: ' + str(d) + ', degree: ' + str(deg), ', y: ' + str(line_y - self.pos[1]))
        return d, deg, line_y - self.pos[1]

    def decelaration(self): ##加速度の処理
        if not self.isStop:
            #print('(dec vel): x = ' + str(self.vel[0]) + ', y = ' + str(self.vel[1]) + ', z = ' + str(self.vel[2]))
            if np.sqrt(self.vel[0] * self.vel[0] + self.vel[1] * self.vel[1] + self.vel[2] * self.vel[2]) < 0.02:
                self.stop()
                return

            if self.pos[2] > 0:
                for i in range(2):
                    self.acc[i] = -self.vel[i] * air_resist
                self.acc[2] = g
            else:
                for i in range(2):
                    self.acc[i] = -self.vel[i] * 3 * air_resist
                self.acc[2] = 0
        else:
            self.stop()

    def stop(self):
        #print('ball is stop')
        self.isStop = True
        self.vel = [0, 0, 0]
        self.acc = [0, 0, 0]

    def thrown(self, x, y):
        self.vel[0] = x
        self.vel[1] = y
        self.isStop = False

    def setDropPoint(self):
        t = (-self.vel[2] - np.sqrt(self.vel[2]*self.vel[2] - 2*g*self.pos[2])) / g
        self.drop[0] = self.pos[0] + self.vel[0]*t + self.acc[0] * t * t / 2
        self.drop[1] = self.pos[1] + self.vel[1]*t + self.acc[1] * t * t / 2
        #print('(drop) ' + str(self.drop))

    def computeNearestPlayer(self, players):
        min = 10000000
        nearest = players[0]
        for p in players:
            x = self.drop[0] - p.pos[0]
            y = self.drop[1] - p.pos[1]
            dis = np.sqrt(x * x + y * y)
            #print('(np)' + str(p.position) + ': ' + str(dis))
            if dis < min:
                min = dis
                nearest = p
        return nearest

    def getDropPoint(self, loc):
        if self.mode == status.PITCHED or self.mode == status.TIME or self.mode == status.LOOKED:
            return 10000000

        if self.isCaught:
            return 10000000

        x = self.drop[0] - loc[0]
        y = self.drop[1] - loc[1]

        dis = np.sqrt(x * x + y * y)
        return dis

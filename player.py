# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import numpy as np
import random
import math

from ball import status, homebase

p_default = 20
position_locs = [[298, 298, 400, 350, 200, 250, 150, 300, 450], [350, 500, 320, 225, 320, 225, 150, 100, 150]]

class Player():
    def __init__(self, f, p, mw):
        self.top = f
        self.position = p       ## 守備位置 or 打順

        self.onBase = -1
        self.backed = False

        self.hasBall = False
        self.stepBase = -1

        self.label = QLabel(mw)
        if self.top:
            pixmap = QPixmap('img/player_b.png').scaled(p_default, p_default, Qt.KeepAspectRatio)
            self.pos = [315, 480]
        else:
            pixmap = QPixmap('img/player_r.png').scaled(p_default, p_default, Qt.KeepAspectRatio)
            self.pos = [position_locs[0][p], position_locs[1][p]]
        #print(self.pos)
        self.label.setPixmap(pixmap)

        self.power = random.randint(3, 4)       ##パワー
        self.contact = random.randint(4, 5)     ##ミート
        self.run = 4                            ##走力
        self.range = 30                         ##守備範囲（角度）
        self.radians = 200                      ##守備範囲（半径）
        #self.error = random.randint(0, 3)       ##エラー
        self.kyori = 400

    def initialize(self):
        if not self.top:
            self.pos = [position_locs[0][self.position], position_locs[1][self.position]]
            self.stepBase = -1

    def draw(self):  ##選手の描画
        if self.top and self.onBase != -1:  ##攻撃中かつバッターボックス or 塁上にいる
            #print('(draw) position: ' + str(self.position) + ', onBase = ' + str(self.onBase) + ', location = ' + str(self.pos))
            self.label.move(self.pos[0], self.pos[1])   ##ここでバッターボックスかベース上に立たせる
            self.label.setHidden(False)
        elif self.top and self.onBase == -1:
            #print('(not draw) position: ' + str(self.position) + ', onBase = ' + str(self.onBase) + ', location = ' + str(self.pos))
            self.label.setHidden(True)
            return
        elif not self.top:             ##守備中
            #print(str(self.position) + ': ' + str(self.pos))
            self.label.move(self.pos[0], self.pos[1])   ##ここで守備位置に立たせる

    def run_next(self, ground):
        ground.runFrom(self.onBase, self.position)

        x, y, dis = ground.bases[self.onBase].getNextBaseDirection(self.pos)
        if dis > 5:
            self.pos[0] += self.run * x / dis
            self.pos[1] += self.run * y / dis
        else:
            if self.onBase != 3:
                self.onBase += 1
                ground.setRunners(self.onBase, self.position)
            else:
                if ground.bases[self.onBase].runner == self.position:
                    ground.bases[self.onBase].deleteRunner()
                ground.running[self.onBase] = -1
                self.onBase = -1
                print(':tada: +++ 1 point +++ :tada:')
                return 1
        return 0

    def back(self, ground):
        x, y, dis = ground.bases[self.onBase].getBackBaseDirection(self.pos)
        if dis > 5:
            self.pos[0] += self.run * x / dis
            self.pos[1] += self.run * y / dis
        else:
            ground.running[self.onBase] = -1
            self.backed = True

    def move_attack(self, ball, ground, br):
        point = 0
        if self.onBase == 0:    # 自分が打者のとき
            point = self.run_next(ground)
        elif ball.mode == status.HOMERUN:
            point = self.run_next(ground)
        elif ball.mode == status.HITTED:    # 打球が落ちた時
            if ground.mustGo(self.onBase, self.position): # 後ろの塁がつまってる時
                point = self.run_next(ground)
            elif ground.bases[self.onBase].safetyToGoNext(ball, self.pos) and not ground.cannotGo(self.onBase, self.position): # 安全かつ前の走者が走ってる
                point = self.run_next(ground)
            else:
                self.back(ground)
        elif ball.mode == status.FRYING:    # フライが上がった時
            if self.position == br and not ground.cannotGo(self.onBase, self.position):    # 打者走者の時
                point = self.run_next(ground)
            elif ball.mode == status.HOMERUN:
                point = self.run_next(ground)
            else:   # ハーフウェイ
                ground.runFrom(self.onBase, self.position)
                self.backed = False
                x, y, dis = ground.bases[self.onBase].getNextBaseDirection(self.pos)
                if dis > 100:
                    self.pos[0] += self.run * x / dis
                    self.pos[1] += self.run * y / dis
        elif ball.mode == status.FRYCAUGHT:     # フライ捕球後
            if not self.backed:
                self.back(ground)
            else:
                if ground.bases[self.onBase].safetyToGoNext(ball, self.pos) and not ground.cannotGo(self.onBase, self.position):
                    point = self.run_next(ground)
        return point

    def backToBase(self, i, base):
        self.onBase = i
        self.pos[0] = base.loc[0]
        self.pos[1] = base.loc[1]
        base.runner = self.position
        self.backed = False
        #print('player ' + str(self.position) + ' : ' + str(self.onBase), end='')

    def judgeCatch(self, ball, ground):
        #print('(judgecatch) height: ' + str(ball.pos[2]))
        if ball.pos[2] < 3 and not self.hasBall:
            x1 = ball.pos[0] - 5
            y1 = ball.pos[1] - 5
            x2 = x1 + ball.vel[0] + 10
            y2 = y1 + ball.vel[1] + 10
            x3 = self.pos[0]
            y3 = self.pos[1]
            #print('(judgecatch) vel: ' + str(np.sqrt(ball.vel[0]*ball.vel[0] + ball.vel[1]*ball.vel[1])))
            #if np.sqrt(ball.vel[0]*ball.vel[0] + ball.vel[1]*ball.vel[1]) < 5:
            x = x1 - x3
            y = y1 - y3
            dis = np.sqrt(x*x + y*y)
            if dis < 6:
                self.catch(ball) # 捕球
            if (x1 <= x3 <= x2 or x1 >= x3 >= x2) and (y1 <= y3 <= y2 or y1 >= y3 >= y2) and not self.hasBall:
                u = np.array([x2 - x1, y2 - y1])
                v = np.array([x3 - x1, y3 - y1])
                L = abs(np.cross(u, v) / np.linalg.norm(u))
                print('(pos ' + str(self.position) + ') height: ' + str(ball.pos[2] + ball.vel[2]) + ', dis: ' + str(L))
                if L <= 20:
                    self.catch(ball) # 捕球

    def isBallInRange(self, ball):
        ## 自分の位置から+-15度（ホームベースを中心に）以内にボールがあるかどうか
        myline = [position_locs[0][self.position]-homebase[0], position_locs[1][self.position]-homebase[1]]
        ball_d, ball_deg, ball_p = ball.getBallPositionOnGround(myline)

        dis = ball.getDropPoint([position_locs[0][self.position], position_locs[1][self.position]])
        #print('Position ' + str(self.position) + ', deg = ' + str(ball_deg) + ', dis = ' + str(dis))

        x = ball.pos[0] - homebase[0]
        y = ball.pos[1] - homebase[1]
        fromHome = np.sqrt(x * x + y * y)

        if fromHome > self.kyori:
            return False
        if ball.mode == status.FRYING:
            return abs(ball_deg) < self.range and dis < self.radians
        else:
            return abs(ball_deg) < self.range

    def move_defence(self, ball, ground):
        if self.isBallInRange(ball) and not ball.isCaught:
            if self.stepBase == -1:
                ground.bases[self.stepBase].isSteped = False
                self.stepBase = -1
            x = ball.pos[0] + ball.vel[0] - self.pos[0]
            y = ball.pos[1] + ball.vel[1] - self.pos[1]
            dis = np.sqrt(x * x + y * y)
            #print('(move_defence) pos: x = ' + str(x) + ', y = ' + str(y))
            if ball.mode == status.HITTED:
                # 移動
                self.pos[0] += self.run * x / dis
                self.pos[1] += self.run * y / dis
            elif ball.mode == status.FRYING:
                d_x = ball.drop[0] - self.pos[0]
                d_y = ball.drop[1] - self.pos[1]
                d_dis = np.sqrt(d_x * d_x + d_y * d_y)
                self.pos[0] += self.run * d_x / d_dis
                self.pos[1] += self.run * d_y / d_dis

            if self.hasBall:
                ball.pos[0] = self.pos[0]
                ball.pos[1] = self.pos[1]

    def judgeThrow(self, ball, ground):
        for i in [0, 3, 2, 1]:
            b = (i-1) % 4
            #print('(judge throw) base ' + str(i) + ' is steped ' + str(ground.bases[i].isSteped) + ', ' + str(ground.running[b]))
            if ground.bases[i].isSteped and ground.running[b] != -1:
                if self.stepBase != i:
                    self.throw(ball, ground.bases[i])
                    return
                else:
                    self.goToBase(ground.bases[i], ball)
                    return
        #print('player ' + str(self.position) + ' does not throw')

    def catch(self, ball):
        print('player ' + str(self.position) + ' catched')
        if ball.mode == status.FRYING:
            print("OUT !")
            ball.mode = status.FRYCAUGHT
        ball.stop()
        for i in range(2):
            ball.pos[i] = self.pos[i]
            ball.vel[i] = 0
        ball.pos[2] = 1
        ball.vel[2] = 0
        self.hasBall = True
        ball.isCaught = True

    def throw(self, ball, base):
        print('player ' + str(self.position) + ' throw to ' + str(base.id))
        dir_x = (base.loc[0] - self.pos[0])
        dir_y = (base.loc[1] - self.pos[1])
        if base.id == 0:
            dir_x = (homebase[0] - 10 - self.pos[0])
            dir_y = (homebase[1] - 10 - self.pos[1])

        dis = np.sqrt(dir_x * dir_x + dir_y * dir_y)
        if dis > 30:
            dir_x *= self.power
            dir_y *= self.power
        x = 4 * dir_x / dis
        y = 4 * dir_y / dis
        ball.thrown(x, y)
        self.hasBall = False
        #ball.isCaught = False

    def goToBase(self, base, ball):
        #print('player ' + str(self.position) + ' goes to ' + str(base.id))
        x = base.loc[0] - self.pos[0]
        y = base.loc[1] - self.pos[1]
        if base.id == 0:
            x = homebase[0] - 10 - self.pos[0]
            y = homebase[1] - 10 - self.pos[1]
        dis = np.sqrt(x * x + y * y)

        if dis < 3:
            self.stepBase = base.id
            base.isSteped = True
        else:
            self.stepBase = -1
            base.isSteped = False
            if self.stepBase != base.id:
                self.pos[0] += self.run * x / dis
                self.pos[1] += self.run * y / dis
            if self.hasBall:
                ball.pos[0] = self.pos[0]
                ball.pos[1] = self.pos[1]

    def hitting(self, ball):
        r = random.randint(0, 100)
        x_dis = (ball.pos[0] - self.pos[0])
        y_dis = ball.pos[1] - self.pos[1]
        dis = np.sqrt(x_dis * x_dis + y_dis * y_dis)
        #print(dis)
        if dis < 15.3:
            if r < self.contact * 20:
                if r < self.contact / 2:
                    angle = 225 + 45 * random.random()
                else:
                    angle = 360 * random.random()
                #print('(hitting) angle = ' + str(angle))
                #speed = np.sqrt(ball.vel[0] * ball.vel[0] + ball.vel[1] * ball.vel[1])
                x = self.power * np.cos(math.radians(angle)) * 3
                y = self.power * np.sin(math.radians(angle)) * 3

                ball.vel[0] = x
                ball.vel[1] = y
                ball.vel[2] = 2 * random.random() - 0.5
                ball.mode = status.FRYING
                ball.hittedBy = self.position
                return 'hitted'
            else:
                ball.mode = status.LOOKED
                return 'looked'
        else:
            return 'yet'

if __name__ == '__main__':
    print(position_locs)

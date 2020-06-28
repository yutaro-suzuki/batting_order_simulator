# -*- coding: utf-8 -*-
import random
from player import Player
from player_types import Pitcher, Catcher, First, Second, Third, Short
from ball import status
from ground import Ground
import time
import numpy as np

class Game():
    def __init__(self, mw, ball):
        #self.mw = mw
        self.ground = Ground()
        self.points = [0 for _ in range(9)]
        self.records = []
        self.sumrecords = []
        self.games = 0
        self.top_players = [Player(True, i, mw) for i in range(9)]
        self.bottom_players = []
        for i in range(9):
            if i == 0:
                p = Pitcher(False, i, mw)
            elif i == 1:
                p = Catcher(False, i, mw)
            elif i == 2:
                p = First(False, i, mw)
            elif i == 3:
                p = Second(False, i, mw)
            elif i == 4:
                p = Third(False, i, mw)
            elif i == 5:
                p = Short(False, i, mw)
            else:
                p = Player(False, i, mw)
            self.bottom_players.append(p)
        self.ball = ball

    def drawPlayers(self):
        for i in range(9):
            self.top_players[i].draw()
            self.bottom_players[i].draw()

    def newGame(self):
        self.inning = -1
        self.current_batter = -1
        self.current_base = [0, -1, -1, -1]     ##現在各ベースにいる選手の打順
        self.newInning()

    def newInning(self):
        if self.inning < 8:
            self.inning += 1
            self.ball_count = 0
            self.strike_count = 0
            self.out_count = 0
            self.nextBatter()
            self.setNewBall()
            self.current_base = [self.current_batter, -1, -1, -1]
            for player in self.top_players:
                if player.onBase != -1 and player.position != self.current_base:
                    player.onBase = -1
            self.ground.resetRunners(self.current_base)
        else:
            self.records.append(self.points)
            self.sumrecords.append(np.sum(self.points))
            print(self.records)
            self.games += 1
            self.points = [0 for _ in range(9)]
            self.newGame()

    def setNewBall(self):
        pitcher = self.bottom_players[0]
        for player in self.bottom_players:
            player.initialize()
            if player.position == 0:
                pitcher = player
                self.ball.initialize()
                player.hasBall = True
            else:
                player.hasBall = False

        #print('(next batter) runners back to base: ', end='')
        #print('(new ball) ' + str(self.current_base))
        for i in range(len(self.current_base)):
            #print(self.current_base[i])
            if self.current_base[i] != -1:
                self.top_players[self.current_base[i]].backToBase(i, self.ground.bases[i])
        #print()
        #time.sleep(3)
        for i in range(4):
            self.ground.bases[i].isSteped = False

        pitcher.pitchTheBall(self.ball)

    def out(self, i):
        print('player ' + str(i) + ' is OUT !')
        self.out_count += 1
        self.top_players[i].onBase = -1
        for index in range(len(self.ground.running)):
            if self.ground.running[index] == i:
                self.ground.running[index] = -1
        for base in self.ground.bases:
            if base.runner == i:
                base.deleteRunner()
        if self.out_count == 3:
            self.newInning()

    def judge(self):
        ## ボールが停止かつ走塁中のランナーがいなくなれば ball.mode = TIME
        #print('(judge) running: ' + str(self.ground.running) + ', has runner?: ' +  str(self.ground.hasRunner()) + ', ball is stop? ' + str(self.ball.isStop))
        #print('(judge) ball speed: ' + str(np.sqrt(self.ball.vel[0] * self.ball.vel[0] + self.ball.vel[1] * self.ball.vel[1] + self.ball.vel[2] * self.ball.vel[2])))
        if self.ball.isStop and not self.ground.hasRunner():
            self.ball.mode = status.TIME
            self.nextBatter()
            return

        if self.ball.mode == status.FRYCAUGHT:
            print('a fry ball is caught')
            self.out(self.ball.hittedBy)
            self.ball.mode = status.HITTED
        ## ここで各塁におけるセーフアウトを判定する
        for i in range(4):
            baseman = self.bottom_players[0]
            for p in self.bottom_players:
                if p.stepBase == i:
                    baseman = p
            runner = self.ground.running[(i-1)%4]
            #print('(judge) ' + str(i) + ' runner: ' + str(runner) + ', player has ball?: ' + str(baseman.hasBall) + ', base is steped: ' + str(self.ground.bases[i].isSteped))
            if runner != -1 and baseman.hasBall and self.ground.bases[i].isSteped:
                self.out(runner)

    def nextBatter(self):
        self.current_batter = (self.current_batter + 1) % 9
        self.current_base[0] = self.current_batter
        self.ground.setRunners(0, self.current_batter)
        #print('next batter is ' + str(self.current_batter))
        self.top_players[self.current_batter].onBase = 0
        self.ball.mode = status.TIME
        self.ball_count = 0
        self.strike_count = 0

        #print('(next batter) update runners: ', end='')
        for i in range(4):
            self.ground.bases[i].isSteped = False
            runner = self.ground.bases[i].runner
            self.current_base[i] = runner
            #print(str(i) + ': ' + str(runner) + ', ', end='')
        #print()

    def management(self):
        #print(self.ball.mode)
        #print(self.ball.pos)
        #print("(management) running: " + str(self.ground.running))
        #print('(management) on base players: ', end='')
        #for i in range(4):
        #    runner = self.ground.bases[i].runner
        #    print(str(i) + ': ' + str(runner) + ', ', end='')
        #print()
        #print('(management) top players: ', end='')
        #for p in self.top_players:
        #    print(str(p.position) + ': ' + str(p.onBase) + ', ', end="")
        #print()
        if self.ball.mode == status.TIME:
            # タイム中
            print('PLAY !')
            self.setNewBall()
        elif self.ball.mode == status.PITCHED or self.ball.mode == status.LOOKED:
            # 投球後
            cs = self.top_players[self.current_base[0]].hitting(self.ball)
            #print(cs)
            # 見逃した時
            self.bottom_players[1].catchThePitch(self.ball)
            if cs == 'looked':
                r = random.random()
                if r > 0.7:
                    self.strike_count += 1
                    if self.strike_count == 3:
                        self.out(self.current_base[0])
                        self.ball.mode = status.TIME
                        self.nextBatter()
                else:
                    self.ball_count += 1
                    #if self.ball_count == 4:
                    #    for b in self.ground.bases:
                    #        flg = False
                    #        if b.runner == -1:
                    #            flg = True
                    #        b.next.setRunner(b.runner)
                    #        if flg:
                    #            break
                    #    self.ball.mode = status.TIME
                    #    self.nextBatter()
        elif self.ball.mode == status.HOMERUN:
            # HOMERUN時
            for player in self.top_players:
                if player.onBase != -1:
                    self.points[self.inning] += player.move_attack(self.ball, self.ground, self.current_base[0])
            flg = True
            for b in self.ground.bases:
                #print('base ' + str(b) + ': ' + str(b.runner))
                if b.runner != -1:
                    flg = False
            if flg:
                self.ball.mode = status.TIME
                self.nextBatter()
            return
        else:   # 打った時
            bs = self.ball.status()
            if bs == 'foul':    # ファール
                if self.strike_count < 2:
                    self.strike_count += 1
                self.ball.mode = status.TIME
                self.ground.resetRunners(self.current_base)
            elif bs == 'balldead':
                self.ball.mode = status.TIME
                self.nextBatter()
            else:               # フェア
                for player in self.top_players:
                    if player.onBase != -1:
                        self.points[self.inning] += player.move_attack(self.ball, self.ground, self.current_base[0])

                if bs != 'homerun':
                    #nearest = self.ball.computeNearestPlayer(self.bottom_players)
                    for player in self.bottom_players:
                        player.judgeCatch(self.ball, self.ground)
                        if not player.hasBall:
                            player.move_defence(self.ball, self.ground)
                        else:
                            player.judgeThrow(self.ball, self.ground)
                else:
                    print('+++ HOMERUN! +++')

                self.judge()

# -*- coding: utf-8 -*-

import numpy as np

base_locs = [[315, 480], [415, 350], [295, 250], [175, 350]]

class Ground():
    def __init__(self):
        home = Base(base_locs[0], 0)
        first = Base(base_locs[1], 1)
        second = Base(base_locs[2], 2)
        third = Base(base_locs[3], 3)

        home.setNext(first)
        first.setNext(second)
        second.setNext(third)
        third.setNext(home)
        home.setBack(third)
        first.setBack(home)
        second.setBack(first)
        third.setBack(second)

        self.bases = [home, first, second, third]
        self.running = [-1, -1, -1, -1] # 塁間に走者がいるかどうかを管理する配列

    def resetRunners(self, list):
        #print('(reset runners): ' + str(list))
        for (i, l) in enumerate(list):
            self.bases[i].runner = l
            self.running[i] = -1
            #print(str(i) + ' on base: ' + str(self.bases[i].runner) + ', running: ' + str(self.running[i]))

    def setRunners(self, base, i):
        self.bases[base].setRunner(i)

        if base != 0:
            if self.running[base-1] == i:
                self.running[base-1] = -1
        else:
            if self.running[3] == i:
                self.running[3] = -1

    def runFrom(self, i, runner):
        #print('(run from): base ' + str(i) + ' has ' + str(runner))
        self.running[i] = runner

    def hasRunner(self):
        b = False
        #print('(hasRunner) ' + str(self.running))
        for r in self.running:
            if r != -1:
                b = True
        return b

    def cannotGo(self, i, me):
        if i == 3:
            return False
        if self.bases[i].next.runner != -1 and self.running[i+1] == -1 or self.running[i] != -1 and self.running[i] != me:
            return True
        return False

    def mustGo(self, i, me):
        if self.bases[i].runner != -1 and self.bases[i].runner != me:
            return True
        ans = True
        for b in range(0, i):
            if self.bases[b].runner == -1:
                ans = False
        return ans

class Base():
    def __init__(self, loc, id):
        self.loc = loc
        self.id = id
        self.runner = -1
        self.isSteped = False

    def setNext(self, next):
        self.next = next

    def setBack(self, back):
        self.back = back

    def getNextBaseDirection(self, pos):
        x = self.next.loc[0] - pos[0]
        y = self.next.loc[1] - pos[1]
        dis = np.sqrt(x*x+y*y)

        return x, y, dis

    def getBackBaseDirection(self, pos):
        x = self.loc[0] - pos[0]
        y = self.loc[1] - pos[1]
        dis = np.sqrt(x*x+y*y)

        return x, y, dis

    def setRunner(self, i):
        #print('(set runner) on ' + str(self.id) + ': ' + str(i))
        if i != -1 and self.back.runner == i:
            self.back.setRunner(-1)
        self.runner = i

    def deleteRunner(self):
        self.runner = -1

    def safetyToGoNext(self, ball, run):
        if self.loc == base_locs[0]:
            return True
        x = self.next.loc[0] - ball.pos[0]
        y = self.next.loc[1] - ball.pos[1]
        dis = np.sqrt(x*x+y*y)

        x2 = self.next.loc[0] - run[0]
        y2 = self.next.loc[1] - run[1]
        dis2 = np.sqrt(x2*x2+y2*y2)
        return dis - dis2 > 100 or dis2 < 50

# -*- coding: utf-8 -*-
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
import time

from ball import Ball, b_default, status
from game import Game
from member import Member

class MainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self, flags=Qt.Window)
        self.resize(800, 600)
        self.setWindowTitle('Baseball Simulator')

        self.move(0, 0)
        self.ball = Ball(self)
        self.initItems()

        self.game = Game(self, self.ball)

        self.members = []
        for p in self.game.top_players:
            self.members.append(Member(p, self))

        self.balllabel = QLabel(self)
        self.ballpixmap = QPixmap('img/ball.png')


    def initItems(self):
        self.groundpixmap = QPixmap('img/ground.png')
        h = self.size().height()
        self.groundpixmap = self.groundpixmap.scaled(h, h, Qt.KeepAspectRatio)
        self.groundlabel = QLabel(self)
        self.groundlabel.setPixmap(self.groundpixmap)
        self.groundlabel.move(int(5), int(h/10))

        B = QLabel(self)
        B.setText('B')
        B.setFont(QFont('Times', 20, QFont.Bold))
        B.setStyleSheet('QLabel { color: white; }')
        B.setGeometry(450, 452, 30, 25)
        B.setAlignment(Qt.AlignCenter)
        B.show()

        S = QLabel(self)
        S.setText('S')
        S.setFont(QFont('Times', 20, QFont.Bold))
        S.setStyleSheet('QLabel { color: white; }')
        S.setGeometry(450, 477, 30, 25)
        S.setAlignment(Qt.AlignCenter)
        S.show()

        O = QLabel(self)
        O.setText('O')
        O.setFont(QFont('Times', 20, QFont.Bold))
        O.setStyleSheet('QLabel { color: white; }')
        O.setGeometry(450, 502, 30, 25)
        O.setAlignment(Qt.AlignCenter)
        O.show()

        self.pointlabels = [QLabel(self) for _ in range(9)]
        for i in range(9):
            self.pointlabels[i].setFont(QFont('Times', 20, QFont.Bold))
            self.pointlabels[i].setStyleSheet('QLabel { color: white; }')
            self.pointlabels[i].setGeometry(490+i*30, 23, 30, 30)
            self.pointlabels[i].setAlignment(Qt.AlignCenter)

        self.sumlabel = QLabel(self)
        self.sumlabel.setFont(QFont('Times', 20, QFont.Bold))
        self.sumlabel.setStyleSheet('QLabel { color: white; }')
        self.sumlabel.setGeometry(760, 23, 30, 30)
        self.sumlabel.setAlignment(Qt.AlignCenter)

        self.avglabels = [QLabel(self) for _ in range(10)]
        for i in range(10):
            self.avglabels[i].setFont(QFont('Times', 20, QFont.Bold))
            self.avglabels[i].setStyleSheet('QLabel { color: white; }')
            self.avglabels[i].setGeometry(490+i*30, 53, 30, 30)
            self.avglabels[i].setAlignment(Qt.AlignCenter)

        titleA = QLabel(self)
        titleA.setText('this')
        titleA.setFont(QFont('Times', 20, QFont.Bold))
        titleA.setStyleSheet('QLabel { color: white; }')
        titleA.setGeometry(450, 23, 40, 30)
        titleA.setAlignment(Qt.AlignCenter)
        titleA.show()

        titleB = QLabel(self)
        titleB.setText('avg')
        titleB.setFont(QFont('Times', 20, QFont.Bold))
        titleB.setStyleSheet('QLabel { color: white; }')
        titleB.setGeometry(450, 53, 40, 30)
        titleB.setAlignment(Qt.AlignCenter)
        titleB.show()

        gamelabel = QLabel(self)
        gamelabel.setText('game: ')
        gamelabel.setFont(QFont('Times', 20, QFont.Bold))
        gamelabel.setStyleSheet('QLabel { color: white; }')
        gamelabel.setGeometry(650, 90, 80, 30)
        gamelabel.setAlignment(Qt.AlignCenter)
        gamelabel.show()

        self.gameCountlabel = QLabel(self)
        self.gameCountlabel.setFont(QFont('Times', 20, QFont.Bold))
        self.gameCountlabel.setStyleSheet('QLabel { color: white; }')
        self.gameCountlabel.setGeometry(730, 90, 40, 30)
        self.gameCountlabel.setAlignment(Qt.AlignCenter)
        self.gameCountlabel.show()

        inninglabel = QLabel(self)
        inninglabel.setText('inning: ')
        inninglabel.setFont(QFont('Times', 20, QFont.Bold))
        inninglabel.setStyleSheet('QLabel { color: white; }')
        inninglabel.setGeometry(650, 120, 80, 30)
        inninglabel.setAlignment(Qt.AlignCenter)
        inninglabel.show()

        self.inningCountlabel = QLabel(self)
        self.inningCountlabel.setFont(QFont('Times', 20, QFont.Bold))
        self.inningCountlabel.setStyleSheet('QLabel { color: white; }')
        self.inningCountlabel.setGeometry(730, 120, 40, 30)
        self.inningCountlabel.setAlignment(Qt.AlignCenter)
        self.inningCountlabel.show()

    def drawBall(self):
        s = int(b_default + self.ball.pos[2])
        self.balllabel.resize(s, s)
        self.balllabel.move(int(self.ball.pos[0]), int(self.ball.pos[1]))
        self.balllabel.setPixmap(self.ballpixmap.scaled(s, s, Qt.KeepAspectRatio))
        #self.balllabel.show()

    def drawCountBoard(self):
        painter = QPainter(self)
        painter.setPen(Qt.white)
        painter.drawRect(450, 450, 120, 75)

        for i in range(3):
            if self.game.ball_count > i:
                painter.setBrush(Qt.green)
            else:
                painter.setBrush(Qt.black)
            painter.drawEllipse(480 + i * 30, 452, 20, 20)

        for i in range(2):
            if self.game.strike_count > i:
                painter.setBrush(Qt.yellow)
            else:
                painter.setBrush(Qt.black)
            painter.drawEllipse(480 + i * 30, 477, 20, 20)

        for i in range(2):
            if self.game.out_count > i:
                painter.setBrush(Qt.red)
            else:
                painter.setBrush(Qt.black)
            painter.drawEllipse(480 + i * 30, 502, 20, 20)

    def drawMemberSheet(self):
        for m in self.members:
            m.draw()

    def drawScoreBoard(self):
        painter = QPainter(self)
        painter.setPen(Qt.white)
        painter.drawRect(450, 20, 340, 60)
        for i in range(10):
            painter.drawLine(490+i*30, 20, 490+i*30, 80)
        painter.drawLine(450, 50, 790, 50)

        for i in range(9):
            if i < self.game.inning or self.game.points[i] > 0:
                self.pointlabels[i].setText(str(self.game.points[i]))
                if self.game.games == 0:
                    self.avglabels[i].setText(str(self.game.points[i]))
            else:
                self.pointlabels[i].setText('-')
                if self.game.games == 0:
                    self.avglabels[i].setText('-')

        if self.game.games != 0:
            list = np.mean(self.game.records, axis=0)
            for i in range(len(self.avglabels)-1):
                self.avglabels[i].setText(str(list[i]))
            self.avglabels[9].setText(str(np.mean(self.game.sumrecords)))
        else:
            self.avglabels[9].setText(str(np.sum(self.game.points)))
        self.sumlabel.setText(str(np.sum(self.game.points)))
        self.gameCountlabel.setText(str(self.game.games+1))
        self.inningCountlabel.setText(str(self.game.inning+1))

    def paintEvent(self, QPaintEvent):
        time.sleep(0.1)
        if self.ball.mode == status.TIME:
            time.sleep(0.5)
        self.drawCountBoard()
        self.drawMemberSheet()
        self.drawScoreBoard()

        self.game.drawPlayers()
        self.ball.move()
        self.drawBall()
        self.game.management()
        self.update()

    #def mousePressEvent(self, event):
        #first_line = [1, -1]
        #print('pos x: ' + str(event.x()) + ', y: ' + str(event.y()))
        #pos = [event.x()- 305, event.y()-498]
        #i = np.inner(pos, first_line)
        #theta = np.arccos(i / (np.linalg.norm(pos) * np.linalg.norm(first_line)))
        #deg = np.degrees(theta)
        #y = -event.x() + 305 + 498
        #print('degree: ' + str(deg) + ', y: ' + str(event.y()-y))

    def main(self):
        for i in range(9):
            print('batter ' + str(i+1))
            self.game.top_players[i].contact = int(input('input the contact ability in 1 to 5: '))
            self.game.top_players[i].power = int(input('input the power ability in 1 to 5: '))

        self.game.newGame()
        time.sleep(3)
        self.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.main()

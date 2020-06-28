# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Member():
    def __init__(self, player, mw):
        self.player = player
        self.mw = mw
        self.id = self.player.position
        self.pos = QLabel(mw)
        self.pos.setFont(QFont('Times', 20, QFont.Bold))
        self.pos.setAlignment(Qt.AlignCenter)

        contact = QLabel(self.mw)
        contact.setFont(QFont('Times', 15, QFont.Bold))
        contact.setAlignment(Qt.AlignLeft)
        contact.setText('contact:')
        contact.setGeometry(600, 305 + self.id*25, 50, 25)
        contact.show()

        power = QLabel(self.mw)
        power.setFont(QFont('Times', 15, QFont.Bold))
        power.setAlignment(Qt.AlignLeft)
        power.setText('power:')
        power.setGeometry(700, 305 + self.id*25, 50, 25)
        power.show()

        self.c = QLabel(self.mw)
        self.c.setFont(QFont('Times', 20, QFont.Bold))
        self.c.setAlignment(Qt.AlignRight)
        self.c.setText(str(self.player.contact))
        self.c.setGeometry(660, 300 + self.id*25, 30, 25)
        self.c.show()

        self.p = QLabel(self.mw)
        self.p.setFont(QFont('Times', 20, QFont.Bold))
        self.p.setAlignment(Qt.AlignRight)
        self.p.setGeometry(750, 300 + self.id*25, 30, 25)
        self.p.show()

    def draw(self):
        if self.player.onBase == -1:
            self.pos.setText(str(self.id+1))
            self.pos.setStyleSheet('QLabel { color: white; }')
        elif self.player.onBase == 0:
            self.pos.setText('B')
            self.pos.setStyleSheet('QLabel { color: orange; }')
        else:
            self.pos.setText('R')
            self.pos.setStyleSheet('QLabel { color: gray; }')
        self.pos.setGeometry(570, 300 + self.id*25, 30, 25)
        self.pos.show()

        self.c.setText(str(self.player.contact))

        self.p.setText(str(self.player.power))

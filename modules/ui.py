from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QPushButton, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

STYLE = """
QMainWindow { background-color: #0f1016; }
QLabel { color: #00f2ff; font-family: 'Segoe UI'; }
QListWidget { 
    background-color: #161b22; border: none; border-radius: 6px; 
    color: #e6edf3; font-family: 'Consolas'; font-size: 13px; padding: 10px;
}
QPushButton {
    background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d;
    padding: 10px; border-radius: 6px; font-weight: 600;
}
QPushButton:hover { background-color: #30363d; }
QPushButton#scanBtn { background-color: #238636; color: white; }
QPushButton#kickBtn { background-color: #da3633; color: white; }
"""

class Ui_Dashboard(object):
    def setupUi(self, main_window):
        main_window.setWindowTitle("Net-Sentinel Pro v2")
        main_window.setMinimumSize(850, 550)
        main_window.setStyleSheet(STYLE)

        self.central = QWidget()
        main_window.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.info_lbl = QLabel("SİSTEM HAZIR")
        self.info_lbl.setFont(QFont("Segoe UI", 10))
        self.layout.addWidget(self.info_lbl)

        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        self.btn_box = QHBoxLayout()
        self.btn_scan = QPushButton("AĞI TARA")
        self.btn_scan.setObjectName("scanBtn")
        self.btn_graph = QPushButton("CANLI İZLE")
        self.btn_kick = QPushButton("BAĞLANTI KES")
        self.btn_kick.setObjectName("kickBtn")

        self.btn_box.addWidget(self.btn_scan)
        self.btn_box.addWidget(self.btn_graph)
        self.btn_box.addWidget(self.btn_kick)
        self.layout.addLayout(self.btn_box)
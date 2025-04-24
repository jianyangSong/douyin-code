#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
桌面像素宠物主程序
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from pet import DesktopPet

if __name__ == "__main__":
    # 禁用高DPI缩放，保持像素清晰
    QApplication.setAttribute(Qt.AA_DisableHighDpiScaling)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.Floor)
    
    app = QApplication(sys.argv)
    
    # 创建桌面宠物实例
    pet = DesktopPet()
    pet.show()
    
    sys.exit(app.exec_()) 
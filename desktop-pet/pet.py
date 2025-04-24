#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
桌面宠物核心逻辑模块
实现了动画播放、运动逻辑和交互功能
"""

import os
import random
import time
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect, QSize
from PyQt5.QtGui import QPixmap, QPainter, QCursor, QTransform
from PyQt5.QtWidgets import (QWidget, QMenu, QAction, QDesktopWidget, 
                            QLabel, QVBoxLayout, QApplication)
from memo import MemoWindow
from monitor import SystemMonitor

class DesktopPet(QWidget):
    """桌面宠物主类"""
    
    def __init__(self):
        super().__init__()
        
        # 属性初始化
        self.state = "IDLE"  # 初始状态：待机
        self.direction = random.choice([1, -1])   # 初始方向随机
        self.frame_index = 0  # 当前帧索引
        self.scale_factor = 4  # 默认放大4倍
        self.fps = 15         # 默认15帧/秒
        self.speed = 4        # 移动速度，从2增加到4
        self.is_paused = False # 是否暂停
        self.is_dragging = False # 是否拖拽中
        self.drag_offset = QPoint() # 拖拽偏移量
        self.position_y = 0    # 当前Y坐标，用于保持垂直位置
        self.position_x = 0    # 当前X坐标，用于保持水平位置
        self.first_move = True  # 标记是否第一次移动，用于初始化位置
        
        # 动画帧资源
        self.frames = {
            "IDLE": [],  # 待机动画帧
            "WALK": []   # 行走动画帧
        }
        
        # 加载资源
        self.load_frames()
        
        # 窗口设置
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        
        # 初始位置：屏幕右下角
        screen_geo = QDesktopWidget().availableGeometry()
        x = screen_geo.width() - self.width() - 50
        y = screen_geo.height() - self.height() - 50
        self.move(x, y)
        
        # 动画计时器 - 提高帧率
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(1000 // 20)  # 提高到20帧/秒
        
        # 状态切换计时器 - 增加切换频率
        self.state_timer = QTimer(self)
        self.state_timer.timeout.connect(self.random_state_change)
        self.state_timer.start(random.randint(1500, 4000))  # 减少状态切换间隔
        
        # 系统监控悬停计时器
        self.hover_timer = QTimer(self)
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self.show_system_monitor)
        
        # 初始化子窗口
        self.memo_window = None
        self.monitor_window = None
        
        # 连接应用退出信号
        QApplication.instance().aboutToQuit.connect(self.cleanup)
    
    def load_frames(self):
        """加载动画帧资源"""
        # 清空现有帧
        self.frames["IDLE"].clear()
        self.frames["WALK"].clear()
        
        # 检查帧是否全部成功加载的标志
        all_frames_loaded = True
        
        # 加载待机动画帧
        for i in range(5):
            path = os.path.join("frames", f"idle_{i}.png")
            pixmap = QPixmap(path)
            
            # 确保图像不被平滑处理
            if pixmap.isNull():
                print(f"警告: 无法加载图像: {path}")
                all_frames_loaded = False
                continue
                
            self.frames["IDLE"].append(pixmap)
        
        # 加载行走动画帧
        for i in range(6):
            path = os.path.join("frames", f"walk_{i}.png")
            pixmap = QPixmap(path)
            
            # 确保图像不被平滑处理
            if pixmap.isNull():
                print(f"警告: 无法加载图像: {path}")
                all_frames_loaded = False
                continue
                
            self.frames["WALK"].append(pixmap)
        
        # 检查是否所有帧都成功加载
        if not self.frames["IDLE"] or not self.frames["WALK"]:
            print("错误: 无法加载必要的动画帧！")
            QApplication.instance().quit()
            return
            
        # 如果有帧缺失，给出警告
        if not all_frames_loaded:
            print("警告: 部分动画帧缺失，程序可能无法正常运行")
        
        # 更新窗口尺寸
        self.update_size()
    
    def update_size(self):
        """更新窗口尺寸"""
        if not self.frames["IDLE"]:
            return
            
        # 根据放大因子调整窗口大小，确保使用整数倍缩放
        orig_size = self.frames["IDLE"][0].size()
        scaled_width = orig_size.width() * self.scale_factor
        scaled_height = orig_size.height() * self.scale_factor
        
        # 设置窗口大小为整数像素值
        self.setFixedSize(int(scaled_width), int(scaled_height))
    
    def update_animation(self):
        """更新动画帧和位置"""
        if self.is_paused:
            return
            
        # 获取当前状态的帧列表
        frames = self.frames[self.state]
        if not frames:
            return
            
        # 更新帧索引
        self.frame_index = (self.frame_index + 1) % len(frames)
        
        # 如果是行走状态，更新位置
        if self.state == "WALK":
            self.move_pet()
        
        # 触发重绘
        self.update()
    
    def move(self, x, y):
        """重写move方法，在移动时保存当前位置"""
        super().move(x, y)
        # 保存当前位置
        self.position_x = x
        self.position_y = y
    
    def move_pet(self):
        """移动宠物位置"""
        # 如果是第一次移动，初始化位置
        if self.first_move:
            pos = self.pos()
            self.position_x = pos.x()
            self.position_y = pos.y()
            self.first_move = False
            
        # 计算移动距离，确保为整数像素
        distance = int(self.speed * self.direction * (self.scale_factor / 4))
        
        # 计算新的X坐标
        new_x = self.position_x + distance
        
        # 检查边界碰撞
        screen_geo = QDesktopWidget().availableGeometry()
        if new_x <= 0:
            # 碰到左边界，改变方向
            new_x = 0
            self.direction = 1  # 确保方向值为1，代表向右
            self.frame_index = 0
        elif new_x + self.width() >= screen_geo.width():
            # 碰到右边界，改变方向
            new_x = screen_geo.width() - self.width()
            self.direction = -1  # 确保方向值为-1，代表向左
            self.frame_index = 0
        
        # 更新位置，使用当前保存的Y坐标
        super().move(int(new_x), int(self.position_y))
        self.position_x = new_x  # 更新保存的X坐标
    
    def random_state_change(self):
        """随机改变状态"""
        if not self.is_paused and not self.is_dragging:
            # 有80%概率切换状态，提高变化概率
            if random.random() < 0.8:
                self.state = "WALK" if self.state == "IDLE" else "IDLE"
                
                # 如果切换到行走状态且当前静止，随机选择移动方向
                if self.state == "WALK":
                    # 20%的概率改变方向（如果宠物静止）
                    if random.random() < 0.2:
                        self.direction = random.choice([1, -1])
            
            # 重设随机切换计时器，间隔更短
            self.state_timer.start(random.randint(1500, 4000))
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        # 禁用平滑渲染，保持像素风格的清晰度
        painter.setRenderHint(QPainter.SmoothPixmapTransform, False)
        
        # 获取当前帧
        frames = self.frames[self.state]
        if not frames or self.frame_index >= len(frames):
            return
            
        # 获取当前帧图像
        pixmap = frames[self.frame_index]
        
        # 根据方向翻转图像
        if self.direction == -1:
            # 修复翻转问题，使用正确的QTransform
            transform = QTransform().scale(-1, 1)
            pixmap = pixmap.transformed(transform, Qt.FastTransformation)
        
        # 计算源矩形和目标矩形
        src_rect = QRect(0, 0, pixmap.width(), pixmap.height())
        dest_rect = QRect(0, 0, self.width(), self.height())
        
        # 绘制图像，确保像素保持清晰
        painter.drawPixmap(dest_rect, pixmap, src_rect)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 记录拖拽偏移量
            self.is_dragging = True
            self.drag_offset = event.pos()
        
        # 无论什么按钮，都重置悬停计时器
        self.hover_timer.stop()
        
        # 确保系统监控窗口关闭
        if self.monitor_window:
            self.monitor_window.close()
            self.monitor_window = None
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            # 记录是否是拖拽操作
            was_dragging = self.is_dragging and self.drag_offset != event.pos()
            
            # 结束拖拽状态
            self.is_dragging = False
            
            # 如果是拖拽操作，更新位置
            if was_dragging:
                current_pos = self.pos()
                self.position_y = current_pos.y()
            else:
                # 如果是点击而非拖拽，切换暂停状态
                self.is_paused = not self.is_paused
    
    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件"""
        if event.button() == Qt.LeftButton:
            self.open_memo()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.is_dragging:
            # 拖拽时移动窗口
            new_pos = event.globalPos() - self.drag_offset
            super().move(new_pos.x(), new_pos.y())
            # 直接保存新位置
            self.position_x = new_pos.x()
            self.position_y = new_pos.y()
            self.first_move = False  # 已经有确定位置了
        else:
            # 悬停时启动计时器显示系统监控
            self.hover_timer.start(2000)  # 2秒后显示
    
    def contextMenuEvent(self, event):
        """右键菜单事件"""
        menu = QMenu(self)
        
        # 备忘录菜单项
        memo_action = QAction("打开备忘录", self)
        memo_action.triggered.connect(self.open_memo)
        menu.addAction(memo_action)
        
        menu.addSeparator()
        
        # 状态切换菜单项
        if self.state == "IDLE":
            state_action = QAction("切换到行走状态", self)
            state_action.triggered.connect(lambda: self.set_state("WALK"))
        else:
            state_action = QAction("切换到待机状态", self)
            state_action.triggered.connect(lambda: self.set_state("IDLE"))
        menu.addAction(state_action)
        
        menu.addSeparator()
        
        # 尺寸调整菜单
        size_menu = menu.addMenu("显示尺寸")
        
        increase_size = QAction("放大显示", self)
        increase_size.triggered.connect(self.increase_size)
        size_menu.addAction(increase_size)
        
        decrease_size = QAction("缩小显示", self)
        decrease_size.triggered.connect(self.decrease_size)
        size_menu.addAction(decrease_size)
        
        # 速度调整菜单
        speed_menu = menu.addMenu("动画速度")
        
        increase_fps = QAction("加快速度", self)
        increase_fps.triggered.connect(self.increase_fps)
        speed_menu.addAction(increase_fps)
        
        decrease_fps = QAction("减慢速度", self)
        decrease_fps.triggered.connect(self.decrease_fps)
        speed_menu.addAction(decrease_fps)
        
        menu.addSeparator()
        
        # 退出菜单项
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(exit_action)
        
        # 显示菜单
        menu.exec_(event.globalPos())
    
    def set_state(self, state):
        """设置宠物状态"""
        if state in ["IDLE", "WALK"]:
            self.state = state
            self.frame_index = 0
            self.update()
    
    def increase_size(self):
        """增加显示尺寸"""
        if self.scale_factor < 8:
            self.scale_factor += 1
            self.update_size()
    
    def decrease_size(self):
        """减小显示尺寸"""
        if self.scale_factor > 1:
            self.scale_factor -= 1
            self.update_size()
    
    def increase_fps(self):
        """增加动画帧率"""
        if self.fps < 30:
            self.fps += 5  # 增加加速幅度
            self.animation_timer.setInterval(1000 // self.fps)
    
    def decrease_fps(self):
        """减小动画帧率"""
        if self.fps > 6:
            self.fps -= 5  # 增加减速幅度
            self.animation_timer.setInterval(1000 // self.fps)
    
    def open_memo(self):
        """打开备忘录"""
        if not self.memo_window:
            self.memo_window = MemoWindow(self)
        
        self.memo_window.show()
        self.memo_window.raise_()
        self.memo_window.activateWindow()
    
    def show_system_monitor(self):
        """显示系统监控窗口"""
        # 如果鼠标仍在宠物窗口内，则显示系统监控
        if self.rect().contains(self.mapFromGlobal(QCursor.pos())):
            if not self.monitor_window:
                self.monitor_window = SystemMonitor(self)
                
            # 计算窗口位置，显示在宠物旁边
            pet_pos = self.pos()
            pet_size = self.size()
            monitor_pos = QPoint(pet_pos.x() + pet_size.width() + 10, pet_pos.y())
            
            self.monitor_window.move(monitor_pos)
            self.monitor_window.show()
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        # 停止悬停计时器
        self.hover_timer.stop()
        
        # 关闭系统监控窗口
        if self.monitor_window:
            self.monitor_window.close()
            self.monitor_window = None
    
    def cleanup(self):
        """清理资源"""
        # 关闭所有计时器
        self.animation_timer.stop()
        self.state_timer.stop()
        self.hover_timer.stop()
        
        # 关闭所有子窗口
        if self.memo_window:
            self.memo_window.close()
        
        if self.monitor_window:
            self.monitor_window.close() 
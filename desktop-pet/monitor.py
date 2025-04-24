#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统监控功能模块
实现像素风格UI的系统资源监控，包括CPU使用率、内存使用率和网络流量
"""

import os
import time
import psutil
from PyQt5.QtCore import Qt, QTimer, QRect, QSize
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QPaintEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

class ProgressBar(QWidget):
    """像素风格进度条"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.setFixedHeight(20)
        self.setMinimumWidth(200)
    
    def set_value(self, value):
        """设置进度条值（0-100）"""
        self.value = max(0, min(100, value))
        self.update()
    
    def paintEvent(self, event):
        """绘制进度条"""
        painter = QPainter(self)
        
        # 绘制背景
        painter.fillRect(self.rect(), QColor(34, 34, 34))
        
        # 绘制边框
        pen = QPen(QColor(102, 102, 102))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        
        # 绘制进度
        if self.value > 0:
            # 计算进度宽度
            progress_width = int((self.width() - 4) * self.value / 100)
            
            # 选择颜色：根据值改变颜色
            if self.value < 60:
                color = QColor(50, 205, 50)  # 绿色
            elif self.value < 80:
                color = QColor(255, 165, 0)  # 橙色
            else:
                color = QColor(220, 20, 60)  # 红色
                
            # 绘制进度矩形
            painter.fillRect(2, 2, progress_width, self.height() - 4, color)
            
            # 像素化效果：每隔几个像素留一个小间隔
            pixel_size = 4
            for x in range(2, 2 + progress_width, pixel_size):
                for y in range(2, self.height() - 4, pixel_size):
                    painter.fillRect(
                        x, y, pixel_size - 1, pixel_size - 1, 
                        QColor(color.red() + 20, color.green() + 20, color.blue() + 20)
                    )

class SystemMonitor(QWidget):
    """系统监控窗口类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 窗口设置
        self.setWindowTitle("系统监控")
        self.setFixedSize(250, 180)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # 网络数据缓存
        self.last_net_io = psutil.net_io_counters()
        self.last_net_time = time.time()
        
        # 初始化UI
        self.init_ui()
        
        # 启动更新计时器
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(1000)  # 每秒更新一次
        
        # 首次更新数据
        self.update_stats()
    
    def init_ui(self):
        """初始化UI"""
        # 主布局
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 标题标签
        title_label = QLabel("系统监控", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Courier New", 14, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        layout.addWidget(title_label)
        
        # CPU 监控
        cpu_layout = QHBoxLayout()
        cpu_label = QLabel("CPU:", self)
        cpu_label.setFont(QFont("Courier New", 10))
        cpu_label.setStyleSheet("color: white;")
        cpu_layout.addWidget(cpu_label)
        
        self.cpu_value = QLabel("0%", self)
        self.cpu_value.setFont(QFont("Courier New", 10))
        self.cpu_value.setStyleSheet("color: white;")
        self.cpu_value.setFixedWidth(50)
        self.cpu_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cpu_layout.addWidget(self.cpu_value)
        
        layout.addLayout(cpu_layout)
        
        # CPU 进度条
        self.cpu_progress = ProgressBar(self)
        layout.addWidget(self.cpu_progress)
        
        # 内存监控
        mem_layout = QHBoxLayout()
        mem_label = QLabel("内存:", self)
        mem_label.setFont(QFont("Courier New", 10))
        mem_label.setStyleSheet("color: white;")
        mem_layout.addWidget(mem_label)
        
        self.mem_value = QLabel("0%", self)
        self.mem_value.setFont(QFont("Courier New", 10))
        self.mem_value.setStyleSheet("color: white;")
        self.mem_value.setFixedWidth(50)
        self.mem_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        mem_layout.addWidget(self.mem_value)
        
        layout.addLayout(mem_layout)
        
        # 内存进度条
        self.mem_progress = ProgressBar(self)
        layout.addWidget(self.mem_progress)
        
        # 网络监控
        net_layout = QHBoxLayout()
        net_label = QLabel("网络:", self)
        net_label.setFont(QFont("Courier New", 10))
        net_label.setStyleSheet("color: white;")
        net_layout.addWidget(net_label)
        
        # 布局微调
        net_layout.addStretch()
        
        # 下载速度
        self.down_label = QLabel("↓ 0 KB/s", self)
        self.down_label.setFont(QFont("Courier New", 10))
        self.down_label.setStyleSheet("color: #3CB371;")  # 绿色
        net_layout.addWidget(self.down_label)
        
        # 上传速度
        self.up_label = QLabel("↑ 0 KB/s", self)
        self.up_label.setFont(QFont("Courier New", 10))
        self.up_label.setStyleSheet("color: #FF6347;")  # 红色
        net_layout.addWidget(self.up_label)
        
        layout.addLayout(net_layout)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QWidget {
                background-color: #222222;
                color: white;
                border: 2px solid #666666;
            }
        """)
    
    def update_stats(self):
        """更新系统统计信息"""
        # 更新CPU使用率
        cpu_percent = psutil.cpu_percent()
        self.cpu_value.setText(f"{cpu_percent:.1f}%")
        self.cpu_progress.set_value(cpu_percent)
        
        # 更新内存使用率
        mem = psutil.virtual_memory()
        mem_percent = mem.percent
        self.mem_value.setText(f"{mem_percent:.1f}%")
        self.mem_progress.set_value(mem_percent)
        
        # 更新网络流量
        current_net_io = psutil.net_io_counters()
        current_time = time.time()
        
        # 计算时间差
        time_diff = current_time - self.last_net_time
        
        if time_diff > 0:
            # 计算下载和上传速度（字节/秒）
            down_speed = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / time_diff
            up_speed = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / time_diff
            
            # 更新显示
            self.down_label.setText(f"↓ {self.format_speed(down_speed)}")
            self.up_label.setText(f"↑ {self.format_speed(up_speed)}")
            
            # 更新缓存数据
            self.last_net_io = current_net_io
            self.last_net_time = current_time
    
    def format_speed(self, bytes_per_sec):
        """格式化网速显示"""
        if bytes_per_sec < 1024:
            return f"{bytes_per_sec:.0f} B/s"
        elif bytes_per_sec < 1024 * 1024:
            return f"{bytes_per_sec / 1024:.1f} KB/s"
        else:
            return f"{bytes_per_sec / (1024 * 1024):.1f} MB/s"
    
    def mousePressEvent(self, event):
        """鼠标按下事件，用于拖动窗口"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件，实现窗口拖动"""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPos() - self.drag_position)
            event.accept() 
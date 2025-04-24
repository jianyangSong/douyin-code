#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
备忘录功能模块
实现像素风格UI的备忘录功能，支持添加、查看和删除备忘录
"""

import os
import json
import time
from datetime import datetime
from PyQt5.QtCore import Qt, QSize, QRect, QPoint
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QFontDatabase
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTextEdit, QListWidget, QListWidgetItem, QLabel,
                            QSplitter, QScrollArea, QFrame)

class PixelButton(QPushButton):
    """像素风格按钮"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(30)
        self.setFont(QFont("Courier New", 10))
        self.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: white;
                border: 2px solid #666666;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #555555;
                border: 2px solid #888888;
            }
            QPushButton:pressed {
                background-color: #222222;
                border: 2px solid #444444;
            }
        """)

class MemoItemWidget(QWidget):
    """备忘录项目小部件"""
    
    def __init__(self, memo_data, parent=None):
        super().__init__(parent)
        self.memo_data = memo_data
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建时间标签
        time_label = QLabel(self.format_timestamp(self.memo_data["timestamp"]), self)
        time_label.setStyleSheet("color: #888888; font-size: 9px;")
        
        # 内容标签
        content_label = QLabel(self.memo_data["content"], self)
        content_label.setWordWrap(True)
        content_label.setStyleSheet("color: white; font-size: 12px;")
        
        # 添加到布局
        layout.addWidget(time_label)
        layout.addWidget(content_label)
        layout.addSpacing(10)
        
        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: #333333;
                border: 1px solid #666666;
                border-radius: 5px;
                padding: 5px;
            }
        """)
    
    def format_timestamp(self, timestamp):
        """格式化时间戳"""
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

class MemoWindow(QWidget):
    """备忘录窗口类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 窗口设置
        self.setWindowTitle("像素备忘录")
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        
        # 数据存储
        self.memos = []
        self.memo_file = "memos.json"
        
        # 加载备忘录数据
        self.load_memos()
        
        # 初始化UI
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 标题标签
        title_label = QLabel("像素备忘录", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Courier New", 16, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        main_layout.addWidget(title_label)
        
        # 输入区域
        input_layout = QVBoxLayout()
        
        # 文本编辑框
        self.text_edit = QTextEdit(self)
        self.text_edit.setFixedHeight(100)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #222222;
                color: white;
                border: 2px solid #666666;
                font-family: 'Courier New';
                font-size: 12px;
                padding: 5px;
            }
        """)
        input_layout.addWidget(self.text_edit)
        
        # 添加按钮
        add_button = PixelButton("添加备忘录", self)
        add_button.clicked.connect(self.add_memo)
        input_layout.addWidget(add_button)
        
        main_layout.addLayout(input_layout)
        
        # 备忘录列表区域
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #222222;
                border: 2px solid #666666;
            }
            QScrollBar:vertical {
                background-color: #222222;
                width: 15px;
                margin: 15px 0 15px 0;
            }
            QScrollBar::handle:vertical {
                background-color: #666666;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
            }
        """)
        
        # 备忘录容器
        self.memo_container = QWidget()
        self.memo_layout = QVBoxLayout(self.memo_container)
        self.memo_layout.setAlignment(Qt.AlignTop)
        self.memo_layout.setSpacing(10)
        self.memo_container.setLayout(self.memo_layout)
        
        scroll_area.setWidget(self.memo_container)
        main_layout.addWidget(scroll_area)
        
        # 显示备忘录
        self.update_memo_list()
        
        # 设置窗口样式
        self.setStyleSheet("""
            QWidget {
                background-color: #222222;
                color: white;
            }
        """)
    
    def load_memos(self):
        """从文件加载备忘录数据"""
        if os.path.exists(self.memo_file):
            try:
                with open(self.memo_file, "r", encoding="utf-8") as file:
                    self.memos = json.load(file)
            except (json.JSONDecodeError, IOError):
                self.memos = []
    
    def save_memos(self):
        """保存备忘录数据到文件"""
        try:
            with open(self.memo_file, "w", encoding="utf-8") as file:
                json.dump(self.memos, file, ensure_ascii=False, indent=2)
        except IOError:
            print("无法保存备忘录数据")
    
    def add_memo(self):
        """添加备忘录"""
        content = self.text_edit.toPlainText().strip()
        if content:
            # 创建备忘录数据
            memo = {
                "content": content,
                "timestamp": time.time()
            }
            
            # 添加到列表前端
            self.memos.insert(0, memo)
            
            # 保存备忘录
            self.save_memos()
            
            # 更新UI
            self.text_edit.clear()
            self.update_memo_list()
    
    def update_memo_list(self):
        """更新备忘录列表显示"""
        # 清空现有项目
        while self.memo_layout.count():
            item = self.memo_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加备忘录项目
        for memo in self.memos:
            memo_widget = MemoItemWidget(memo, self)
            
            # 创建包含备忘录和删除按钮的布局
            item_layout = QHBoxLayout()
            item_layout.addWidget(memo_widget, 1)
            
            # 删除按钮
            delete_button = QPushButton("×", self)
            delete_button.setFixedSize(30, 30)
            delete_button.setFont(QFont("Arial", 12, QFont.Bold))
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #aa3333;
                    color: white;
                    border: 1px solid #dd5555;
                    border-radius: 15px;
                }
                QPushButton:hover {
                    background-color: #cc3333;
                }
                QPushButton:pressed {
                    background-color: #882222;
                }
            """)
            
            # 连接删除信号
            delete_button.clicked.connect(lambda checked, m=memo: self.delete_memo(m))
            
            item_layout.addWidget(delete_button)
            
            # 将整个布局添加到备忘录布局中
            container = QWidget()
            container.setLayout(item_layout)
            self.memo_layout.addWidget(container)
    
    def delete_memo(self, memo):
        """删除备忘录"""
        self.memos.remove(memo)
        self.save_memos()
        self.update_memo_list()
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 关闭窗口时保存备忘录
        self.save_memos()
        event.accept() 
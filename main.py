#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
宇树Go2-W机器狗毕业设计主程序
功能：自主导航、目标识别、跟随、语音控制
"""

import time
import threading
from navigation.navigation import Navigation
from object_detection.detector import ObjectDetector
from follow.follower import Follower
from voice_control.voice_controller import VoiceController
from utils.robot_interface import RobotInterface

class Go2WController:
    def __init__(self):
        # 初始化机器人接口
        self.robot = RobotInterface()
        
        # 初始化各个功能模块
        self.navigation = Navigation(self.robot)
        self.detector = ObjectDetector()
        self.follower = Follower(self.robot, self.detector)
        self.voice_controller = VoiceController(self)
        
        # 系统状态
        self.running = False
        self.current_mode = "idle"
    
    def start(self):
        """启动系统"""
        print("启动宇树Go2-W机器狗系统...")
        self.running = True
        
        # 启动语音控制线程
        voice_thread = threading.Thread(target=self.voice_controller.listen)
        voice_thread.daemon = True
        voice_thread.start()
        
        # 启动主循环
        while self.running:
            try:
                if self.current_mode == "navigation":
                    self.navigation.update()
                elif self.current_mode == "follow":
                    self.follower.update()
                time.sleep(0.1)
            except Exception as e:
                print(f"错误: {e}")
                time.sleep(1)
    
    def stop(self):
        """停止系统"""
        print("停止宇树Go2-W机器狗系统...")
        self.running = False
        self.robot.stop()
    
    def set_mode(self, mode):
        """设置运行模式"""
        print(f"切换到模式: {mode}")
        self.current_mode = mode
    
    def navigate_to(self, target):
        """导航到目标位置"""
        self.set_mode("navigation")
        self.navigation.set_target(target)
    
    def start_following(self, target_type="person"):
        """开始跟随目标"""
        self.set_mode("follow")
        self.follower.set_target_type(target_type)
    
    def stop_following(self):
        """停止跟随"""
        self.set_mode("idle")
    
    def voice_command(self, command):
        """处理语音命令"""
        print(f"收到语音命令: {command}")
        
        if "导航" in command:
            # 提取目标位置
            target = command.replace("导航到", "").strip()
            self.navigate_to(target)
        elif "跟随" in command:
            self.start_following()
        elif "停止" in command and "跟随" in command:
            self.stop_following()
        elif "前进" in command:
            self.robot.move_forward(0.2)
        elif "后退" in command:
            self.robot.move_backward(0.2)
        elif "左转" in command:
            self.robot.turn_left(0.3)
        elif "右转" in command:
            self.robot.turn_right(0.3)
        elif "停止移动" in command:
            self.robot.stop()
        elif "站立" in command:
            self.robot.stand_up()
        elif "趴下" in command:
            self.robot.stand_down()
        elif "恢复" in command:
            self.robot.recovery()
        elif "速度等级" in command:
            # 提取速度等级
            import re
            match = re.search(r"速度等级(\d+)", command)
            if match:
                level = int(match.group(1))
                self.robot.set_speed_level(level)

if __name__ == "__main__":
    controller = Go2WController()
    try:
        controller.start()
    except KeyboardInterrupt:
        controller.stop()

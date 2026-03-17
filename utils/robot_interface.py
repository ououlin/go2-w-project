#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
机器人接口类
用于与宇树Go2-W机器狗进行通信
"""

import subprocess
import os

class RobotInterface:
    def __init__(self, network_interface="eth0"):
        """初始化机器人接口"""
        print("初始化机器人接口...")
        self.network_interface = network_interface
        self.speed = 0.0
        self.angular_speed = 0.0
        self.control_executable = os.path.join(os.path.dirname(__file__), "go2w_control")
    
    def _run_command(self, command, *args):
        """运行控制命令"""
        cmd = [self.control_executable, self.network_interface, command] + list(args)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            print(f"命令执行结果: {result.stdout.strip()}")
            return result.returncode == 0
        except Exception as e:
            print(f"命令执行错误: {e}")
            return False
    
    def move_forward(self, speed=0.2):
        """向前移动"""
        print(f"向前移动，速度: {speed}")
        self.speed = speed
        self.angular_speed = 0.0
        return self._run_command("move", str(speed), "0", "0")
    
    def move_backward(self, speed=0.2):
        """向后移动"""
        print(f"向后移动，速度: {speed}")
        self.speed = -speed
        self.angular_speed = 0.0
        return self._run_command("move", str(-speed), "0", "0")
    
    def turn_left(self, angular_speed=0.3):
        """向左转"""
        print(f"向左转，角速度: {angular_speed}")
        self.speed = 0.0
        self.angular_speed = angular_speed
        return self._run_command("move", "0", "0", str(angular_speed))
    
    def turn_right(self, angular_speed=0.3):
        """向右转"""
        print(f"向右转，角速度: {angular_speed}")
        self.speed = 0.0
        self.angular_speed = -angular_speed
        return self._run_command("move", "0", "0", str(-angular_speed))
    
    def stop(self):
        """停止移动"""
        print("停止移动")
        self.speed = 0.0
        self.angular_speed = 0.0
        return self._run_command("stop_move")
    
    def stand_up(self):
        """站立"""
        print("站立")
        return self._run_command("stand_up")
    
    def stand_down(self):
        """趴下"""
        print("趴下")
        return self._run_command("stand_down")
    
    def recovery(self):
        """恢复站立"""
        print("恢复站立")
        return self._run_command("recovery")
    
    def set_speed_level(self, level):
        """设置速度等级"""
        print(f"设置速度等级: {level}")
        return self._run_command("speed_level", str(level))
    
    def get_odometry(self):
        """获取里程计数据"""
        # 模拟返回里程计数据
        return {
            "x": 0.0,
            "y": 0.0,
            "theta": 0.0,
            "linear_velocity": self.speed,
            "angular_velocity": self.angular_speed
        }
    
    def get_lidar_data(self):
        """获取激光雷达数据"""
        # 模拟返回激光雷达数据
        return {
            "ranges": [1.0] * 360,  # 360度激光数据
            "angle_min": 0.0,
            "angle_max": 6.28,  # 2π
            "angle_increment": 0.01745,  # π/180
            "time_increment": 0.0,
            "scan_time": 0.1,
            "range_min": 0.05,
            "range_max": 10.0
        }
    
    def get_camera_image(self):
        """获取摄像头图像"""
        # 模拟返回摄像头图像
        return None  # 实际应用中返回图像数据

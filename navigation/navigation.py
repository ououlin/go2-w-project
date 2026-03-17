#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
导航模块
实现机器狗的自主导航功能
"""

import math
import time

class Navigation:
    def __init__(self, robot):
        """初始化导航模块"""
        print("初始化导航模块...")
        self.robot = robot
        self.target = None
        self.current_position = (0.0, 0.0, 0.0)  # (x, y, theta)
        
        # 导航参数
        self.goal_threshold = 0.1  # 到达目标的阈值
        self.angle_threshold = 0.05  # 角度阈值
        self.max_speed = 0.3  # 最大速度
        self.max_angular_speed = 0.5  # 最大角速度
    
    def set_target(self, target):
        """设置目标位置"""
        # 这里简化处理，实际应用中需要根据地图或环境确定目标坐标
        print(f"设置导航目标: {target}")
        # 模拟目标坐标
        if target == "客厅":
            self.target = (2.0, 3.0, 0.0)
        elif target == "卧室":
            self.target = (5.0, 2.0, 0.0)
        elif target == "厨房":
            self.target = (1.0, 5.0, 0.0)
        else:
            # 默认目标
            self.target = (3.0, 3.0, 0.0)
    
    def update(self):
        """更新导航状态"""
        if self.target is None:
            return
        
        # 获取当前位置
        odom = self.robot.get_odometry()
        self.current_position = (odom["x"], odom["y"], odom["theta"])
        
        # 计算到目标的距离和角度
        dx = self.target[0] - self.current_position[0]
        dy = self.target[1] - self.current_position[1]
        distance = math.sqrt(dx**2 + dy**2)
        target_angle = math.atan2(dy, dx)
        angle_error = target_angle - self.current_position[2]
        
        # 调整角度误差到[-pi, pi]
        angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))
        
        # 检查是否到达目标
        if distance < self.goal_threshold:
            print("到达目标位置")
            self.robot.stop()
            self.target = None
            return
        
        # 避障处理
        if self.check_obstacle():
            print("检测到障碍物，进行避障")
            self.avoid_obstacle()
            return
        
        # 控制逻辑
        if abs(angle_error) > self.angle_threshold:
            # 先转向
            angular_speed = min(self.max_angular_speed, max(-self.max_angular_speed, angle_error * 0.5))
            if angular_speed > 0:
                self.robot.turn_left(abs(angular_speed))
            else:
                self.robot.turn_right(abs(angular_speed))
        else:
            # 前进
            linear_speed = min(self.max_speed, distance * 0.5)
            self.robot.move_forward(linear_speed)
    
    def check_obstacle(self):
        """检查是否有障碍物"""
        lidar_data = self.robot.get_lidar_data()
        # 检查前方是否有障碍物
        front_ranges = lidar_data["ranges"][0:30] + lidar_data["ranges"][330:360]
        min_distance = min(front_ranges)
        return min_distance < 0.5  # 距离小于0.5米认为有障碍物
    
    def avoid_obstacle(self):
        """避障处理"""
        # 简单的避障策略：向右侧移动
        self.robot.turn_right(0.3)
        time.sleep(1.0)
        self.robot.move_forward(0.2)
        time.sleep(1.0)
        self.robot.turn_left(0.3)
        time.sleep(1.0)

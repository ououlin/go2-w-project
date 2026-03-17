#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
跟随模块
实现机器狗跟随目标的功能
"""

import cv2
import time

class Follower:
    def __init__(self, robot, detector):
        """初始化跟随器"""
        print("初始化跟随器...")
        self.robot = robot
        self.detector = detector
        self.target_type = "person"
        self.target_id = None
        self.camera = None
        
        # 跟随参数
        self.follow_distance = 1.0  # 跟随距离
        self.max_speed = 0.3  # 最大速度
        self.max_angular_speed = 0.5  # 最大角速度
        self.image_width = 640  # 图像宽度
        self.image_height = 480  # 图像高度
        self.center_x = self.image_width // 2  # 图像中心x坐标
    
    def set_target_type(self, target_type):
        """设置目标类型"""
        self.target_type = target_type
        print(f"设置跟随目标类型: {target_type}")
    
    def start_camera(self):
        """启动摄像头"""
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            print("启动摄像头...")
    
    def stop_camera(self):
        """停止摄像头"""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            print("停止摄像头...")
    
    def update(self):
        """更新跟随状态"""
        # 启动摄像头
        self.start_camera()
        
        # 获取图像并检测目标
        detections, frame = self.detector.detect_from_camera(self.camera)
        
        if detections and frame is not None:
            # 过滤目标类型
            target_detections = [d for d in detections if d["class"] == self.target_type]
            
            if target_detections:
                # 选择最近的目标
                target = max(target_detections, key=lambda x: (x["bbox"][2] - x["bbox"][0]) * (x["bbox"][3] - x["bbox"][1]))
                
                # 计算目标中心
                x1, y1, x2, y2 = target["bbox"]
                target_center_x = (x1 + x2) // 2
                target_center_y = (y1 + y2) // 2
                
                # 计算目标大小（面积）
                target_area = (x2 - x1) * (y2 - y1)
                
                # 计算偏差
                x_error = target_center_x - self.center_x
                
                # 计算速度和角速度
                linear_speed = self.calculate_linear_speed(target_area)
                angular_speed = self.calculate_angular_speed(x_error)
                
                # 控制机器人
                if abs(angular_speed) > 0.1:
                    # 先转向
                    if angular_speed > 0:
                        self.robot.turn_left(abs(angular_speed))
                    else:
                        self.robot.turn_right(abs(angular_speed))
                else:
                    # 前进或后退
                    if linear_speed > 0:
                        self.robot.move_forward(linear_speed)
                    elif linear_speed < 0:
                        self.robot.move_backward(abs(linear_speed))
                    else:
                        self.robot.stop()
                
                # 可视化
                frame = self.detector.visualize(frame, detections)
                cv2.circle(frame, (target_center_x, target_center_y), 5, (0, 0, 255), -1)
                cv2.imshow("Follow Mode", frame)
                cv2.waitKey(1)
            else:
                # 没有检测到目标，停止移动
                self.robot.stop()
        else:
            # 没有图像，停止移动
            self.robot.stop()
    
    def calculate_linear_speed(self, target_area):
        """计算线速度"""
        # 目标面积与距离成反比
        # 假设目标在合适距离时的面积为30000
        target_area_desired = 30000
        
        if target_area > target_area_desired * 1.2:
            # 目标太近，后退
            return -min(self.max_speed, (target_area - target_area_desired) / 100000)
        elif target_area < target_area_desired * 0.8:
            # 目标太远，前进
            return min(self.max_speed, (target_area_desired - target_area) / 100000)
        else:
            # 距离合适，停止
            return 0.0
    
    def calculate_angular_speed(self, x_error):
        """计算角速度"""
        # 比例控制
        kp = 0.001
        angular_speed = kp * x_error
        return max(-self.max_angular_speed, min(self.max_angular_speed, angular_speed))

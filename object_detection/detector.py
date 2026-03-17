#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
目标检测模块
使用Ultralytics YOLO库实现目标识别
"""

from ultralytics import YOLO
import cv2

class ObjectDetector:
    def __init__(self, model_path="yolov26n.pt"):
        """初始化目标检测器"""
        print("初始化目标检测器...")
        # 加载YOLOv26模型
        self.model = YOLO(model_path)
        # 目标类别
        self.class_names = self.model.names
    
    def detect(self, image):
        """检测图像中的目标"""
        if image is None:
            return []
        
        # 运行目标检测
        results = self.model(image)
        
        # 处理检测结果
        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = box.conf[0].item()
                class_id = box.cls[0].item()
                class_name = self.class_names[int(class_id)]
                
                detections.append({
                    "class": class_name,
                    "confidence": confidence,
                    "bbox": [x1, y1, x2, y2]
                })
        
        return detections
    
    def detect_from_camera(self, camera):
        """从摄像头检测目标"""
        ret, frame = camera.read()
        if not ret:
            return [], None
        
        detections = self.detect(frame)
        return detections, frame
    
    def visualize(self, image, detections):
        """可视化检测结果"""
        if image is None:
            return None
        
        # 绘制检测框
        for detection in detections:
            x1, y1, x2, y2 = detection["bbox"]
            class_name = detection["class"]
            confidence = detection["confidence"]
            
            # 绘制矩形框
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            
            # 绘制标签
            label = f"{class_name}: {confidence:.2f}"
            cv2.putText(image, label, (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return image

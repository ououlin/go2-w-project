#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Socket服务器
用于与Node.js后端进行通信
"""

import socket
import json
import threading
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import Go2WController

class RobotSocketServer:
    def __init__(self, host='127.0.0.1', port=9999):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.robot_controller = None
        self.client_socket = None
        
    def start(self):
        """启动socket服务器"""
        print("初始化机器人控制器...")
        self.robot_controller = Go2WController()
        
        print(f"启动Socket服务器: {self.host}:{self.port}")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.running = True
        
        # 在单独线程中运行机器人主循环
        robot_thread = threading.Thread(target=self.robot_controller.start, daemon=True)
        robot_thread.start()
        
        while self.running:
            try:
                print("等待连接...")
                self.client_socket, addr = self.server_socket.accept()
                print(f"已连接: {addr}")
                
                client_thread = threading.Thread(target=self.handle_client, args=(self.client_socket,))
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                if self.running:
                    print(f"接受连接错误: {e}")
    
    def handle_client(self, client_socket):
        """处理客户端连接"""
        buffer = ""
        while self.running:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                buffer += data.decode('utf-8')
                
                # 处理完整的JSON消息
                while '\n' in buffer:
                    message_str, buffer = buffer.split('\n', 1)
                    if message_str.strip():
                        self.process_message(client_socket, message_str)
                        
            except Exception as e:
                print(f"处理客户端错误: {e}")
                break
        
        print("客户端断开连接")
        client_socket.close()
    
    def process_message(self, client_socket, message_str):
        """处理接收到的消息"""
        try:
            message = json.loads(message_str)
            command = message.get('command')
            message_id = message.get('id')
            
            print(f"收到命令: {command}, ID: {message_id}")
            
            response = {'success': False}
            if message_id is not None:
                response['id'] = message_id
            
            if command == 'get_status':
                odom = self.robot_controller.robot.get_odometry()
                response = {
                    'success': True,
                    'status': 'running',
                    'mode': self.robot_controller.current_mode,
                    'position': {
                        'x': odom['x'],
                        'y': odom['y'],
                        'theta': odom['theta']
                    },
                    'velocity': {
                        'linear': odom['linear_velocity'],
                        'angular': odom['angular_velocity']
                    }
                }
                if message_id is not None:
                    response['id'] = message_id
            
            elif command == 'forward':
                speed = message.get('speed', 0.2)
                self.robot_controller.robot.move_forward(speed)
                response['success'] = True
            
            elif command == 'backward':
                speed = message.get('speed', 0.2)
                self.robot_controller.robot.move_backward(speed)
                response['success'] = True
            
            elif command == 'left':
                speed = message.get('speed', 0.3)
                self.robot_controller.robot.turn_left(speed)
                response['success'] = True
            
            elif command == 'right':
                speed = message.get('speed', 0.3)
                self.robot_controller.robot.turn_right(speed)
                response['success'] = True
            
            elif command == 'stop':
                self.robot_controller.robot.stop()
                response['success'] = True
            
            elif command == 'stand_up':
                self.robot_controller.robot.stand_up()
                response['success'] = True
            
            elif command == 'stand_down':
                self.robot_controller.robot.stand_down()
                response['success'] = True
            
            elif command == 'recovery':
                self.robot_controller.robot.recovery()
                response['success'] = True
            
            elif command == 'set_speed_level':
                level = message.get('level', 1)
                self.robot_controller.robot.set_speed_level(level)
                response['success'] = True
            
            elif command == 'follow':
                self.robot_controller.start_following()
                response['success'] = True
            
            elif command == 'stop_follow':
                self.robot_controller.stop_following()
                response['success'] = True
            
            elif command == 'navigate':
                target = message.get('target', '')
                self.robot_controller.navigate_to(target)
                response['success'] = True
            
            elif command == 'get_camera_frame':
                # 获取摄像头图像
                frame = self.robot_controller.robot.get_camera_image()
                if frame is not None:
                    response['success'] = True
                    # 这里需要将图像转换为base64编码
                    # 暂时返回成功
                else:
                    response['error'] = 'Camera not available'
            
            else:
                response['error'] = 'Unknown command'
            
            # 发送响应
            self.send_response(client_socket, response)
            
        except Exception as e:
            print(f"处理消息错误: {e}")
            error_response = {'success': False, 'error': str(e)}
            try:
                message = json.loads(message_str)
                message_id = message.get('id')
                if message_id is not None:
                    error_response['id'] = message_id
            except:
                pass
            self.send_response(client_socket, error_response)
    
    def send_response(self, client_socket, response):
        """发送响应到客户端"""
        try:
            response_str = json.dumps(response) + '\n'
            client_socket.send(response_str.encode('utf-8'))
        except Exception as e:
            print(f"发送响应错误: {e}")
    
    def stop(self):
        """停止服务器"""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        if self.robot_controller:
            self.robot_controller.stop()

if __name__ == '__main__':
    server = RobotSocketServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        server.stop()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语音控制模块
实现机器狗的语音控制功能
"""

import speech_recognition as sr
import threading

class VoiceController:
    def __init__(self, controller):
        """初始化语音控制器"""
        print("初始化语音控制器...")
        self.controller = controller
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.running = False
    
    def listen(self):
        """监听语音命令"""
        self.running = True
        print("开始监听语音命令...")
        
        while self.running:
            try:
                with self.microphone as source:
                    # 调整噪音水平
                    self.recognizer.adjust_for_ambient_noise(source)
                    print("请说出命令...")
                    
                    # 监听语音
                    audio = self.recognizer.listen(source, timeout=5)
                    
                    # 识别语音
                    try:
                        # 使用Google语音识别
                        command = self.recognizer.recognize_google(audio, language="zh-CN")
                        print(f"识别到命令: {command}")
                        
                        # 处理命令
                        self.controller.voice_command(command)
                    except sr.UnknownValueError:
                        print("无法识别语音")
                    except sr.RequestError as e:
                        print(f"语音识别服务错误: {e}")
            except Exception as e:
                print(f"监听错误: {e}")
    
    def stop(self):
        """停止语音监听"""
        self.running = False
        print("停止语音监听...")

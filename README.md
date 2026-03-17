# 宇树Go2-W机器狗毕业设计

## 项目概述
本项目基于宇树Go2-W轮足机器狗，实现了以下功能：
- 自主导航：能够在环境中自主移动，避开障碍物
- 目标识别：使用YOLOv26模型识别目标物体
- 跟随功能：能够跟随指定目标（如人员）移动
- 语音控制：通过语音指令控制机器狗的行为
- Web控制：通过Web界面远程控制机器狗

## 项目结构
```
go2-w-project/
├── main.py                    # 主程序（语音控制）
├── backend/
│   ├── app.js                # Node.js + Express后端
│   └── package.json          # Node.js依赖配置
├── frontend/
│   ├── index.html             # Web前端界面
│   ├── css/
│   │   └── style.css         # 样式文件
│   └── js/
│       └── app.js            # 前端逻辑
├── navigation/                # 导航模块
│   └── navigation.py          # 导航实现
├── object_detection/          # 目标检测模块
│   └── detector.py            # 目标检测实现
├── follow/                    # 跟随模块
│   └── follower.py            # 跟随实现
├── voice_control/             # 语音控制模块
│   └── voice_controller.py    # 语音控制实现
├── utils/                     # 工具模块
│   ├── robot_interface.py     # 机器人接口
│   ├── socket_server.py        # Python Socket服务器
│   ├── go2w_control.cpp       # C++控制程序
│   └── CMakeLists.txt        # C++编译配置
├── requirements.txt           # Python依赖项
└── README.md                 # 项目文档
```

## 技术栈
- Python 3.8+
- Ultralytics YOLOv26 (目标检测)
- OpenCV (图像处理)
- SpeechRecognition (语音识别)
- NumPy (数值计算)
- C++ (SDK集成)
- CMake (编译工具)
- Node.js + Express (Web后端框架)
- HTML/CSS/JavaScript (前端界面)

## 安装依赖

### Python依赖
```bash
pip install -r requirements.txt
```

### Node.js依赖
```bash
cd go2-w-project/backend
npm install
```

## SDK集成步骤
1. 确保已安装SDK依赖：
   ```bash
   apt-get update
   apt-get install -y cmake g++ build-essential libyaml-cpp-dev libeigen3-dev libboost-all-dev libspdlog-dev libfmt-dev
   ```

2. 安装unitree_sdk2：
   ```bash
   cd unitree_sdk2-main/unitree_sdk2-main
   mkdir build
   cd build
   cmake ..
   sudo make install
   ```

3. 编译C++控制程序：
   ```bash
   cd go2-w-project/utils
   mkdir build
   cd build
   cmake ..
   make
   ```

4. 修改network_interface参数：
   在`main.py`中，根据实际网络接口修改RobotInterface的初始化参数

## Web控制平台

### 启动Web服务
1. 确保已安装Python和Node.js依赖
2. 启动Node.js后端：
   ```bash
   cd go2-w-project/backend
   npm start
   ```

3. 在浏览器中访问：
   ```
   http://服务器IP:5000
   ```

### Web界面功能
- **运动控制**：使用方向键或WASD控制机器狗移动
- **机器人动作**：站立、趴下、恢复站立、设置速度等级
- **自动化功能**：跟随模式、导航到指定目标
- **状态显示**：实时显示机器狗的位置、速度、角度等信息
- **键盘快捷键**：
  - W/↑：前进
  - S/↓：后退
  - A/←：左转
  - D/→：右转
  - 空格键：停止

### 云服务器部署
1. 将项目上传到云服务器
2. 在云服务器上安装所有Python和Node.js依赖
3. 确保防火墙开放5000端口
4. 配置域名解析到云服务器IP
5. 使用Nginx反向代理Node.js应用（推荐）
   ```nginx
   server {
       listen 80;
       server_name 你的域名;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 控制命令

### 语音命令
- "导航到客厅" - 导航到客厅
- "导航到卧室" - 导航到卧室
- "导航到厨房" - 导航到厨房
- "跟随我" - 开始跟随模式
- "停止跟随" - 停止跟随模式
- "前进" - 向前移动
- "后退" - 向后移动
- "左转" - 向左转
- "右转" - 向右转
- "停止移动" - 停止移动
- "站立" - 机器狗站立
- "趴下" - 机器狗趴下
- "恢复" - 机器狗恢复站立

### Web界面按钮
所有语音命令都可以通过Web界面按钮执行

## 注意事项
1. 本项目集成了宇树Go2-W机器狗的官方SDK
2. 语音控制需要麦克风权限
3. 目标检测需要摄像头权限
4. 导航功能需要激光雷达数据
5. 需要在Ubuntu 20.04环境下编译和运行C++控制程序
6. Web控制需要Node.js环境
7. Node.js后端通过TCP socket与Python服务器通信

## 架构说明
- **前端**：HTML/CSS/JavaScript，运行在用户浏览器
- **后端**：Node.js + Express，处理API请求
- **Python服务器**：通过TCP socket接收命令，控制机器狗
- **机器人控制**：通过SDK调用控制Go2-W机器狗
- **云服务器**：托管整个系统，提供公网访问

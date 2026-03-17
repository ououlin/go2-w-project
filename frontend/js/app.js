const API_BASE_URL = '';
let isConnected = false;
let statusUpdateInterval = null;
let isInitialized = false;

// 语音控制相关变量
let recognition = null;
let isRecording = false;
const voiceBtn = document.getElementById('startVoiceBtn');
const voiceStatus = document.getElementById('voiceStatus');

const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');
const modeValue = document.getElementById('modeValue');
const xValue = document.getElementById('xValue');
const yValue = document.getElementById('yValue');
const thetaValue = document.getElementById('thetaValue');
const linearValue = document.getElementById('linearValue');
const angularValue = document.getElementById('angularValue');

const initBtn = document.getElementById('initBtn');
const forwardBtn = document.getElementById('forwardBtn');
const backwardBtn = document.getElementById('backwardBtn');
const leftBtn = document.getElementById('leftBtn');
const rightBtn = document.getElementById('rightBtn');
const stopBtn = document.getElementById('stopBtn');
const standUpBtn = document.getElementById('standUpBtn');
const standDownBtn = document.getElementById('standDownBtn');
const recoveryBtn = document.getElementById('recoveryBtn');
const setSpeedBtn = document.getElementById('setSpeedBtn');
const followBtn = document.getElementById('followBtn');
const stopFollowBtn = document.getElementById('stopFollowBtn');
const navigateBtn = document.getElementById('navigateBtn');
const startCameraBtn = document.getElementById('startCameraBtn');
const stopCameraBtn = document.getElementById('stopCameraBtn');
const cameraVideo = document.getElementById('cameraVideo');
const speedLevel = document.getElementById('speedLevel');
const navTarget = document.getElementById('navTarget');

let videoStream = null;

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: 12px;
        color: white;
        font-weight: 600;
        z-index: 1000;
        box-shadow: var(--shadow-lg);
        transform: translateX(400px);
        transition: transform 0.3s ease;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    `;
    
    if (type === 'success') {
        notification.style.background = 'linear-gradient(135deg, var(--success-color), #059669)';
    } else if (type === 'error') {
        notification.style.background = 'linear-gradient(135deg, var(--danger-color), #dc2626)';
    } else if (type === 'warning') {
        notification.style.background = 'linear-gradient(135deg, var(--warning-color), #d97706)';
    } else {
        notification.style.background = 'linear-gradient(135deg, var(--primary-color), var(--primary-dark))';
    }
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

function addButtonFeedback(button) {
    button.addEventListener('click', function() {
        this.style.transform = 'scale(0.95)';
        setTimeout(() => {
            this.style.transform = '';
        }, 100);
    });
}

async function sendControlCommand(command, data = {}) {
    if (!isInitialized && command !== 'init_robot') {
        showNotification('请先初始化机器人！', 'warning');
        return { error: '未初始化' };
    }
    
    try {
        const button = document.querySelector(`button[onclick*="${command}"]`) || 
                      document.getElementById(command + 'Btn');
        
        if (button) {
            button.style.transform = 'scale(0.95)';
            setTimeout(() => button.style.transform = '', 100);
        }
        
        const response = await fetch(`${API_BASE_URL}/api/control`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command, ...data }),
        });
        const result = await response.json();
        if (result.success) {
            showNotification(`✅ 命令执行成功: ${command}`, 'success');
        } else {
            showNotification(`❌ 命令执行失败: ${result.error}`, 'error');
        }
        return result;
    } catch (error) {
        console.error('发送命令时出错:', error);
        showNotification('网络错误，请检查连接', 'error');
        return { error: '网络错误' };
    }
}

async function getStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/status`);
        if (response.ok) {
            const data = await response.json();
            updateStatusDisplay(data);
            if (!isConnected) {
                setConnected(true);
            }
            return data;
        } else {
            setConnected(false);
            return null;
        }
    } catch (error) {
        console.error('获取状态时出错:', error);
        setConnected(false);
        return null;
    }
}

function updateStatusDisplay(data) {
    if (!data) return;
    
    const modeMap = {
        'idle': '⚡ 待机',
        'navigation': '🧭 导航中',
        'follow': '👣 跟随中',
        'moving': '🏃 移动中',
        'standing': '🦮 站立'
    };
    
    modeValue.textContent = modeMap[data.mode] || data.mode;
    xValue.textContent = data.position.x.toFixed(2);
    yValue.textContent = data.position.y.toFixed(2);
    thetaValue.textContent = (data.position.theta * 180 / Math.PI).toFixed(1);
    linearValue.textContent = data.velocity.linear.toFixed(2);
    angularValue.textContent = (data.velocity.angular * 180 / Math.PI).toFixed(1);
    
    const statusItems = document.querySelectorAll('.status-item');
    statusItems.forEach((item, index) => {
        setTimeout(() => {
            item.style.animation = 'pulseGlow 0.5s ease';
            setTimeout(() => {
                item.style.animation = '';
            }, 500);
        }, index * 50);
    });
}

function setConnected(connected) {
    isConnected = connected;
    if (connected) {
        statusIndicator.classList.remove('disconnected');
        statusIndicator.classList.add('connected');
        statusText.textContent = '已连接';
    } else {
        statusIndicator.classList.remove('connected');
        statusIndicator.classList.add('disconnected');
        statusText.textContent = '未连接';
    }
}

async function initRobot() {
    if (isInitialized) {
        showNotification('机器人已经初始化！', 'info');
        return;
    }
    
    initBtn.disabled = true;
    initBtn.innerHTML = '🔄 初始化中<span class="loading-spinner"></span>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/init`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        const result = await response.json();
        if (result.success) {
            isInitialized = true;
            showNotification('🎉 机器人初始化成功！', 'success');
            startStatusUpdates();
            initBtn.innerHTML = '✅ 已初始化';
            initBtn.style.background = 'linear-gradient(135deg, var(--success-color), #059669)';
            document.querySelectorAll('.control-btn, .action-btn, .auto-btn').forEach(btn => {
                btn.style.opacity = '1';
            });
        } else {
            showNotification('初始化失败: ' + result.error, 'error');
            initBtn.disabled = false;
            initBtn.innerHTML = '🔄 初始化机器人';
        }
    } catch (error) {
        console.error('初始化机器人时出错:', error);
        showNotification('初始化失败: 网络错误', 'error');
        initBtn.disabled = false;
        initBtn.innerHTML = '🔄 初始化机器人';
    }
}

function startStatusUpdates() {
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
    }
    statusUpdateInterval = setInterval(getStatus, 500);
}

function stopStatusUpdates() {
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
        statusUpdateInterval = null;
    }
}

// Add button feedback to all buttons
document.querySelectorAll('.control-btn, .action-btn, .auto-btn').forEach(btn => {
    addButtonFeedback(btn);
});

initBtn.addEventListener('click', initRobot);
forwardBtn.addEventListener('click', () => sendControlCommand('forward'));
backwardBtn.addEventListener('click', () => sendControlCommand('backward'));
leftBtn.addEventListener('click', () => sendControlCommand('left'));
rightBtn.addEventListener('click', () => sendControlCommand('right'));
stopBtn.addEventListener('click', () => sendControlCommand('stop'));
standUpBtn.addEventListener('click', () => sendControlCommand('stand_up'));
standDownBtn.addEventListener('click', () => sendControlCommand('stand_down'));
recoveryBtn.addEventListener('click', () => sendControlCommand('recovery'));
setSpeedBtn.addEventListener('click', () => {
    sendControlCommand('set_speed_level', { level: parseInt(speedLevel.value) });
});
followBtn.addEventListener('click', () => sendControlCommand('follow'));
stopFollowBtn.addEventListener('click', () => sendControlCommand('stop_follow'));
navigateBtn.addEventListener('click', () => {
    sendControlCommand('navigate', { target: navTarget.value });
});

async function startCamera() {
    startCameraBtn.disabled = true;
    startCameraBtn.innerHTML = '📹 启动中<span class="loading-spinner"></span>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/camera/start`);
        if (response.ok) {
            const videoUrl = `${API_BASE_URL}/api/camera/stream`;
            cameraVideo.src = videoUrl;
            videoStream = true;
            showNotification('📹 摄像头已启动', 'success');
            startCameraBtn.innerHTML = '📹 摄像头运行中';
            startCameraBtn.style.background = 'linear-gradient(135deg, var(--success-color), #059669)';
            startCameraBtn.style.boxShadow = '0 0 15px rgba(16, 185, 129, 0.4)';
        } else {
            showNotification('启动摄像头失败', 'error');
            startCameraBtn.disabled = false;
            startCameraBtn.innerHTML = '📹 开始摄像头';
        }
    } catch (error) {
        console.error('获取摄像头失败:', error);
        showNotification('获取摄像头失败，尝试访问本地摄像头', 'warning');
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            cameraVideo.srcObject = stream;
            videoStream = stream;
            showNotification('正在使用本地摄像头', 'info');
            startCameraBtn.innerHTML = '📹 本地摄像头运行中';
            startCameraBtn.style.background = 'linear-gradient(135deg, var(--warning-color), #d97706)';
            startCameraBtn.style.boxShadow = '0 0 15px rgba(245, 158, 11, 0.4)';
        } catch (err) {
            console.error('无法访问摄像头:', err);
            showNotification('无法访问任何摄像头', 'error');
            startCameraBtn.disabled = false;
            startCameraBtn.innerHTML = '📹 开始摄像头';
        }
    }
}

function stopCamera() {
    if (videoStream) {
        if (typeof videoStream === 'object') {
            videoStream.getTracks().forEach(track => track.stop());
        }
        cameraVideo.src = '';
        videoStream = null;
        showNotification('摄像头已停止', 'info');
        
        startCameraBtn.disabled = false;
        startCameraBtn.innerHTML = '📹 开始摄像头';
        startCameraBtn.style.background = '';
        startCameraBtn.style.boxShadow = '';
    }
}

startCameraBtn.addEventListener('click', startCamera);
stopCameraBtn.addEventListener('click', stopCamera);

document.addEventListener('keydown', (e) => {
    if (!isInitialized) return;
    
    switch (e.key) {
        case 'ArrowUp':
        case 'w':
        case 'W':
            e.preventDefault();
            forwardBtn.style.transform = 'scale(0.9)';
            setTimeout(() => forwardBtn.style.transform = '', 100);
            sendControlCommand('forward');
            break;
        case 'ArrowDown':
        case 's':
        case 'S':
            e.preventDefault();
            backwardBtn.style.transform = 'scale(0.9)';
            setTimeout(() => backwardBtn.style.transform = '', 100);
            sendControlCommand('backward');
            break;
        case 'ArrowLeft':
        case 'a':
        case 'A':
            e.preventDefault();
            leftBtn.style.transform = 'scale(0.9)';
            setTimeout(() => leftBtn.style.transform = '', 100);
            sendControlCommand('left');
            break;
        case 'ArrowRight':
        case 'd':
        case 'D':
            e.preventDefault();
            rightBtn.style.transform = 'scale(0.9)';
            setTimeout(() => rightBtn.style.transform = '', 100);
            sendControlCommand('right');
            break;
        case ' ':
            e.preventDefault();
            stopBtn.style.transform = 'scale(0.9)';
            setTimeout(() => stopBtn.style.transform = '', 100);
            sendControlCommand('stop');
            break;
    }
});

// Page load animation
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.fade-in').forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        setTimeout(() => {
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    showNotification('🎮 欢迎使用Go2-W控制平台！请先初始化机器人', 'info');
});

// Disable buttons initially
document.querySelectorAll('.control-btn, .action-btn, .auto-btn').forEach(btn => {
    if (btn.id !== 'initBtn') {
        btn.style.opacity = '0.7';
    }
});

startStatusUpdates();

// 初始化语音识别
function initVoiceRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'zh-CN';
        recognition.continuous = false;
        recognition.interimResults = false;
        
        recognition.onstart = function() {
            isRecording = true;
            voiceBtn.classList.add('recording');
            voiceStatus.textContent = '🎤 正在聆听...';
        };
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            voiceStatus.textContent = `📝 识别结果: ${transcript}`;
            processVoiceCommand(transcript);
        };
        
        recognition.onerror = function(event) {
            console.error('语音识别错误:', event.error);
            voiceStatus.textContent = '❌ 识别失败，请重试';
            stopVoiceRecognition();
        };
        
        recognition.onend = function() {
            stopVoiceRecognition();
        };
    } else {
        voiceStatus.textContent = '❌ 您的浏览器不支持语音识别';
        voiceBtn.disabled = true;
        voiceBtn.style.opacity = '0.5';
    }
}

// 开始语音识别
function startVoiceRecognition() {
    if (!isInitialized) {
        showNotification('请先初始化机器人！', 'warning');
        return;
    }
    
    if (recognition && !isRecording) {
        try {
            recognition.start();
        } catch (error) {
            console.error('启动语音识别失败:', error);
            voiceStatus.textContent = '❌ 启动失败，请重试';
        }
    }
}

// 停止语音识别
function stopVoiceRecognition() {
    if (recognition && isRecording) {
        recognition.stop();
    }
    isRecording = false;
    voiceBtn.classList.remove('recording');
}

// 处理语音命令
function processVoiceCommand(command) {
    console.log('处理语音命令:', command);
    
    const lowerCommand = command.toLowerCase();
    
    // 导航命令
    if (lowerCommand.includes('导航到客厅')) {
        sendControlCommand('navigate', { target: '客厅' });
    } else if (lowerCommand.includes('导航到卧室')) {
        sendControlCommand('navigate', { target: '卧室' });
    } else if (lowerCommand.includes('导航到厨房')) {
        sendControlCommand('navigate', { target: '厨房' });
    }
    
    // 跟随命令
    else if (lowerCommand.includes('跟随我')) {
        sendControlCommand('follow');
    } else if (lowerCommand.includes('停止跟随')) {
        sendControlCommand('stop_follow');
    }
    
    // 移动命令
    else if (lowerCommand.includes('前进')) {
        sendControlCommand('forward');
    } else if (lowerCommand.includes('后退')) {
        sendControlCommand('backward');
    } else if (lowerCommand.includes('左转')) {
        sendControlCommand('left');
    } else if (lowerCommand.includes('右转')) {
        sendControlCommand('right');
    } else if (lowerCommand.includes('停止移动') || lowerCommand.includes('停下来')) {
        sendControlCommand('stop');
    }
    
    // 动作命令
    else if (lowerCommand.includes('站立')) {
        sendControlCommand('stand_up');
    } else if (lowerCommand.includes('趴下')) {
        sendControlCommand('stand_down');
    } else if (lowerCommand.includes('恢复')) {
        sendControlCommand('recovery');
    }
    
    // 速度命令
    else if (lowerCommand.includes('设置速度等级1') || lowerCommand.includes('速度1')) {
        sendControlCommand('set_speed_level', { level: 1 });
    } else if (lowerCommand.includes('设置速度等级2') || lowerCommand.includes('速度2')) {
        sendControlCommand('set_speed_level', { level: 2 });
    } else if (lowerCommand.includes('设置速度等级3') || lowerCommand.includes('速度3')) {
        sendControlCommand('set_speed_level', { level: 3 });
    }
    
    // 摄像头命令
    else if (lowerCommand.includes('打开摄像头') || lowerCommand.includes('开始摄像头')) {
        startCamera();
    } else if (lowerCommand.includes('关闭摄像头') || lowerCommand.includes('停止摄像头')) {
        stopCamera();
    }
    
    // 初始化命令
    else if (lowerCommand.includes('初始化')) {
        initRobot();
    }
    
    else {
        showNotification(`🤔 未识别的命令: ${command}`, 'warning');
    }
}

// 语音按钮事件监听
if (voiceBtn) {
    voiceBtn.addEventListener('mousedown', startVoiceRecognition);
    voiceBtn.addEventListener('mouseup', stopVoiceRecognition);
    voiceBtn.addEventListener('mouseleave', stopVoiceRecognition);
    
    // 触摸设备支持
    voiceBtn.addEventListener('touchstart', startVoiceRecognition, { passive: true });
    voiceBtn.addEventListener('touchend', stopVoiceRecognition, { passive: true });
}

// 页面加载时初始化语音识别
document.addEventListener('DOMContentLoaded', function() {
    initVoiceRecognition();
});

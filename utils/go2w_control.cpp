#include <iostream>
#include <string>
#include <chrono>
#include <thread>
#include <unitree/robot/go2/sport/sport_client.hpp>

using namespace std;

int main(int argc, char **argv) {
    // 初始化 dds
    if (argc < 3) {
        std::cout << "Usage: " << argv[0] << " networkInterface command [params]" << std::endl;
        return -1;
    }
    
    std::string networkInterface = argv[1];
    std::string command = argv[2];
    
    unitree::robot::ChannelFactory::Instance()->Init(0, networkInterface.c_str());
    
    // 初始化sportclient
    unitree::robot::go2::SportClient sport_client;
    sport_client.SetTimeout(20.0f);
    sport_client.Init();
    
    int res = 1;
    
    if (command == "stand_up") {
        res = sport_client.StandUp();
    } else if (command == "stand_down") {
        res = sport_client.StandDown();
    } else if (command == "move") {
        if (argc >= 6) {
            float vx = std::stof(argv[3]);
            float vy = std::stof(argv[4]);
            float vw = std::stof(argv[5]);
            res = sport_client.Move(vx, vy, vw);
        } else {
            std::cout << "Error: move command requires 3 parameters: vx vy vw" << std::endl;
            return -1;
        }
    } else if (command == "stop_move") {
        res = sport_client.StopMove();
    } else if (command == "damp") {
        res = sport_client.Damp();
    } else if (command == "recovery") {
        res = sport_client.RecoveryStand();
    } else if (command == "balance") {
        res = sport_client.BalanceStand();
    } else if (command == "speed_level") {
        if (argc >= 4) {
            int level = std::stoi(argv[3]);
            res = sport_client.SpeedLevel(level);
        } else {
            std::cout << "Error: speed_level command requires 1 parameter: level" << std::endl;
            return -1;
        }
    } else {
        std::cout << "Error: unknown command" << std::endl;
        return -1;
    }
    
    std::cout << "Command: " << command << ", Result: " << res << std::endl;
    return res;
}

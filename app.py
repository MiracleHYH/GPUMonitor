from typing import override

from flask import Flask, render_template, jsonify
import threading
import time
import paramiko
import yaml  # 用于加载配置文件

# 全局变量存储服务器状态
server_status = {}

# 全局配置
CONFIG = {}
SERVERS = []
REFRESH_INTERVAL = 5  # 默认刷新间隔


class SSHClientManager:
    def __init__(self, name, hostname, port, username, password):
        """
        初始化 SSH 客户端管理器。
        """
        self.name = name
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.ssh_client = None
        self.connect()

    def connect(self):
        """
        建立 SSH 连接。
        """
        try:
            if self.ssh_client is None or not self.ssh_client.get_transport().is_active():
                self.ssh_client = paramiko.SSHClient()
                self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh_client.connect(
                    hostname=self.hostname,
                    port=self.port,
                    username=self.username,
                    password=self.password
                )
                print(f"Connected to {self.hostname}:{self.port}")
        except Exception as e:
            print(f"Failed to connect to {self.hostname}:{self.port}: {e}")
            self.ssh_client = None

    def execute_command(self, command):
        """
        执行远程命令。如果连接失效，自动重连。
        """
        try:
            if self.ssh_client is None or not self.ssh_client.get_transport().is_active():
                print(f"Reconnecting to {self.hostname}:{self.port}")
                self.connect()
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            return stdout.read().decode(), stderr.read().decode()
        except Exception as e:
            print(f"Failed to execute command on {self.hostname}:{self.port}: {e}")
            return None, str(e)

    def close(self):
        """
        关闭 SSH 连接。
        """
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
            print(f"Disconnected from {self.hostname}:{self.port}")

    def __del__(self):
        """
        析构函数，自动关闭 SSH 连接。
        """
        self.close()


def fetch_server_status():
    """
    定期获取远程服务器的 GPU、CPU 和内存状态。
    """
    global server_status
    managers = {server["name"]: SSHClientManager(**server) for server in SERVERS}

    while True:
        for server in SERVERS:
            server_name = server["name"]
            manager = managers[server_name]

            try:
                # 获取 GPU 信息
                nvidia_output, _ = manager.execute_command(
                    "nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv")
                gpu_info = parse_nvidia_smi_output(nvidia_output)

                # 获取 CPU 和内存信息
                cpu_output, _ = manager.execute_command("top -bn1 | grep 'Cpu(s)'")
                memory_output, _ = manager.execute_command("free -m")

                cpu_usage = parse_cpu_output(cpu_output)
                memory_info = parse_memory_output(memory_output)

                # 更新全局状态
                server_status[server_name] = {
                    "cpu_usage": cpu_usage,
                    "memory_used": memory_info["used"],
                    "memory_total": memory_info["total"],
                    "memory_percentage": memory_info["percentage"],
                    "gpu_info": gpu_info
                }
            except Exception as e:
                print(f"Failed to fetch status for {server_name}: {e}")

        # 按配置的刷新间隔更新
        time.sleep(REFRESH_INTERVAL)


def parse_nvidia_smi_output(output):
    """
    解析 nvidia-smi 输出，提取显卡名称、显存占用和显存使用率。
    """
    gpu_info = []
    for line in output.splitlines()[1:]:  # 跳过表头
        parts = line.split(",")
        gpu_name = parts[0].strip()
        memory_used = int(parts[1].strip().split()[0])  # 提取显存使用
        memory_total = int(parts[2].strip().split()[0])  # 提取显存总量
        usage_percentage = (memory_used / memory_total) * 100
        gpu_info.append({
            "name": gpu_name,
            "memory_used": memory_used,
            "memory_total": memory_total,
            "usage_percentage": round(usage_percentage, 2)
        })
    return gpu_info


def parse_cpu_output(output):
    """
    解析 top 输出中的 CPU 使用率。
    """
    try:
        cpu_line = output.strip().split(",")
        for item in cpu_line:
            if "id" in item:
                idle = float(item.split()[0])
                cpu_usage = 100 - idle
                return round(cpu_usage, 2)
        raise ValueError("Idle value not found in CPU output")
    except Exception as e:
        print(f"Failed to parse CPU output: {e}")
        return 0.0


def parse_memory_output(output):
    """
    解析 free -m 输出中的内存使用情况。
    """
    try:
        lines = output.splitlines()
        for line in lines:
            if line.startswith("Mem:") or line.startswith("内存："):
                parts = line.split()
                total = int(parts[1])
                used = int(parts[2])
                percentage = (used / total) * 100
                return {"total": total, "used": used, "percentage": round(percentage, 2)}
        raise ValueError("Memory information not found in output")
    except Exception as e:
        print(f"Failed to parse memory output: {e}")
        return {"total": 0, "used": 0, "percentage": 0.0}


def load_config():
    """
    从配置文件加载服务器信息和刷新间隔。
    """
    global CONFIG, SERVERS, REFRESH_INTERVAL
    try:
        with open("./config/config.yaml", "r") as f:
            CONFIG = yaml.safe_load(f)
            SERVERS = CONFIG.get("servers", [])
            REFRESH_INTERVAL = CONFIG.get("refresh_interval", 5)
            print("Configuration loaded successfully.")
    except Exception as e:
        print(f"Failed to load configuration: {e}")


def start_background_task():
    """
    启动定期任务线程。
    """
    status_thread = threading.Thread(target=fetch_server_status)
    status_thread.daemon = True
    status_thread.start()
    print("Background task started.")


# 初始化 Flask 应用
app = Flask(__name__)

# 加载配置文件
load_config()

# 启动后台任务
start_background_task()


@app.route("/")
def home():
    """
    渲染主页面，显示服务器状态。
    """
    return render_template("index.html", server_status=server_status)


@app.route("/api/server_status")
def get_server_status():
    """
    返回服务器状态的 JSON 数据。
    """
    return jsonify(server_status)


if __name__ == "__main__":
    # 启动 Flask 应用
    app.run(host="0.0.0.0", port=5000, debug=False)



import paramiko

# 定义服务器列表，包括服务器名称、IP地址、端口号、用户名和密码
servers = [

    {"name": "美国", "hostname": "1.1.1.1", "port": 22, "username": "root", "password": "123456"},   
    {"name": "不丹", "hostname": "1.1.1.1", "port": 22, "username": "root", "password": "123456"},   
    {"name": "毛里求斯", "hostname": "1.1.1.1", "port": 22, "username": "root", "password": "123456"},   
    # 添加更多服务器

]


# 定义更新操作
def update_server(name, hostname, port, username, password):
    try:

        # 连接服务器
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username, password=password)

        # 设置 DEBIAN_FRONTEND 环境变量
        print(f"{name} 开启BBR加速")
        stdin, stdout, stderr = client.exec_command('cat > /etc/sysctl.conf << EOF\nnet.core.default_qdisc=fq_pie\nnet.ipv4.tcp_congestion_control=bbr\nEOF\nsudo sysctl -p\n')
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end="")

        # 检查更新状态
        if stderr.channel.recv_exit_status() == 0:
            print(f"启动成功")
        else:
            print(f"启动失败")


        # 关闭 SSH 连接
        client.close()

        print()        
    
    except Exception as e:
        print(f"连接 {name} 失败 \n")

# 遍历服务器列表，逐一更新
for server in servers:
    name = server["name"]
    hostname = server["hostname"]
    port = server["port"]
    username = server["username"]
    password = server["password"]
    update_server(name, hostname, port, username, password)

# 等待用户按下任意键后关闭窗口
input("按任意键关闭窗口...")

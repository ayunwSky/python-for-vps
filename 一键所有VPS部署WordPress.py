import paramiko

servers = [

    {"name": "美国", "hostname": "1.1.1.1", "port": 22, "username": "root", "password": "123456", "domain": "yuming.com"},   
    {"name": "不丹", "hostname": "1.1.1.1", "port": 22, "username": "root", "password": "123456", "domain": "yuming.com"},   
    {"name": "毛里求斯", "hostname": "1.1.1.1", "port": 22, "username": "root", "password": "123456", "domain": "yuming.com"},   
    # 添加更多服务器

]

# 公钥路径
# /home/nginx/certs/cert.pem
# 
# 私钥路径
# /home/nginx/certs/key.pem

# 定义更新操作
def update_server(name, hostname, port, username, password, domain):
    try:

        # 连接服务器
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username, password=password)


        print(f" {name} 更新")
        stdin, stdout, stderr = client.exec_command("apt update -y && apt install -y curl wget sudo socat")
        
        print(f"正在更新:")
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end="")

        # 检查执行状态
        if stderr.channel.recv_exit_status() == 0:
            print(f"更新成功")
        else:
            print(f"更新失败")
        
        print()

        print(f"{name} 安装 Docker")
        stdin, stdout, stderr = client.exec_command("wget -qO- https://get.docker.com/ | sh")

        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end="")

        # 检查执行状态
        if stderr.channel.recv_exit_status() == 0:
            print(f"安装 Docker 成功")
        else:
            print(f"安装 Docker 失败")

        print()



        print(f"{name} 创建WP专用网络")
        stdin, stdout, stderr = client.exec_command("docker network create my_network")

        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end="")


        print()

        print(f"{name} 安装WordPress")
        stdin, stdout, stderr = client.exec_command("mkdir -p /home/wp1/mysql && \
                                                        docker run -d \
                                                        --name my_wordpress \
                                                        --restart=always \
                                                        -p 9000:80 \
                                                        -e WORDPRESS_DB_HOST=my_mysql \
                                                        -e WORDPRESS_DB_NAME=wordpress \
                                                        -e WORDPRESS_DB_USER=wordpress \
                                                        -e WORDPRESS_DB_PASSWORD=wordpress_password \
                                                        -v /home/wp1/wp-data:/var/www/html \
                                                        --network my_network \
                                                        wordpress")

        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end="")

        # 检查执行状态
        if stderr.channel.recv_exit_status() == 0:
            print(f"安装成功")
        else:
            print(f"安装失败")

        print()


        print(f"{name} 安装MySQL")
        stdin, stdout, stderr = client.exec_command("docker run -d \
                                                        --name my_mysql \
                                                        --restart=always \
                                                        -e MYSQL_ROOT_PASSWORD=root_password \
                                                        -e MYSQL_DATABASE=wordpress \
                                                        -e MYSQL_USER=wordpress \
                                                        -e MYSQL_PASSWORD=wordpress_password \
                                                        -v /home/wp1/mysql:/var/lib/mysql \
                                                        --network my_network \
                                                        mysql")

        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end="")

        # 检查执行状态
        if stderr.channel.recv_exit_status() == 0:
            print(f"安装成功")
        else:
            print(f"安装失败")

        print()

        print(f"{name} 创建nginx目录")
        stdin, stdout, stderr = client.exec_command("mkdir -p /home/nginx\ntouch /home/nginx/nginx.conf &&\
                                                    mkdir -p /home/nginx/certs")

        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end="")

        # 检查执行状态
        if stderr.channel.recv_exit_status() == 0:
            print(f"创建目录成功")
        else:
            print(f"创建目录失败")

        print()

        print(f"{name} 申请证书")
        stdin, stdout, stderr = client.exec_command("curl https://get.acme.sh | sh &&\
                                                     ~/.acme.sh/acme.sh --register-account -m xxxx@gmail.com && ~/.acme.sh/acme.sh --issue -d {} --standalone".format(domain))
        print(f"正在申请中:")
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end="")

        # 检查执行状态
        if stderr.channel.recv_exit_status() == 0:
            print(f"申请成功")
        else:
            print(f"申请失败")

        print()

        print(f"{name} 下载证书")
        stdin, stdout, stderr = client.exec_command("~/.acme.sh/acme.sh --installcert -d {} --key-file /home/nginx/certs/wp_key.pem --fullchain-file /home/nginx/certs/wp_cert.pem".format(domain))
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end="")

        # 检查执行状态
        if stderr.channel.recv_exit_status() == 0:
            print(f"下载证书成功")
        else:
            print(f"下载证书失败")

        print()        

        print(f"{name} 配置nginx")

        # 重定向到那个网站
        redirect = f"{hostname}:9000"
        stdin, stdout, stderr = client.exec_command('wget -O /home/nginx/nginx.conf https://raw.githubusercontent.com/kejilion/nginx/main/nginx_wp.conf && sed -i "s/wp.com/' + domain + '/g" /home/nginx/nginx.conf && sed -i "s/wp.wp.wp.wp:9000/' + redirect + '/g" /home/nginx/nginx.conf')
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end="")

        # 检查执行状态
        if stderr.channel.recv_exit_status() == 0:
            print(f"配置成功")
        else:
            print(f"配置失败")

        print()

        print(f"{name} 安装nginx")
        stdin, stdout, stderr = client.exec_command('docker run -d --name nginx --restart=always -p 80:80 -p 443:443 -v /home/nginx/nginx.conf:/etc/nginx/nginx.conf -v /home/nginx/certs:/etc/nginx/certs -v /home/nginx/html:/usr/share/nginx/html nginx:latest')
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end="")

        # 检查执行状态
        if stderr.channel.recv_exit_status() == 0:
            print(f"安装成功")
        else:
            print(f"安装失败")

        print()

        print(f"{name} nginx启动状态")
        stdin, stdout, stderr = client.exec_command('docker ps -a')
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end="")

        print(f"搭建完成\nhttps://{domain}")
        print()
        print()

        # 关闭 SSH 连接
        client.close()


    except Exception as e:
        print(f"连接 {name} 失败")


# 遍历服务器列表，逐一更新
for server in servers:
    name = server["name"]
    hostname = server["hostname"]
    port = server["port"]
    username = server["username"]
    password = server["password"]
    domain = server["domain"]
    update_server(name, hostname, port, username, password, domain)

# 等待用户按下任意键后关闭窗口
input("按任意键关闭窗口...")



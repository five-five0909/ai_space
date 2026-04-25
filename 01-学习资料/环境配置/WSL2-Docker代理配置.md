# WSL2 + Docker 代理配置

## 原理说明

WSL2 每次启动宿主机 IP 会变，存在 `/etc/resolv.conf` 的 nameserver 里。
curl/wget 等工具读 shell 环境变量的代理，但 **Docker daemon 是独立服务，必须单独配置**。

---

## 一、WSL2 Shell 代理（让 curl/wget/pip 等走代理）

编辑 `~/.bashrc` 或 `~/.zshrc`，加在末尾：

```bash
# WSL2 动态代理
export HOST_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
export http_proxy="http://${HOST_IP}:7897"
export https_proxy="http://${HOST_IP}:7897"
export no_proxy="localhost,127.0.0.1"
```

端口改成你代理软件实际端口（Clash 一般是 `7890` 或 `7897`）。

生效：
```bash
source ~/.zshrc
```

---

## 二、Docker Daemon 代理（让 docker pull 走代理）

### 2.1 创建自动配置脚本

```bash
sudo tee /usr/local/bin/set-docker-proxy.sh <<'EOF'
#!/bin/bash
HOST_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
PROXY_PORT=7897

mkdir -p /etc/systemd/system/docker.service.d

cat > /etc/systemd/system/docker.service.d/proxy.conf <<CONF
[Service]
Environment="HTTP_PROXY=http://${HOST_IP}:${PROXY_PORT}"
Environment="HTTPS_PROXY=http://${HOST_IP}:${PROXY_PORT}"
Environment="NO_PROXY=localhost,127.0.0.1"
CONF

systemctl daemon-reload
systemctl restart docker
echo "Docker proxy set to ${HOST_IP}:${PROXY_PORT}"
EOF

sudo chmod +x /usr/local/bin/set-docker-proxy.sh
```

### 2.2 注册为开机自启服务

```bash
sudo tee /etc/systemd/system/docker-proxy-setup.service <<EOF
[Unit]
Description=Set Docker proxy with dynamic WSL2 host IP
After=network.target docker.service
Requires=docker.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/set-docker-proxy.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable docker-proxy-setup.service
```

### 2.3 立即生效

```bash
sudo /usr/local/bin/set-docker-proxy.sh
```

---

## 三、验证

```bash
# 验证 shell 代理
curl -v https://www.google.com

# 验证 docker 代理
docker pull hello-world
```

---

## 四、注意事项

- 代理端口按实际修改，Clash 常见端口：`7890` / `7897`
- WSL2 重启后 shell 代理自动生效（.zshrc），docker 代理由 systemd 服务自动重设
- 若宿主机关闭代理软件，docker pull 会超时，正常现象

---

## 五、一键脚本（完整版）

如果想一次性完成所有配置，可以使用以下一键脚本：

```bash
# WSL2 Shell 代理配置
cat >> ~/.zshrc <<'EOF'

# WSL2 动态代理
export HOST_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
export http_proxy="http://${HOST_IP}:7897"
export https_proxy="http://${HOST_IP}:7897"
export no_proxy="localhost,127.0.0.1"
EOF

# Docker Daemon 代理配置脚本
sudo tee /usr/local/bin/set-docker-proxy.sh <<'EOF'
#!/bin/bash
HOST_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
PROXY_PORT=7897

mkdir -p /etc/systemd/system/docker.service.d

cat > /etc/systemd/system/docker.service.d/proxy.conf <<CONF
[Service]
Environment="HTTP_PROXY=http://${HOST_IP}:${PROXY_PORT}"
Environment="HTTPS_PROXY=http://${HOST_IP}:${PROXY_PORT}"
Environment="NO_PROXY=localhost,127.0.0.1"
CONF

systemctl daemon-reload
systemctl restart docker
echo "Docker proxy set to ${HOST_IP}:${PROXY_PORT}"
EOF

sudo chmod +x /usr/local/bin/set-docker-proxy.sh

# 注册开机自启服务
sudo tee /etc/systemd/system/docker-proxy-setup.service <<EOF
[Unit]
Description=Set Docker proxy with dynamic WSL2 host IP
After=network.target docker.service
Requires=docker.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/set-docker-proxy.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable docker-proxy-setup.service

# 立即生效
source ~/.zshrc
sudo /usr/local/bin/set-docker-proxy.sh

echo "配置完成！请运行以下命令验证："
echo "  curl -v https://www.google.com"
echo "  docker pull hello-world"
```
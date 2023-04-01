# McyangBackEnd_DockerVersion
## 1. 项目介绍
這是一個基於Docker的後端服務器，使用Django作為後端框架，使用MariaDB作為資料庫，使用Docker Compose作為容器管理工具。
這個專案是"情境劇本Beacon互動教學工具"的後端服務器，用於提供手機應用程式的API。

學生端APP: https://github.com/NakiriYuuzu/New_McyangStudent

老師端APP: https://github.com/NakiriYuuzu/New_McyangTeacher

---
## 2. 项目结构
### 2.1 API
請參考 https://blog.csdn.net/Carrie_Q/article/details/117811425

    1. 打開Postman匯入documentation/api/McyangAPI.postman_collection.json
    2. 選擇McyangAPI
    3. 選擇API然後選擇送出就可以測試API

### 2.2 資料庫設計
![img.png](documentation/image/img.png)

---
## 3. 项目部署
```bash
# 1. 安装docker
#!/bin/bash

# 更新資源
sudo apt-get update

# 安裝必要的一些系統工具
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# 添加Docker的官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 更新資源
sudo apt-get update

# 安裝docker
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# 添加docker用户组
sudo usermod -aG docker $USER

# 2. 安装docker-compose
sudo apt-get install -y docker-compose

# 3. Git clone项目
git clone https://github.com/NakiriYuuzu/McyangDockerServer.git

# 4. 进入项目目录
cd McyangDockerServer

# 5. 启动项目
docker-compose up --build    # 启动项目與視窗
docker-compose up -d --build # 启动项目與背景執行

# 6. 停止项目
docker-compose down

# 設定 django Admin
docker-compose exec web python manage.py createsuperuser

# Docker 其他指令
docker-compose exec [請看docker-compose.yml 内容有 db 和 web] bash # 進入容器
docker-compose ps # 查看容器狀態
```

### 如啓動失敗，請在啓動一次
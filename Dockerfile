# 使用官方轻量级 Python 镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 拷贝依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝项目文件到容器中
COPY . .

# 暴露应用端口
EXPOSE 5000

# 启动应用，使用 Gunicorn 作为 WSGI 服务器
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

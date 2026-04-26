FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data

# 环境变量
ENV PYTHONUNBUFFERED=1

# 启动命令
CMD ["python", "-m", "bot.main"]

# 使用官方的PostgreSQL镜像作为基础镜像
FROM postgres:latest

# 安装构建工具和依赖项
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        postgresql-server-dev-all \
    && rm -rf /var/lib/apt/lists/*

# 克隆pg_vector扩展的源代码
RUN git -c http.sslVerify=false clone https://github.com/pgvector/pgvector.git

# 编译和安装pg_vector扩展
RUN cd pgvector \
    && make \
    && make install

# 启动PostgreSQL服务
CMD ["postgres"]
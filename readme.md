#参考Gradio

https://www.gradio.app/guides/creating-a-chatbot-fast


## 本地调试 需一个支持PG vector扩展的库 

构造一个镜像 - 如需要

```bash
docker build -t my_postgres .
```

启动容器

```bash
docker run --name vg_my_postgres -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d vg_postgres
```
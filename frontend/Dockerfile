# 前端 Dockerfile - 使用华为云镜像
# dist 目录已本地构建好，直接使用

# 生产阶段
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/nginx:alpine

# 复制已构建的静态文件
COPY dist /usr/share/nginx/html

# 复制 nginx 配置
COPY frontend.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
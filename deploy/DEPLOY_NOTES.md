# Deploy Notes (ECS 实际状态 vs git)

> 7-20 记录: ECS 上历史手维护的差异, 不要轻易 unify, 改了反而会让当前 production 502

## nginx 容器

- **ECS 实际**: 手动 `docker run` 起的孤儿容器, 不在 docker-compose.prod.yml 管理内
- **git 状态**: docker-compose.prod.yml 里也定义了 nginx service (未启用)
- **为什么不 unifiy 到 compose**: 一旦 `docker compose up -d` 会创建新 nginx 容器, 跟手动的争端口 (80/443); 而且 nginx.conf 是用容器内的 213 行版本 (含 babyname server block), 不是 bind mount
- **风险**: 手动 run 的容器不会跟着 `docker-compose down/up` 重起, 只能 `docker restart english_learning_nginx`

## nginx.conf

- **ECS 实际**: 容器内 `/etc/nginx/nginx.conf` (213 行, 含 babyname server block)
- **git 跟踪**: `deploy/nginx/nginx.conf` (已 sync 213 行版本)
- **bind mount**: 容器没有 bind mount nginx.conf, 只有 ssl; 因此 git 里的 nginx.conf **没生效**

## SSL 证书

- **来源**: `/etc/letsencrypt/live/{fluenty.cn,api.babyname.asia}/`
- **同步目标**: `/opt/english-learning/deploy/nginx/ssl/{,fluenty.cn/,babyname/}`
- **历史问题 (7-20)**: 长期缺 fullchain.pem, `nginx -s reload` emerg 起不来, 502
- **修复**: `deploy/deploy-server.sh [5/8]` 自动从 letsencrypt cp 到 deploy dir

## network 名

- **ECS 实际**: `english-learning_english_learning_network` (compose 创建的实际名)
- **compose 配置**: 写 `english_learning_network` (旧名/别名)
- **效果**: docker compose 创建时自动 alias, 功能正常
- **为什么不动**: 改 network 名会触发容器重建, 当前 production 别动
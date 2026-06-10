#!/bin/bash
# 一键部署到服务器
SERVER="root@8.137.184.79"
REMOTE_DIR="/opt/morning-briefing"

echo "=== 部署早报系统到服务器 ==="

# 1. 上传代码
echo "上传代码..."
rsync -az --checksum \
  config.py news_fetcher.py script_generator.py \
  tts_generator.py alexa_feed.py run.py requirements.txt \
  "$SERVER:$REMOTE_DIR/"

# 2. 上传 .env（如果本地有）
if [ -f .env ]; then
  scp .env "$SERVER:$REMOTE_DIR/.env"
fi

# 3. 服务器上安装依赖
echo "安装依赖..."
ssh "$SERVER" "cd $REMOTE_DIR && pip3 install -r requirements.txt -q && apt-get install -y ffmpeg -q 2>/dev/null || true"

# 4. 创建目录
ssh "$SERVER" "mkdir -p $REMOTE_DIR/audio $REMOTE_DIR/scripts"

# 5. 设置 nginx 静态托管
echo "配置 nginx..."
ssh "$SERVER" "cat > /etc/nginx/conf.d/briefing.conf << 'EOF'
location /briefing/ {
    alias /opt/morning-briefing/;
    autoindex off;
    add_header Access-Control-Allow-Origin *;
    add_header Cache-Control \"no-cache, must-revalidate\";
}
EOF
nginx -t && nginx -s reload"

# 6. 设置 cron（UTC 6:00 = 爱尔兰夏令时 7:00）
echo "设置定时任务..."
ssh "$SERVER" "(crontab -l 2>/dev/null | grep -v morning-briefing; echo '0 6 * * * cd /opt/morning-briefing && python3 run.py >> /opt/morning-briefing/cron.log 2>&1') | crontab -"

echo ""
echo "=== 部署完成！==="
echo ""
echo "测试命令（服务器上手动跑一次）："
echo "  ssh $SERVER 'cd /opt/morning-briefing && python3 run.py'"
echo ""
echo "查看日志："
echo "  ssh $SERVER 'tail -f /opt/morning-briefing/cron.log'"
echo ""
echo "接下来需要在 Alexa Developer Console 配置 Flash Briefing："
echo "  Feed URL: https://zlifelog.xin/briefing/feed.json"

#!/bin/bash

# ========================================
#  日志查看脚本
# ========================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

LOG_DIR="/opt/english-learning/logs"

# 显示帮助
show_help() {
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  all       查看全量日志 (app.log)"
    echo "  info      查看 INFO 级别日志"
    echo "  error     查看 ERROR 级别日志"
    echo "  warning   查看 WARNING 级别日志"
    echo "  tail      实时跟踪所有日志"
    echo "  clean     清理7天前的旧日志"
    echo "  size      查看日志文件大小"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 error        # 查看错误日志"
    echo "  $0 tail         # 实时查看日志"
    echo "  $0 error -n 50  # 查看最近50行错误日志"
    echo ""
}

# 检查日志目录
check_log_dir() {
    if [ ! -d "$LOG_DIR" ]; then
        echo -e "${RED}日志目录不存在: $LOG_DIR${NC}"
        echo "请确保服务已启动并生成了日志文件"
        exit 1
    fi
}

# 查看日志
view_log() {
    local log_file=$1
    local lines=${2:-100}

    if [ ! -f "$log_file" ]; then
        echo -e "${YELLOW}日志文件不存在: $log_file${NC}"
        return
    fi

    echo -e "${GREEN}=== $log_file (最近 $lines 行) ===${NC}"
    tail -n $lines "$log_file"
    echo ""
}

# 实时跟踪日志
tail_logs() {
    echo -e "${GREEN}实时跟踪日志 (Ctrl+C 退出)...${NC}"
    echo ""

    # 检查哪些日志文件存在
    local files=""
    [ -f "$LOG_DIR/app.log" ] && files="$files $LOG_DIR/app.log"
    [ -f "$LOG_DIR/error.log" ] && files="$files $LOG_DIR/error.log"

    if [ -z "$files" ]; then
        echo -e "${RED}没有找到日志文件${NC}"
        exit 1
    fi

    tail -f $files
}

# 清理旧日志
clean_old_logs() {
    echo -e "${YELLOW}清理7天前的旧日志...${NC}"
    find $LOG_DIR -name "*.log.*" -mtime +7 -delete
    echo -e "${GREEN}清理完成${NC}"
}

# 显示日志大小
show_size() {
    echo -e "${GREEN}日志文件大小:${NC}"
    echo ""
    echo "文件名                    大小        修改时间"
    echo "--------------------------------------------------------"

    for file in $LOG_DIR/*.log; do
        if [ -f "$file" ]; then
            size=$(du -h "$file" | cut -f1)
            mtime=$(stat -c %y "$file" 2>/dev/null | cut -d. -f1)
            printf "%-25s %-10s %s\n" "$(basename $file)" "$size" "$mtime"
        fi
    done

    echo ""
    echo -e "总大小: $(du -sh $LOG_DIR | cut -f1)"
}

# 主逻辑
case "$1" in
    all|app)
        check_log_dir
        view_log "$LOG_DIR/app.log" ${3:-100}
        ;;
    info)
        check_log_dir
        view_log "$LOG_DIR/info.log" ${3:-100}
        ;;
    error|err)
        check_log_dir
        view_log "$LOG_DIR/error.log" ${3:-100}
        ;;
    warning|warn)
        check_log_dir
        view_log "$LOG_DIR/warning.log" ${3:-100}
        ;;
    tail|f)
        check_log_dir
        tail_logs
        ;;
    clean)
        check_log_dir
        clean_old_logs
        ;;
    size|du)
        check_log_dir
        show_size
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        echo -e "${RED}未知选项: $1${NC}"
        show_help
        exit 1
        ;;
esac

#!/usr/bin/env bash
#
# Kimi 配置安装脚本 - TDD 实现
#

set -euo pipefail

# 路径配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
INSTALL_DIR="${HOME}/.kimi"
SKILLS_DIR="${INSTALL_DIR}/skills"
AGENT_DIR="${INSTALL_DIR}/agents/superpower"

# 源文件路径
SKILLS_SOURCE="${PROJECT_ROOT}/kimi/skills"
AGENT_SOURCE="${PROJECT_ROOT}/kimi/agents/superpower"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERR]${NC} $1"; }

# 检查源文件
check_source() {
    if [[ ! -d "$SKILLS_SOURCE" ]]; then
        error "Skills 源目录不存在: $SKILLS_SOURCE"
        exit 1
    fi
    if [[ ! -f "$AGENT_SOURCE/agent.yaml" ]]; then
        error "Agent 配置文件不存在: $AGENT_SOURCE/agent.yaml"
        exit 1
    fi
}

# 复制 skills 到目标目录
copy_skills() {
    local target="$1"
    rm -rf "${target:?}/"*
    cp -r "${SKILLS_SOURCE}/"* "$target/"
}

# 复制 agent 到目标目录
copy_agent() {
    local target="$1"
    rm -rf "${target:?}/"*
    cp -r "${AGENT_SOURCE}/"* "$target/"
}

# 获取 skills 数量
count_skills() {
    find "$SKILLS_DIR" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' '
}

# 创建启动脚本
create_wrapper() {
    local wrapper="${PROJECT_ROOT}/kimi-superpower"
    cat > "$wrapper" << EOF
#!/usr/bin/env bash
# Kimi Superpower 启动脚本
exec kimi --agent-file "${AGENT_DIR}/agent.yaml" "\$@"
EOF
    chmod +x "$wrapper"
    echo "$wrapper"
}

# 删除启动脚本
remove_wrapper() {
    local wrapper="${PROJECT_ROOT}/kimi-superpower"
    [[ -f "$wrapper" ]] && rm -f "$wrapper"
}

# 安装配置
cmd_install() {
    local force=false
    [[ "${1:-}" == "-f" || "${1:-}" == "--force" ]] && force=true

    check_source

    info "安装 Kimi 配置到 ${INSTALL_DIR}"

    # 如果已存在且非强制模式，询问用户
    if [[ -d "$SKILLS_DIR" ]] && [[ "$force" == false ]]; then
        warn "配置已存在: ${SKILLS_DIR}"
        read -p "是否覆盖? [y/N] " -n 1 -r
        echo
        [[ $REPLY =~ ^[Yy]$ ]] || { info "取消安装"; exit 0; }
    fi

    # 创建目录
    mkdir -p "$SKILLS_DIR" "$AGENT_DIR"

    # 复制 Skills
    info "复制 Skills..."
    copy_skills "$SKILLS_DIR"
    success "Skills 安装完成 ($(count_skills) 个)"

    # 复制 Agent
    info "复制 Agent 配置..."
    copy_agent "$AGENT_DIR"
    success "Agent 安装完成"

    # 创建启动脚本
    local wrapper
    wrapper=$(create_wrapper)
    success "启动脚本已创建: ${wrapper/#$HOME/~}"

    echo
    success "安装完成!"
    echo
    echo "使用方法:"
    echo "  ./kimi-superpower"
    echo
    echo "或使用完整路径:"
    echo "  kimi --agent-file ${AGENT_DIR/#$HOME/~}/agent.yaml"
}

# 更新配置
cmd_update() {
    check_source

    if [[ ! -d "$SKILLS_DIR" ]]; then
        error "未找到已安装的配置，请先运行: $0 install"
        exit 1
    fi

    info "更新配置..."

    copy_skills "$SKILLS_DIR"
    copy_agent "$AGENT_DIR"

    success "更新完成 ($(count_skills) 个 skills)"
}

# 卸载配置
cmd_uninstall() {
    local force=false
    [[ "${1:-}" == "-f" || "${1:-}" == "--force" ]] && force=true

    if [[ ! -d "$SKILLS_DIR" ]]; then
        warn "未找到配置: ${SKILLS_DIR}"
        exit 0
    fi

    if [[ "$force" == false ]]; then
        warn "将删除: ${INSTALL_DIR}"
        read -p "确认卸载? [y/N] " -n 1 -r
        echo
        [[ $REPLY =~ ^[Yy]$ ]] || { info "取消卸载"; exit 0; }
    fi

    info "卸载配置..."
    rm -rf "${INSTALL_DIR}"
    remove_wrapper

    success "卸载完成"
}

# 查看状态
cmd_status() {
    echo "=== Kimi 配置状态 ==="
    echo
    echo "安装目录: ${INSTALL_DIR/#$HOME/~}"
    echo

    # 检查 Skills
    if [[ -d "$SKILLS_DIR" ]]; then
        success "Skills: $(count_skills) 个 (${SKILLS_DIR/#$HOME/~})"
    else
        warn "Skills: 未安装"
    fi

    # 检查 Agent
    if [[ -f "$AGENT_DIR/agent.yaml" ]]; then
        success "Agent: 已安装 (${AGENT_DIR/#$HOME/~})"
    else
        warn "Agent: 未安装"
    fi

    # 检查源文件
    echo
    echo "源文件:"
    if [[ -d "$SKILLS_SOURCE" ]]; then
        success "Skills: $(find "$SKILLS_SOURCE" -name "SKILL.md" | wc -l | tr -d ' ') 个"
    else
        error "Skills 源文件缺失"
    fi

    if [[ -f "$AGENT_SOURCE/agent.yaml" ]]; then
        success "Agent: 存在"
    else
        error "Agent 源文件缺失"
    fi

    # 检查启动脚本
    echo
    if [[ -f "${PROJECT_ROOT}/kimi-superpower" ]]; then
        success "启动脚本: ${PROJECT_ROOT/#$HOME/~}/kimi-superpower"
    else
        warn "启动脚本: 未创建"
    fi
}

# 显示帮助
usage() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

Commands:
    install     安装配置 (默认)
    update      更新配置
    uninstall   卸载配置
    status      查看状态

Options:
    -f, --force     强制安装/卸载，不询问
    -h, --help      显示帮助

Examples:
    $0                      # 安装配置
    $0 install -f           # 强制安装（覆盖）
    $0 update               # 更新配置
    $0 uninstall            # 卸载配置
    $0 status               # 查看状态
EOF
}

# 主函数
main() {
    local cmd="${1:-install}"

    case "$cmd" in
        install|i)
            shift || true
            cmd_install "$@"
            ;;
        update|u)
            cmd_update
            ;;
        uninstall|remove|rm)
            shift || true
            cmd_uninstall "$@"
            ;;
        status|s|check)
            cmd_status
            ;;
        -h|--help|help)
            usage
            exit 0
            ;;
        *)
            error "未知命令: $cmd"
            usage
            exit 1
            ;;
    esac
}

main "$@"

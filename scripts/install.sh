#!/usr/bin/env bash
#
# 配置安装脚本 - 支持 Kimi 和 Codex 平台
#

set -euo pipefail

# 基础路径配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# 平台相关变量（由 init_paths 函数初始化）
PLATFORM=""
INSTALL_DIR=""
SKILLS_DIR=""
AGENT_DIR=""
SKILLS_SOURCE=""
AGENT_SOURCE=""

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

# 初始化平台相关路径
init_paths() {
    local platform="${1:-kimi}"
    PLATFORM="$platform"
    
    if [[ "$PLATFORM" == "kimi" ]]; then
        # Kimi: 使用 ~/.kimi/ 目录结构
        INSTALL_DIR="${HOME}/.kimi"
        SKILLS_DIR="${INSTALL_DIR}/skills"
        AGENT_DIR="${INSTALL_DIR}/agents/superpower"
        SKILLS_SOURCE="${PROJECT_ROOT}/kimi/skills"
        AGENT_SOURCE="${PROJECT_ROOT}/kimi/agents/superpower"
    else
        # Codex: 使用 ~/.agents/skills/ 目录结构（符合官方规范）
        INSTALL_DIR="${HOME}/.agents"
        SKILLS_DIR="${INSTALL_DIR}/skills"
        AGENT_DIR=""  # Codex 不使用 agent 目录
        SKILLS_SOURCE="${PROJECT_ROOT}/codex/skills"
        AGENT_SOURCE=""
    fi
}

# 检查源文件
check_source() {
    if [[ ! -d "$SKILLS_SOURCE" ]]; then
        error "Skills 源目录不存在: $SKILLS_SOURCE"
        exit 1
    fi
    
    # Kimi 需要检查 agent 配置
    if [[ "$PLATFORM" == "kimi" ]]; then
        if [[ ! -f "$AGENT_SOURCE/agent.yaml" ]]; then
            error "Agent 配置文件不存在: $AGENT_SOURCE/agent.yaml"
            exit 1
        fi
    fi
}

# 复制 skills 到目标目录
copy_skills() {
    local target="$1"
    rm -rf "${target:?}/"*
    cp -r "${SKILLS_SOURCE}/"* "$target/"
}

# 复制 agent 到目标目录 (仅 Kimi)
copy_agent() {
    local target="$1"
    rm -rf "${target:?}/"*
    cp -r "${AGENT_SOURCE}/"* "$target/"
}

# 获取 skills 数量
count_skills() {
    find "$SKILLS_DIR" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' '
}

# 创建启动脚本 (仅 Kimi)
create_wrapper() {
    if [[ "$PLATFORM" != "kimi" ]]; then
        return
    fi
    
    local wrapper="${PROJECT_ROOT}/kimi-superpower"
    cat > "$wrapper" << EOF
#!/usr/bin/env bash
# Kimi Superpower 启动脚本
exec kimi --agent-file "${AGENT_DIR}/agent.yaml" "\$@"
EOF
    chmod +x "$wrapper"
    echo "$wrapper"
}

# 删除启动脚本 (仅 Kimi)
remove_wrapper() {
    if [[ "$PLATFORM" != "kimi" ]]; then
        return
    fi
    
    local wrapper="${PROJECT_ROOT}/kimi-superpower"
    [[ -f "$wrapper" ]] && rm -f "$wrapper"
}

# 安装配置
cmd_install() {
    local force=false
    [[ "${1:-}" == "-f" || "${1:-}" == "--force" ]] && force=true

    check_source

    if [[ "$PLATFORM" == "kimi" ]]; then
        info "安装 Kimi 配置到 ${INSTALL_DIR}"
    else
        info "安装 Codex skills 到 ${SKILLS_DIR}"
    fi

    # 如果已存在且非强制模式，询问用户
    if [[ -d "$SKILLS_DIR" ]] && [[ "$force" == false ]]; then
        warn "配置已存在: ${SKILLS_DIR}"
        read -p "是否覆盖? [y/N] " -n 1 -r
        echo
        [[ $REPLY =~ ^[Yy]$ ]] || { info "取消安装"; exit 0; }
    fi

    # 创建目录
    mkdir -p "$SKILLS_DIR"
    
    # Kimi 需要创建 agent 目录
    if [[ "$PLATFORM" == "kimi" ]]; then
        mkdir -p "$AGENT_DIR"
    fi

    # 复制 Skills
    info "复制 Skills..."
    copy_skills "$SKILLS_DIR"
    success "Skills 安装完成 ($(count_skills) 个)"

    # Kimi 复制 Agent
    if [[ "$PLATFORM" == "kimi" ]]; then
        info "复制 Agent 配置..."
        copy_agent "$AGENT_DIR"
        success "Agent 安装完成"

        # 创建启动脚本
        local wrapper
        wrapper=$(create_wrapper)
        success "启动脚本已创建: ${wrapper/#$HOME/~}"
    fi

    echo
    success "安装完成!"
    
    if [[ "$PLATFORM" == "kimi" ]]; then
        echo
        echo "使用方法:"
        echo "  ./kimi-superpower"
        echo
        echo "或使用完整路径:"
        echo "  kimi --agent-file ${AGENT_DIR/#$HOME/~}/agent.yaml"
    else
        echo
        echo "使用方法:"
        echo "  codex"
        echo
        echo "Skills 已安装到: ${SKILLS_DIR/#$HOME/~}"
        echo "运行 'codex' 后使用 /skills 查看已加载的技能"
    fi
}

# 更新配置
cmd_update() {
    check_source

    if [[ ! -d "$SKILLS_DIR" ]]; then
        error "未找到已安装的配置，请先运行: $0 ${PLATFORM} install"
        exit 1
    fi

    info "更新 ${PLATFORM} 配置..."

    copy_skills "$SKILLS_DIR"
    
    if [[ "$PLATFORM" == "kimi" ]]; then
        copy_agent "$AGENT_DIR"
    fi

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

    info "卸载 ${PLATFORM} 配置..."
    rm -rf "${INSTALL_DIR}"
    remove_wrapper

    success "卸载完成"
}

# 查看状态
cmd_status() {
    echo "=== ${PLATFORM} 配置状态 ==="
    echo
    
    if [[ "$PLATFORM" == "kimi" ]]; then
        echo "安装目录: ${INSTALL_DIR/#$HOME/~}"
    else
        echo "Skills 目录: ${SKILLS_DIR/#$HOME/~}"
    fi
    echo

    # 检查 Skills
    if [[ -d "$SKILLS_DIR" ]]; then
        success "Skills: $(count_skills) 个 (${SKILLS_DIR/#$HOME/~})"
    else
        warn "Skills: 未安装"
    fi

    # Kimi 检查 Agent
    if [[ "$PLATFORM" == "kimi" ]]; then
        if [[ -f "$AGENT_DIR/agent.yaml" ]]; then
            success "Agent: 已安装 (${AGENT_DIR/#$HOME/~})"
        else
            warn "Agent: 未安装"
        fi
    fi

    # 检查源文件
    echo
    echo "源文件:"
    if [[ -d "$SKILLS_SOURCE" ]]; then
        success "Skills: $(find "$SKILLS_SOURCE" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ') 个"
    else
        error "Skills 源文件缺失: ${SKILLS_SOURCE}"
    fi

    if [[ "$PLATFORM" == "kimi" ]]; then
        if [[ -f "$AGENT_SOURCE/agent.yaml" ]]; then
            success "Agent: 存在"
        else
            error "Agent 源文件缺失: ${AGENT_SOURCE}"
        fi
    fi

    # Kimi 检查启动脚本
    if [[ "$PLATFORM" == "kimi" ]]; then
        echo
        if [[ -f "${PROJECT_ROOT}/kimi-superpower" ]]; then
            success "启动脚本: ${PROJECT_ROOT/#$HOME/~}/kimi-superpower"
        else
            warn "启动脚本: 未创建"
        fi
    fi
}

# 显示帮助
usage() {
    cat << EOF
Usage: $0 [PLATFORM] [COMMAND] [OPTIONS]

Platforms:
    kimi        Kimi CLI (默认)
    codex       Codex CLI

Commands:
    install     安装配置 (默认)
    update      更新配置
    uninstall   卸载配置
    status      查看状态

Options:
    -f, --force     强制安装/卸载，不询问
    -h, --help      显示帮助

Examples:
    $0                      # 安装 kimi 配置
    $0 kimi install         # 安装 kimi 配置
    $0 codex install        # 安装 codex skills 到 ~/.agents/skills/
    $0 codex install -f     # 强制安装 codex 配置
    $0 kimi update          # 更新 kimi 配置
    $0 codex status         # 查看 codex 状态
EOF
}

# 解析命令行参数
parse_args() {
    local platform=""
    local cmd=""
    local args=()

    # 如果没有参数，使用默认值
    if [[ $# -eq 0 ]]; then
        echo "kimi install"
        return
    fi

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case "$1" in
            kimi|codex)
                if [[ -z "$platform" ]]; then
                    platform="$1"
                else
                    args+=("$1")
                fi
                shift
                ;;
            install|i|update|u|uninstall|remove|rm|status|s|check)
                if [[ -z "$cmd" ]]; then
                    cmd="$1"
                else
                    args+=("$1")
                fi
                shift
                ;;
            -f|--force|-h|--help)
                args+=("$1")
                shift
                ;;
            *)
                # 如果 platform 和 cmd 都还没有设置，这是一个无效的平台/命令
                if [[ -z "$platform" && -z "$cmd" ]]; then
                    echo "INVALID_COMMAND"
                    return
                fi
                args+=("$1")
                shift
                ;;
        esac
    done

    # 设置默认值
    platform="${platform:-kimi}"
    cmd="${cmd:-install}"

    # 输出解析结果
    if [[ ${#args[@]} -gt 0 ]]; then
        echo "$platform $cmd ${args[*]}"
    else
        echo "$platform $cmd"
    fi
}

# 主函数
main() {
    # 解析参数
    local parsed
    parsed=$(parse_args "$@")
    
    # 检查无效命令
    if [[ "$parsed" == "INVALID_COMMAND" ]]; then
        error "未知命令: $1"
        usage
        exit 1
    fi
    
    local platform
    local cmd
    platform=$(echo "$parsed" | awk '{print $1}')
    cmd=$(echo "$parsed" | awk '{print $2}')
    local args=($(echo "$parsed" | cut -d' ' -f3-))

    # 初始化路径
    init_paths "$platform"

    case "$cmd" in
        install|i)
            if [[ ${#args[@]} -gt 0 ]]; then
                cmd_install "${args[@]}"
            else
                cmd_install
            fi
            ;;
        update|u)
            cmd_update
            ;;
        uninstall|remove|rm)
            if [[ ${#args[@]} -gt 0 ]]; then
                cmd_uninstall "${args[@]}"
            else
                cmd_uninstall
            fi
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

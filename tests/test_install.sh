#!/usr/bin/env bash
#
# install.sh 测试脚本
# TDD - 红阶段：编写失败测试
#

set -euo pipefail

# 测试框架
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 测试目录
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${TEST_DIR}/.." && pwd)"
FAKE_HOME="${PROJECT_ROOT}/.test_home_$$"
INSTALL_SCRIPT="${PROJECT_ROOT}/scripts/install.sh"

# 设置/清理
test_setup() {
    export HOME="$FAKE_HOME"
    export INSTALL_DIR="${FAKE_HOME}/.kimi"
    export SKILLS_DIR="${INSTALL_DIR}/skills"
    export AGENT_DIR="${INSTALL_DIR}/agents/superpower"
    
    # 清理
    rm -rf "$FAKE_HOME"
    mkdir -p "$FAKE_HOME"
}

test_teardown() {
    rm -rf "$FAKE_HOME"
    unset HOME INSTALL_DIR SKILLS_DIR AGENT_DIR
}

# 测试断言
assert_equals() {
    local expected="$1"
    local actual="$2"
    local msg="${3:-}"
    
    ((TESTS_RUN++))
    
    if [[ "$expected" == "$actual" ]]; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} ${msg:-assert_equals}"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} ${msg:-assert_equals}"
        echo "  Expected: $expected"
        echo "  Actual:   $actual"
        return 1
    fi
}

assert_true() {
    local condition="$1"
    local msg="${2:-}"
    
    ((TESTS_RUN++))
    
    if eval "$condition"; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} ${msg:-assert_true}"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} ${msg:-assert_true}: $condition"
        return 1
    fi
}

assert_false() {
    local condition="$1"
    local msg="${2:-}"
    
    ((TESTS_RUN++))
    
    if ! eval "$condition"; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} ${msg:-assert_false}"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} ${msg:-assert_false}: $condition"
        return 1
    fi
}

# ===== 测试用例 =====

# 测试1: install 命令应该创建目录
test_install_creates_directories() {
    echo -e "\n${BLUE}Test:${NC} install 创建目录"
    test_setup
    
    # 执行安装
    bash "$INSTALL_SCRIPT" install -f
    
    # 验证目录创建
    assert_true "[[ -d '$SKILLS_DIR' ]]" "Skills 目录已创建"
    assert_true "[[ -d '$AGENT_DIR' ]]" "Agent 目录已创建"
    
    test_teardown
}

# 测试2: install 应该复制所有 skills
test_install_copies_all_skills() {
    echo -e "\n${BLUE}Test:${NC} install 复制所有 skills"
    test_setup
    
    bash "$INSTALL_SCRIPT" install -f
    
    # 统计源 skills 数量
    local source_count
    source_count=$(find "${PROJECT_ROOT}/kimi/skills" -name "SKILL.md" | wc -l)
    
    # 统计安装后的 skills 数量
    local installed_count
    installed_count=$(find "$SKILLS_DIR" -name "SKILL.md" | wc -l)
    
    assert_equals "$source_count" "$installed_count" "Skills 数量匹配"
    
    # 验证特定 skill 存在
    assert_true "[[ -f '$SKILLS_DIR/dev-using-skills/SKILL.md' ]]" "dev-using-skills 存在"
    assert_true "[[ -f '$SKILLS_DIR/dev-tdd/SKILL.md' ]]" "dev-tdd 存在"
    
    test_teardown
}

# 测试3: install 应该复制 agent 配置
test_install_copies_agent_config() {
    echo -e "\n${BLUE}Test:${NC} install 复制 agent 配置"
    test_setup
    
    bash "$INSTALL_SCRIPT" install -f
    
    assert_true "[[ -f '$AGENT_DIR/agent.yaml' ]]" "agent.yaml 存在"
    assert_true "[[ -f '$AGENT_DIR/system.md' ]]" "system.md 存在"
    
    test_teardown
}

# 测试4: install 应该创建启动脚本
test_install_creates_wrapper() {
    echo -e "\n${BLUE}Test:${NC} install 创建启动脚本"
    test_setup
    
    bash "$INSTALL_SCRIPT" install -f
    
    assert_true "[[ -f '${PROJECT_ROOT}/kimi-superpower' ]]" "启动脚本已创建"
    assert_true "[[ -x '${PROJECT_ROOT}/kimi-superpower' ]]" "启动脚本可执行"
    
    test_teardown
}

# 测试5: status 应该显示未安装状态
test_status_shows_not_installed() {
    echo -e "\n${BLUE}Test:${NC} status 显示未安装"
    test_setup
    
    local output
    output=$(bash "$INSTALL_SCRIPT" status 2>&1)
    
    assert_true "[[ '$output' == *'未安装'* ]]" "status 显示未安装"
    
    test_teardown
}

# 测试6: status 应该显示已安装状态
test_status_shows_installed() {
    echo -e "\n${BLUE}Test:${NC} status 显示已安装"
    test_setup
    
    bash "$INSTALL_SCRIPT" install -f
    local output
    output=$(bash "$INSTALL_SCRIPT" status 2>&1)
    
    assert_false "[[ '$output' == *'未安装'* ]]" "status 不显示未安装"
    assert_true "[[ '$output' == *'安装完成'* || '$output' == *'已安装'* ]]" "status 显示已安装"
    
    test_teardown
}

# 测试7: update 应该更新已存在的配置
test_update_updates_existing() {
    echo -e "\n${BLUE}Test:${NC} update 更新已存在的配置"
    test_setup
    
    # 先安装
    bash "$INSTALL_SCRIPT" install -f
    
    # 修改一个文件模拟更新
    echo "# old content" > "$SKILLS_DIR/dev-using-skills/SKILL.md"
    
    # 执行更新
    bash "$INSTALL_SCRIPT" update
    
    # 验证文件被更新（不应该包含 old content）
    assert_false "grep -q 'old content' '$SKILLS_DIR/dev-using-skills/SKILL.md'" "文件已被更新"
    
    test_teardown
}

# 测试8: update 应该在没有安装时报错
test_update_fails_when_not_installed() {
    echo -e "\n${BLUE}Test:${NC} update 未安装时报错"
    test_setup
    
    local exit_code=0
    bash "$INSTALL_SCRIPT" update 2>&1 || exit_code=$?
    
    assert_equals "1" "$exit_code" "update 返回错误码"
    
    test_teardown
}

# 测试9: uninstall 应该删除配置
test_uninstall_removes_config() {
    echo -e "\n${BLUE}Test:${NC} uninstall 删除配置"
    test_setup
    
    # 先安装
    bash "$INSTALL_SCRIPT" install -f
    
    # 卸载
    bash "$INSTALL_SCRIPT" uninstall -f
    
    assert_false "[[ -d '$INSTALL_DIR' ]]" "配置目录已删除"
    
    test_teardown
}

# 测试10: uninstall 应该删除启动脚本
test_uninstall_removes_wrapper() {
    echo -e "\n${BLUE}Test:${NC} uninstall 删除启动脚本"
    test_setup
    
    bash "$INSTALL_SCRIPT" install -f
    bash "$INSTALL_SCRIPT" uninstall -f
    
    assert_false "[[ -f '${PROJECT_ROOT}/kimi-superpower' ]]" "启动脚本已删除"
    
    test_teardown
}

# 测试11: 无效命令应该报错
test_invalid_command_fails() {
    echo -e "\n${BLUE}Test:${NC} 无效命令报错"
    test_setup
    
    local exit_code=0
    bash "$INSTALL_SCRIPT" invalid_command 2>&1 || exit_code=$?
    
    assert_equals "1" "$exit_code" "无效命令返回错误码"
    
    test_teardown
}

# 测试12: install -f 应该覆盖现有配置
test_install_force_overwrites() {
    echo -e "\n${BLUE}Test:${NC} install -f 覆盖现有配置"
    test_setup
    
    # 第一次安装
    bash "$INSTALL_SCRIPT" install -f
    local first_mtime
    first_mtime=$(stat -c %Y "$AGENT_DIR/agent.yaml" 2>/dev/null || stat -f %m "$AGENT_DIR/agent.yaml")
    
    # 等待一秒确保时间戳变化
    sleep 1
    
    # 强制重新安装
    bash "$INSTALL_SCRIPT" install -f
    local second_mtime
    second_mtime=$(stat -c %Y "$AGENT_DIR/agent.yaml" 2>/dev/null || stat -f %m "$AGENT_DIR/agent.yaml")
    
    assert_true "[[ $second_mtime -ge $first_mtime ]]" "文件已被覆盖"
    
    test_teardown
}

# 运行所有测试
run_all_tests() {
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}  Running TDD Tests for install.sh${NC}"
    echo -e "${YELLOW}========================================${NC}"
    
    test_install_creates_directories
    test_install_copies_all_skills
    test_install_copies_agent_config
    test_install_creates_wrapper
    test_status_shows_not_installed
    test_status_shows_installed
    test_update_updates_existing
    test_update_fails_when_not_installed
    test_uninstall_removes_config
    test_uninstall_removes_wrapper
    test_invalid_command_fails
    test_install_force_overwrites
    
    echo -e "\n${YELLOW}========================================${NC}"
    echo -e "${YELLOW}  Test Summary${NC}"
    echo -e "${YELLOW}========================================${NC}"
    echo -e "Total:  $TESTS_RUN"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "\n${GREEN}All tests passed!${NC}"
        return 0
    else
        echo -e "\n${RED}Some tests failed!${NC}"
        return 1
    fi
}

# 主函数
main() {
    # 检查源文件是否存在
    if [[ ! -f "$INSTALL_SCRIPT" ]]; then
        echo -e "${RED}Error: install.sh not found at $INSTALL_SCRIPT${NC}"
        exit 1
    fi
    
    run_all_tests
}

main "$@"

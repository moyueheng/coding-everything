# Configuration Manager Makefile
# 支持 Kimi 和 Codex 平台

.PHONY: help install install-force update uninstall status test clean
.PHONY: install-codex install-codex-force update-codex uninstall-codex status-codex

# 默认目标
help:
	@echo "Configuration Manager - 常用命令"
	@echo ""
	@echo "Kimi 命令:"
	@echo "  make install          安装配置到 ~/.kimi/"
	@echo "  make install-force    强制安装 kimi（覆盖现有配置）"
	@echo "  make update           更新已安装的 kimi 配置"
	@echo "  make uninstall        卸载 kimi 配置"
	@echo "  make status           查看 kimi 安装状态"
	@echo "  make run              安装并启动 kimi-superpower"
	@echo ""
	@echo "Codex 命令:"
	@echo "  make install-codex        安装 skills 到 ~/.agents/skills/"
	@echo "  make install-codex-force  强制安装 codex（覆盖现有配置）"
	@echo "  make update-codex         更新已安装的 codex 配置"
	@echo "  make uninstall-codex      卸载 codex 配置"
	@echo "  make status-codex         查看 codex 安装状态"
	@echo ""
	@echo "其他命令:"
	@echo "  make test             运行测试"
	@echo "  make clean            清理测试文件"

# ==================== Kimi 命令 ====================

# 安装配置
install:
	@./scripts/install.sh kimi install

# 强制安装
install-force:
	@./scripts/install.sh kimi install -f

# 更新配置
update:
	@./scripts/install.sh kimi update

# 卸载配置
uninstall:
	@./scripts/install.sh kimi uninstall

# 查看状态
status:
	@./scripts/install.sh kimi status

# 运行 kimi
run: install
	@./kimi-superpower

# ==================== Codex 命令 ====================

# 安装 codex skills
install-codex:
	@./scripts/install.sh codex install

# 强制安装 codex
install-codex-force:
	@./scripts/install.sh codex install -f

# 更新 codex 配置
update-codex:
	@./scripts/install.sh codex update

# 卸载 codex 配置
uninstall-codex:
	@./scripts/install.sh codex uninstall

# 查看 codex 状态
status-codex:
	@./scripts/install.sh codex status

# ==================== 通用命令 ====================

# 运行测试
test:
	@./tests/test_install.sh

# 清理测试生成的文件
clean:
	@rm -rf .test_home_* kimi-superpower
	@echo "清理完成"

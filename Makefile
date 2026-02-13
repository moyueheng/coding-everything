# Kimi Configuration Makefile
# 常用命令快捷方式

.PHONY: help install install-force update uninstall status test clean

# 默认目标
help:
	@echo "Kimi Configuration - 常用命令"
	@echo ""
	@echo "安装命令:"
	@echo "  make install        安装配置到 ~/.kimi/"
	@echo "  make install-force  强制安装（覆盖现有配置）"
	@echo "  make update         更新已安装的配置"
	@echo "  make uninstall      卸载配置"
	@echo ""
	@echo "查看命令:"
	@echo "  make status         查看安装状态"
	@echo "  make test           运行测试"
	@echo ""
	@echo "其他命令:"
	@echo "  make clean          清理测试文件"
	@echo "  make run            安装并启动 kimi-superpower"

# 安装配置
install:
	@./scripts/install.sh install

# 强制安装
install-force:
	@./scripts/install.sh install -f

# 更新配置
update:
	@./scripts/install.sh update

# 卸载配置
uninstall:
	@./scripts/install.sh uninstall

# 查看状态
status:
	@./scripts/install.sh status

# 运行测试
test:
	@./tests/test_install.sh

# 清理测试生成的文件
clean:
	@rm -rf .test_home_* kimi-superpower
	@echo "清理完成"

# 安装并运行
run: install
	@./kimi-superpower

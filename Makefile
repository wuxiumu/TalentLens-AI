# ============================================
# Resume CLI - Makefile
# ============================================
# 用法: make <target>
# ============================================

# Python 自动检测：优先 .venv，其次系统 python3
VENV_PYTHON := .venv/bin/python3
SYSTEM_PYTHON := $(shell command -v python3 2>/dev/null)

ifeq ($(shell test -x $(VENV_PYTHON) && echo yes),yes)
	PYTHON := $(VENV_PYTHON)
else
	PYTHON := $(SYSTEM_PYTHON)
endif

CLI := ./resume-cli
EXAMPLES_DIR := examples

# ---- 基础命令 ----

.PHONY: help
help: ## 显示帮助信息
	@echo "Resume CLI - 可用命令:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "当前 Python: $(PYTHON)"

.PHONY: install
install: ## 创建虚拟环境并安装依赖
	@echo "📦 正在安装依赖..."
	@if command -v uv >/dev/null 2>&1; then \
		echo "使用 uv 创建虚拟环境..."; \
		uv venv .venv --python 3.12 2>/dev/null || uv venv .venv; \
		uv pip install -r requirements.txt --python .venv/bin/python; \
	else \
		echo "使用 pip 创建虚拟环境..."; \
		$(PYTHON) -m venv .venv; \
		.venv/bin/pip install -r requirements.txt; \
	fi
	@echo "✅ 安装完成！使用 ./resume-cli 运行"

.PHONY: run
run: ## 显示 CLI 帮助
	$(CLI) --help

# ---- 示例命令 ----

.PHONY: demo-parse
demo-parse: ## 演示: 解析 PDF 简历
	$(CLI) parse $(EXAMPLES_DIR)/resume.pdf

.PHONY: demo-extract
demo-extract: ## 演示: AI 提取简历信息（Mock 模式）
	$(CLI) extract $(EXAMPLES_DIR)/resume.pdf --mock

.PHONY: demo-score
demo-score: ## 演示: JD 匹配评分（Mock 模式）
	$(CLI) score $(EXAMPLES_DIR)/resume.pdf --jd $(EXAMPLES_DIR)/jd.txt --mock

.PHONY: demo-all
demo-all: demo-parse demo-extract demo-score ## 演示全部命令

# ---- 测试 ----

.PHONY: smoke
smoke: ## 冒烟：不调用真实 API（version / parse / extract --mock / score --mock）
	$(CLI) --version
	$(CLI) parse $(EXAMPLES_DIR)/resume.pdf
	$(CLI) extract $(EXAMPLES_DIR)/resume.pdf --mock
	$(CLI) score $(EXAMPLES_DIR)/resume.pdf --jd $(EXAMPLES_DIR)/jd.txt --mock
	@echo "✅ 冒烟通过（未调用真实 API）"

.PHONY: test
test: ## 运行测试
	$(PYTHON) -m pytest tests/ -v

# ---- Docker ----

.PHONY: docker-build
docker-build: ## 构建 Docker 镜像
	docker build -t resume-cli .

.PHONY: docker-demo
docker-demo: ## Docker 演示（Mock 模式）
	docker run --rm resume-cli extract /app/examples/resume.pdf --mock

# ---- 工具 ----

.PHONY: lint
lint: ## 代码风格检查
	$(PYTHON) -m py_compile resume_cli/main.py
	@echo "✅ 语法检查通过"

.PHONY: clean
clean: ## 清理临时文件
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache dist build *.egg-info
	@echo "✅ 清理完成"

.PHONY: gen-test-files
gen-test-files: ## 生成测试用 PDF 和 JD 文件
	$(PYTHON) examples/create_test_files.py

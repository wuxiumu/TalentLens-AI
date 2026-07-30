# ============================================
# Resume CLI Dockerfile
# ============================================
# 构建: docker build -t resume-cli .
# 运行: docker run --rm -v $(pwd)/examples:/app/examples resume-cli parse /app/examples/resume.pdf
# ============================================

FROM python:3.12-slim

LABEL maintainer="resume-cli"
LABEL description="AI 简历解析 CLI 工具"

# 设置工作目录
WORKDIR /app

# 安装依赖（利用 Docker 缓存层）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY resume_cli/ resume_cli/
COPY resume-cli .
RUN chmod +x resume-cli

# 创建非 root 用户
RUN useradd -m -s /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# 默认显示帮助
ENTRYPOINT ["./resume-cli"]
CMD ["--help"]

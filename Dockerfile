# ============================================
# Resume CLI Dockerfile
# ============================================
# 构建: docker build -t resume-cli .
# Mock: docker run --rm resume-cli extract /app/examples/resume.pdf --mock
# 真实调用: docker run --rm --env-file .env -v "$PWD:/data:ro" resume-cli score /data/resume.pdf --jd /data/jd.txt
# ============================================

FROM python:3.12-slim

LABEL maintainer="resume-cli"
LABEL description="AI 简历解析 CLI 工具"

# 设置工作目录
WORKDIR /app

# 安装依赖（利用 Docker 缓存层）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码与示例简历（Mock / 冒烟不依赖宿主机挂载）
COPY resume_cli/ resume_cli/
COPY resume-cli .
COPY examples/ examples/
RUN chmod +x resume-cli

# 创建非 root 用户
RUN useradd -m -s /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# 默认显示帮助
ENTRYPOINT ["./resume-cli"]
CMD ["--help"]

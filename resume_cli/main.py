"""
Resume CLI - AI 简历解析命令行工具

主入口文件，注册所有子命令。
"""

import typer

from resume_cli import __version__

# 创建主应用
app = typer.Typer(
    name="resume-cli",
    help="AI 简历解析 CLI 工具 —— 支持 PDF 解析、信息提取、JD 匹配评分",
    add_completion=False,
    invoke_without_command=True,
)


def version_callback(value: bool):
    """版本回调"""
    if value:
        typer.echo(f"resume-cli v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="显示版本号",
        callback=version_callback,
        is_eager=True,
    ),
):
    """AI 简历解析 CLI 工具"""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


# 导入并注册命令
from resume_cli.commands.parse import parse_pdf  # noqa: E402
from resume_cli.commands.extract import extract_info  # noqa: E402
from resume_cli.commands.score import score_resume  # noqa: E402

app.command(name="parse", help="解析 PDF 简历，提取文本内容")(parse_pdf)
app.command(name="extract", help="调用 AI 从简历中提取结构化信息")(extract_info)
app.command(name="score", help="简历与 JD 匹配评分")(score_resume)


def cli():
    """CLI 入口点"""
    app()


if __name__ == "__main__":
    cli()

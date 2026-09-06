import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from quiver_to_image.exceptions import (
    CompilationError,
    DockerDaemonNotRunningError,
    DockerImageNotFoundError,
    DockerNotAvailableError,
)

DOCKER_IMAGE = "quiver-render"
TEX_TEMPLATE = r"""\documentclass[tikz,border=2pt]{{standalone}}
\usepackage{{amsmath}}
\usepackage{{quiver}}
\begin{{document}}
{code}
\end{{document}}"""


def strip_delimiters(code: str) -> str:
    lines = code.splitlines()
    result = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("\\["):
            line = line[line.index("\\[") + 2 :]
        if stripped.endswith("\\]"):
            line = line[: line.rindex("\\]")]
        result.append(line)

    return "\n".join(result).strip()


def check_docker() -> None:
    if not shutil.which("docker"):
        raise DockerNotAvailableError(
            "Docker not found. Installation options:\n"
            "  1) Docker Desktop for Windows (enable WSL 2 backend)\n"
            "  2) sudo apt install docker-ce docker-ce-cli containerd.io"
        )

    result = subprocess.run(
        ["docker", "info"],
        capture_output=True,
    )
    if result.returncode != 0:
        raise DockerDaemonNotRunningError(
            "Docker found but daemon is not running. Start it with:\n"
            "  sudo service docker start"
        )

    result = subprocess.run(
        ["docker", "image", "inspect", DOCKER_IMAGE],
        capture_output=True,
    )
    if result.returncode != 0:
        raise DockerImageNotFoundError(
            f"Image {DOCKER_IMAGE} not found. "
            f"Build it first: docker build -t {DOCKER_IMAGE} ."
        )


def generate_tex(code: str, name: str) -> str:
    return TEX_TEMPLATE.format(code=code)


def compile_in_docker(tmpdir: Path, name: str) -> None:
    script = (
        "set -e\n"
        f"pdflatex -interaction=nonstopmode -halt-on-error '{name}.tex' > pdflatex.log 2>&1 || "
        f"{{ cat pdflatex.log; exit 1; }}\n"
        f"pdf2svg '{name}.pdf' '{name}.svg'\n"
        f"pdftoppm -png -r 300 -singlefile '{name}.pdf' '{name}'"
    )

    result = subprocess.run(
        [
            "docker", "run", "--rm",
            "-v", f"{tmpdir}:/data",
            "-w", "/data",
            DOCKER_IMAGE,
            "bash", "-c", script,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise CompilationError(
            f"Compilation error:\n{result.stderr}\n{result.stdout}"
        )


def copy_results(tmpdir: Path, outdir: Path, name: str) -> tuple[Path, Path]:
    outdir.mkdir(parents=True, exist_ok=True)

    svg_src = tmpdir / f"{name}.svg"
    png_src = tmpdir / f"{name}.png"
    svg_dst = outdir / f"{name}.svg"
    png_dst = outdir / f"{name}.png"

    if not svg_src.exists():
        raise CompilationError(f"SVG file not created: {svg_src}")
    if not png_src.exists():
        raise CompilationError(f"PNG file not created: {png_src}")

    shutil.copy2(svg_src, svg_dst)
    shutil.copy2(png_src, png_dst)

    return svg_dst, png_dst


def render(
    code: str,
    name: str,
    outdir: Path,
) -> tuple[Path, Path]:
    code = strip_delimiters(code)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        tex_path = tmpdir / f"{name}.tex"
        tex_path.write_text(generate_tex(code, name))

        compile_in_docker(tmpdir, name)

        return copy_results(tmpdir, outdir, name)

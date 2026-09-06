from datetime import datetime
from pathlib import Path

import typer

from quiver_to_image.clipboard import get_clipboard, get_stdin
from quiver_to_image.compiler import check_docker, render
from quiver_to_image.exceptions import QuiverError

app = typer.Typer(help="Convert quiver tikz-cd diagrams to SVG and PNG")


@app.command()
def main(
    name: str = typer.Argument(
        None,
        help="Output filename (default: diagram-<timestamp>)",
    ),
    output_dir: Path = typer.Option(
        "~/quiver-diagrams",
        "--output", "-o",
        help="Output directory",
    ),
    no_clipboard: bool = typer.Option(
        False,
        "--no-clipboard", "-n",
        help="Read LaTeX from stdin instead of clipboard",
    ),
) -> None:
    if name is None:
        name = f"diagram-{datetime.now():%Y%m%d-%H%M%S}"

    output_dir = output_dir.expanduser()

    try:
        check_docker()

        if no_clipboard:
            code = get_stdin()
        else:
            code = get_clipboard()

        svg_path, png_path = render(code, name, output_dir)

        typer.echo("Done:")
        typer.echo(f"  SVG: {svg_path}")
        typer.echo(f"  PNG: {png_path}")

    except QuiverError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

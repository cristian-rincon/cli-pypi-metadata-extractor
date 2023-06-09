from pathlib import Path

import typer
from rich import print
from typing_extensions import Annotated

from extractor.core import extract_data, save_data
from extractor.render import RequirementsFormat

app = typer.Typer()
VERSION = "0.2.4"


@app.command(name="version")
def version():
    return print(VERSION)


@app.command(name="extract")
def main(
    source_path: Annotated[
        Path,
        typer.Option(
            exists=True,
            file_okay=True,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
            prompt=True,
            help="Requirements files paths. Can be a single file, or a folder",
        ),
    ] = "",
    output: Annotated[
        Path,
        typer.Option(
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            prompt=True,
            help="Path to store the data",
        ),
    ] = "",
    format: Annotated[
        RequirementsFormat,
        typer.Option(prompt=True, help="Incoming requirements format."),
    ] = RequirementsFormat.pip_freeze,
):
    data = extract_data(source_path, format)
    save_data(data, output)


if __name__ == "__main__":
    app()

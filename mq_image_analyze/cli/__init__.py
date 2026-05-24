import typer

from mq_image_analyze.cli.analyze import analyze

app = typer.Typer(
    name="mq-image",
    help="Visual reasoning and image intelligence.",
    no_args_is_help=True,
)


@app.callback()
def _main() -> None:
    pass


app.command("analyze")(analyze)

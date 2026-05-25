import typer

from mq_image_analyze.cli.analyze import analyze
from mq_image_analyze.cli.analyze_ui import analyze_ui_cmd
from mq_image_analyze.cli.compare import compare
from mq_image_analyze.cli.doctor import doctor
from mq_image_analyze.cli.serve import serve

_VERSION = (Path := __import__("pathlib").Path)(__file__).parents[2].joinpath("VERSION").read_text().strip()

app = typer.Typer(
    name="mq-image",
    help="Visual reasoning and image intelligence.",
    no_args_is_help=True,
)


@app.callback(invoke_without_command=True)
def _main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-V", is_eager=True, help="Show version and exit"),
) -> None:
    if version:
        typer.echo(f"mq-image {_VERSION}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


app.command("analyze")(analyze)
app.command("analyze-ui")(analyze_ui_cmd)
app.command("compare")(compare)
app.command("doctor")(doctor)
app.command("serve")(serve)

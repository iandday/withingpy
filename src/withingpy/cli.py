import secrets
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunsplit

import typer

from withingpy.models import WithingsConfig
from withingpy.withings_api_client import WithingsAPIClient


app = typer.Typer(help="Withings Public API CLI Tool")


@app.command()
def configure(
    base_url: str = typer.Option(default="https://wbsapi.withings.net", prompt=True, help="Withings API base URL"),
    client_id: str = typer.Option(..., prompt=True, help="Withings client ID"),
    client_secret: str = typer.Option(..., prompt=True, hide_input=True, help="Withings client secret"),
    config_path: Path = typer.Option(default="withings_config.json", help="Path to the config file"),
):
    """
    Populate and save WithingsConfig to a configuration file
    """
    config = WithingsConfig(base_url=base_url, client_id=client_id, client_secret=client_secret, access_token=None, refresh_token=None)
    config_path.write_text(config.model_dump_json(indent=2))
    typer.echo(f"Config written to {config_path.resolve()}")


@app.command()
def authorize(config_path: Path = typer.Option(default="withings_config.json", help="Path to the config file")):
    """
    Authorize the app with Withings API
    """
    config = WithingsConfig.model_validate_json(config_path.read_text())
    client = WithingsAPIClient(config)
    state = secrets.token_hex(16)
    params = {
        "response_type": "code",
        "client_id": config.client_id,
        "scope": "user.metrics,user.activity",
        "redirect_uri": "http://localhost",
        "state": state,
    }
    query = urlencode(query=params, doseq=True)
    link = urlunsplit(("https", "account.withings.com", "oauth2_user/authorize2", query, ""))

    typer.echo(f"Launching authorization link, copy the URL after authorization")
    typer.launch(link)
    url = typer.prompt("Enter the URL you were redirected to after authorization")
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    if query_params["state"][0] != state:
        typer.echo("State mismatch, possible CSRF attack or invalid state.")
        raise typer.Exit(code=1)
    else:
        code = query_params["code"][0]
        typer.echo(f"Authorization code received: {code}")
        access_token_response = client.get_access_token(code, "http://localhost")
        config.access_token = access_token_response["body"]["access_token"]
        config.refresh_token = access_token_response["body"]["refresh_token"]
        config_path.write_text(config.model_dump_json(indent=2))


if __name__ == "__main__":
    app()

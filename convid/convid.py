import json
import os
import sys
import traceback

import click
import ffmpeg

from convid import version, descriptive_name


# useful aliases
echo = click.secho


def vecho(message: str, verbose: bool) -> None:
    if verbose:
        click.secho(message, fg="magenta")


def get_convid_config_dir_file() -> str:
    if os.name == "nt":
        home_dir = os.environ.get("USERPROFILE", "C:\\Users")
    else:
        home_dir = os.environ.get("HOME", "/home")

    convid_config_dir = os.path.join(home_dir, ".config")
    convid_config_file = os.path.join(convid_config_dir, "convid.json")
    return convid_config_dir, convid_config_file


def get_convid_configs() -> dict:
    convid_config_dir, convid_config_file = get_convid_config_dir_file()
    try:
        with open(convid_config_file) as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        # Create config directory if it doesn't exist
        if not os.path.isdir(convid_config_dir):
            os.mkdir(convid_config_dir)
        # Create an empty file
        config = {}
        out_conf_file = open(convid_config_file, "w")
        json.dump(out_conf_file, config)
        out_conf_file.close()

    return config


def configure_ffmpeg(ctx, _, value):
    if not value or ctx.resilient_parsing:
        return

    config = {"ffmpeg": value}
    _, convid_config_file = get_convid_config_dir_file()
    out_conf_file = open(convid_config_file, "w")
    json.dump(config, out_conf_file)
    out_conf_file.close()
    ctx.exit()


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("video")
@click.argument("ext")
@click.option(
    "-rm", "--remove", is_flag=True, help="Remove original file after conversion."
)
@click.option("-v", "--verbose", is_flag=True, help="Verbose output.")
@click.option(
    "--ffmpeg",
    "_ffmpeg",
    type=click.Path(exists=True, dir_okay=False, executable=True),
    is_eager=True,
    callback=configure_ffmpeg,
    expose_value=True,
    help="Configure ffmpeg executable path",
)
@click.version_option(version, "--version", prog_name=descriptive_name)
def convid(video: str, ext: str, remove: bool, verbose: bool, _ffmpeg: str) -> None:
    """
    \b
    convid - convert your videos
    \b
    VIDEO: Video file to convert
    EXT  : New video extension (e.g.: mp4)
    \f
    :param str video: video file to convert
    :param str ext: new video extension
    :param bool remove: remove original file
    :param bool verbose: print verbose output
    :return: None
    """
    echo("[!] Convid is starting", fg="blue")
    # Options and argument recap
    vecho(f"[*] Video: {video}", verbose)
    vecho(f"[*] Extension: {ext}", verbose)
    vecho(f"[*] Remove: {remove}", verbose)

    # Get absolute path
    vecho("[*] Start video file checks", verbose)
    f = os.path.abspath(video)
    vecho(f"[*] Video absolute path: {f}", verbose)

    # Check video file
    vecho(f"[*] Check if video {video} exists", verbose)
    if not os.path.exists(f):
        echo(f"[-] Error: file <{video}> does not exist", fg="red", bold=True)
        sys.exit(1)

    vecho(f"[*] Check if video {video} is file", verbose)
    if not os.path.isfile(f):
        echo(f"[-] Error: <{video}> is not a file", fg="red", bold=True)
        sys.exit(1)

    vecho(f"[*] Check if video {video} is readable", verbose)
    if not os.access(f, os.R_OK):
        echo(f"[-] Error: file <{video}> is not readable", fg="red", bold=True)
        sys.exit(1)

    # Check extension and add initial . if missing
    vecho(f"[*] Cleaning extension", verbose)
    if not ext.startswith("."):
        ext = f".{ext}"
    name, old_ext = os.path.splitext(f)
    vecho(f"[*] Checking extensions new {ext} and old {old_ext}", verbose)
    if old_ext == ext:
        vecho(
            "[*] New extension is equal to old extension. Ask user to continue", verbose
        )
        proceed = click.confirm(
            click.style(
                "[!] New extension is equal to old extension. Do you still want to proceed?",
                fg="bright_yellow",
            ),
            default=False,
            show_default=True,
        )
        vecho(f"[*] User decided to {proceed}", verbose)
        if not proceed:
            raise click.Abort()

    # Generate new file name
    vecho(f"[*] Elaborate new name", verbose)
    new_file = f"{name}{ext}"
    vecho(f"[*] New file name: {new_file}", verbose)

    # Try to convert video
    echo(
        "[!] Video conversion is starting, it will take a while, please be patience",
        fg="yellow",
    )
    try:
        vecho("[*] Convertion is starting, see ya!", verbose)
        ffmpeg_executable = get_convid_configs().get("ffmpeg", "ffmpeg")
        ffmpeg.input(f).output(new_file).run(
            cmd=ffmpeg_executable, quiet=False if verbose else True
        )
        echo(
            f"[+] Successful conversion! Check your new file: {new_file}",
            fg="green",
            bold=True,
        )
    except AttributeError as ex:
        vecho(f"[!!] An error occurred:", verbose)
        vecho(traceback.format_exc(), verbose)
        echo(
            f"[-] Something went wrong during the video conversion: {ex}\nAre you sure to have ffmpeg installed or correctly configured?",
            fg="red",
            bold=True,
        )
        sys.exit(1)
    except Exception as ex:
        vecho(f"[!!] An error occurred:", verbose)
        vecho(traceback.format_exc(), verbose)
        echo(
            f"[-] Something went wrong during the video conversion: {ex}",
            fg="red",
            bold=True,
        )
        sys.exit(1)

    # Check if old video should be remove
    vecho(f"[*] Should old video be removed? {'YES' if remove else 'NO'}", verbose)
    if remove:
        try:
            os.remove(f)
            echo("[+] Old video successfully removed", fg="green")
        except Exception as ex:
            vecho(f"[*] An error occurred while removing old file:", verbose)
            vecho(traceback.format_exc(), verbose)
            echo(f"[-] Something went wrong while removing old file: {ex}", fg="red")
            sys.exit(1)

    vecho("[*] Thank you and have a nice day :)", verbose)
    sys.exit(0)


if __name__ == "__main__":
    convid()

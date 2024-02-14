import gi
gi.require_version("Gtk", "4.0")
from gi.repository import GLib
from typing import List
from collections.abc import Callable
from pathlib import Path

import yt_dlp
import yt_dlp.options
import threading, json, time

create_parser = yt_dlp.options.create_parser

def parse_patched_options(opts):
    """
    from yt-dlp/devscripts/cli_to_api.py
    """
    patched_parser = create_parser()
    patched_parser.defaults.update({
        "ignoreerrors": False,
        "retries": 0,
        "fragment_retries": 0,
        "extract_flat": False,
        "concat_playlist": "never",
    })
    yt_dlp.options.create_parser = lambda: patched_parser
    try:
        return yt_dlp.parse_options(opts)
    finally:
        yt_dlp.options.create_parser = create_parser

def ytdl_parse_options(ydl_argv: List[str]):
    """
    let yt_dlp parse and convert arguments to options object
    """
    default_opts = parse_patched_options([]).ydl_opts
    opts = parse_patched_options(ydl_argv).ydl_opts

    diff = {k: v for k, v in opts.items() if default_opts[k] != v}
    if "postprocessors" in diff:
        diff["postprocessors"] = [pp for pp in diff["postprocessors"]
                                  if pp not in default_opts["postprocessors"]]
    return diff


class TaskGetMeta(threading.Thread):
    """
    A threading task for extracting info
    """
    def __init__(self, config: dict, url: str,
                 on_done_callback: Callable[[dict, str], bool]):
        super().__init__()
        self.config = config
        # the target URL
        self.url = url
        # the callback function after meta is retrieved
        self.on_done_cb = on_done_callback
        # yt_dlp options
        if config["additional-options"] is not None:
            self.opts = ytdl_parse_options(config["additional-options"])
        else:
            self.opts = dict()
        # temporary unique ID name
        self.idname = f"pygyt_{time.monotonic_ns():x}" 
        # config download home
        self.opts["paths"] = {"home": f"{config['download-folder']}/{self.idname}"}
        # channel playlist not supported
        self.opts["noplaylist"] = True
        # no yt-dlp built-in progress
        self.opts["noprogress"] = True
        # no yt-dlp log messages
        self.opts["quiet"] = True
        # no video download, just metadata and thumbnail
        self.opts["skip_download"] = True
        # options to download the thumbnail
        self.opts["writethumbnail"] = True
        # save with an unique name instead of "%(title)s.%(ext)s"
        self.opts["outtmpl"] = {"thumbnail": f"{self.idname}.%(ext)s"}
        # png format is all we need
        self.opts["postprocessors"] = [{
            "format": "png",
            "key": "FFmpegThumbnailsConvertor",
            "when": "before_dl"
        }]

    def run(self):
        """
        The activity method of the task
        """
        with yt_dlp.YoutubeDL(self.opts) as ytdl:
            try:
                meta = ytdl.sanitize_info(ytdl.extract_info(self.url, download=True))
            except Exception as err:
                GLib.idle_add(self.on_done_cb, None, str(err))
            else:
                json_file = f"{self.opts['paths']['home']}/{meta['title']}.json"
                # dump meta to info json file
                with open(json_file, "w") as f:
                    json.dump(meta, f)
                try:
                    # title is available now, rename the home folder name
                    new_home = Path(self.opts["paths"]["home"]).rename(
                        f"{self.config['download-folder']}/{meta['title']}")
                    thumbnail_path = new_home.joinpath(f"{self.idname}.png")
                    if (thumbnail_path.exists()):
                        thumbnail_path.rename(new_home.joinpath(f"{meta['title']}.png"))
                except OSError as oserr:
                    GLib.idle_add(self.on_done_cb, None, str(oserr))
                else:
                    GLib.idle_add(self.on_done_cb, meta, "")


class TaskGetFile(threading.Thread):
    """
    A threading task for downloading audio/video file
    """
    def __init__(self, config: dict, url: str,
                 on_progress_callback: Callable[[str, float], None],
                 on_done_callback: Callable[[int, str], bool]):
        super().__init__()
        self.config = config
        # the target URL
        self.url = url
        # the callback function to update progress
        self.on_progress_cb = on_progress_callback
        # the callback function after file is retrieved
        self.on_done_cb = on_done_callback
        # yt_dlp options
        if config["additional-options"] is not None:
            self.opts = ytdl_parse_options(config["additional-options"])
        else:
            self.opts = dict()
        # config download home
        self.opts["paths"] = {"home": config['download-folder']}
        # channel playlist not supported
        self.opts["noplaylist"] = True
        # no yt-dlp built-in progress
        self.opts["noprogress"] = True
        # no yt-dlp log messages
        self.opts["quiet"] = True
        # no color code, we interpret the progress in regular string
        self.opts["color"] = {"stderr": "no_color", "stdout": "no_color"}
        # set downloading progress hook
        self.opts["progress_hooks"] = [self.progress_hook]

    def run(self):
        """
        The activity method of the task
        """
        with yt_dlp.YoutubeDL(self.opts) as ytdl:
            try:
                if "info_json" in self.config:
                    error_code = ytdl.download_with_info_file(self.config["info_json"])
                else:
                    error_code = ytdl.download(self.url)
            except Exception as err:
                GLib.idle_add(self.on_done_cb, -1, str(err))
            else:
                GLib.idle_add(self.on_done_cb, error_code, "")

    def progress_hook(self, pdict: dict):
        """
        progress callback by yt-dlp,
        example fields in the dict:
            '_default_template': ' 26.2% of    3.82MiB at    2.82MiB/s ETA 00:01',
            '_downloaded_bytes_str': '1023.00KiB',
            '_elapsed_str': '00:00:00',
            '_eta_str': '00:01',
            '_percent_str': ' 26.2%',
            '_speed_str': '   2.82MiB/s',
            '_total_bytes_estimate_str': '       N/A',
            '_total_bytes_str': '   3.82MiB',
            'downloaded_bytes': 1047552,
            'elapsed': 0.38120484352111816,
            'eta': 1,
        """
        if "downloading" == pdict["status"]:
            percent_float = float(str.strip(pdict["_percent_str"], " %")) / 100.0
            GLib.idle_add(self.on_progress_cb, pdict["status"], percent_float)
        elif "finished" == pdict["status"]:
            GLib.idle_add(self.on_progress_cb, pdict["status"], 1.0)
        elif "error" == pdict['status']:
            GLib.idle_add(self.on_progress_cb, pdict["status"], 0.0)

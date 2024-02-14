import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject, GLib
from ytdlp_tasks import TaskGetMeta, TaskGetFile
from pathlib import Path
import copy

class DownloadItem(Gtk.Box):
    """
    Layout of the interface for single download item
    """
    __gsignals__ = {
        "meta_ready": (GObject.SignalFlags.RUN_FIRST, None, (str,))
    }

    def __init__(self, config: dict, url: str, **kwargs):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, **kwargs)
        self.config = copy.deepcopy(config)
        self.set_spacing(12)

        # vbox layout for title and download options
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # Title and progress
        self.title = Gtk.Entry()
        self.title.set_text("retrieving metadata ...")
        self.title.set_hexpand(True)
        self.title.set_editable(False)
        self.title.set_has_frame(False)
        vbox.append(self.title)

        # grid layout for all download options
        grid_dlopts = Gtk.Grid()
        grid_dlopts.set_column_spacing(12)
        # Audio only & format
        box_aformat = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.audionly_opts = Gtk.CheckButton.new_with_label(" Audio Only  ")
        box_aformat.append(self.audionly_opts)
        self.aformat = Gtk.StringList()
        self.aformat.append("wav")
        self.aformat_opts = Gtk.DropDown.new(self.aformat, None)
        self.aformat_opts.set_halign(Gtk.Align.END)
        box_aformat.append(self.aformat_opts)
        grid_dlopts.attach(box_aformat, 0, 0, 1, 1)

        grid_dlopts.attach(Gtk.Separator(), 1, 0, 1, 1)

        # Resolution selection
        box_resolution = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label_resolution = Gtk.Label(label="Resolution  ")
        box_resolution.append(label_resolution)
        self.resolutions = Gtk.StringList()
        self.resolutions.append("best")
        self.resolution_opts = Gtk.DropDown.new(self.resolutions, None)
        self.resolution_opts.set_halign(Gtk.Align.END)
        box_resolution.append(self.resolution_opts)
        grid_dlopts.attach(box_resolution, 2, 0, 1, 1)

        grid_dlopts.attach(Gtk.Separator(), 3, 0, 1, 1)

        # Video format selection
        box_vformat = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label_vformat = Gtk.Label(label="Video Format  ")
        box_vformat.append(label_vformat)
        self.vformat = Gtk.StringList()
        self.vformat.append("best")
        self.vformat_opts = Gtk.DropDown.new(self.vformat, None)
        self.vformat_opts.set_halign(Gtk.Align.END)
        box_vformat.append(self.vformat_opts)
        grid_dlopts.attach(box_vformat, 4, 0, 1, 1)

        vbox.append(grid_dlopts)
        self.append(vbox)

        # Thumbnail (read temporary image file)
        self.thumbnail = Gtk.Picture.new_for_filename(str(Path(__file__).parent.joinpath("pygyt_wink.png")))
        self.thumbnail.set_keep_aspect_ratio(True)
        self.append(self.thumbnail)

        # initialize states of controls
        self.audionly_opts.connect("toggled", self.on_toggle_audio_only)
        self.audionly_opts.set_active(True)

        self.task_get_meta = TaskGetMeta(
            config=self.config,
            url=url,
            on_done_callback=self.on_get_meta_task_done
        )
        self.meta = None

    def on_toggle_audio_only(self, check_obj):
        """
        toggle audio only controls on or off
        """
        if check_obj.props.active:
            self.aformat_opts.set_sensitive(True)
            self.resolution_opts.set_sensitive(False)
            self.vformat_opts.set_sensitive(False)
        else:
            self.aformat_opts.set_sensitive(False)
            self.resolution_opts.set_sensitive(True)
            self.vformat_opts.set_sensitive(True)

    def get_meta(self):
        """
        Starting a task thread to extract meta info of the download item.
        Expecting to be called once this item is added to the download list
        and must be called before proceeding audio/video file downloading.
        """
        # don't run the task again if metadata is ready
        if self.meta is not None: return
        # start threading task
        self.task_get_meta.start()
        self.title.set_progress_pulse_step(0.2)
        self.title.progress_pulse()
        self.timer_pulse = GLib.timeout_add(50, self.on_pulse_timeout)

    def on_pulse_timeout(self):
        """
        timer timeout event specifically for the activity of getting meta only
        """
        self.title.progress_pulse()
        # return True for periodically get called
        return True

    def on_get_meta_task_done(self, meta: dict, strerr: str):
        # stop the activity timer
        if self.timer_pulse:
            GLib.source_remove(self.timer_pulse)
            self.timer_pulse = None
            self.title.set_progress_pulse_step(0.0)
        self.title.set_progress_fraction(1.0)

        if meta is None:
            self.set_tooltip_text(f"Error: {strerr}")
            self.title.set_progress_fraction(0.0)
            self.title.set_text("retrieving metadata failed.")
            self.emit("meta_ready", self.title.props.text)
            # TODO: also change the thumbnail to indicate error status
            return

        self.meta = meta
        self.title.set_text(meta["title"])
        self.download_home = f"{self.config['download-folder']}/{meta['title']}"

        formats = meta.get("formats")

        # get all available video resolutions
        resolutionset = {f["resolution"] for f in formats
            if (f.get("video_ext") is not None and f["video_ext"] != "none")
            and (f.get("width") is not None and f["width"] != "none")}
        for r in resolutionset:
            self.resolutions.append(r)

        # get all available video extensions
        videoset = {f["video_ext"] for f in formats
            if f.get("video_ext") is not None and f["video_ext"] != "none"}
        for v in videoset:
            self.vformat.append(v)

        # get all available audio extensions
        audioset = {f["audio_ext"] for f in formats
            if f.get("audio_ext") is not None and f["audio_ext"] != "none"}
        for a in audioset:
            self.aformat.append(a)
        # stop the progress
        self.title.set_progress_fraction(0.0)
        # update the image
        self.thumbnail.set_filename(f"{self.download_home}/{meta['title']}.png")
        # item is ready for download
        self.emit("meta_ready", self.title.props.text)

        # update configuration for task to download file
        self.config["download-folder"] += f"/{meta['title']}"
        # info jaon file should also be available by design
        self.config["info_json"] = self.config["download-folder"] + f"/{meta['title']}.json"
        # update tooltip
        self.set_tooltip_text(f"Ready to download: {self.config['download-folder']}")

    def get_file(self):
        """
        Starting a task thread to download file.
        Expecting to be called after get_meta(), i.e. json file of metadata is ready.
        """
        # ignore if metadata is not ready
        if self.meta is None:
            self.set_tooltip_text("Warning: no metadata, not ready to download")
            return
        # ignore if file is downloaded
        if 1.0 == self.title.props.progress_fraction:
            return

        # append additional audio/video options
        if self.config["additional-options"] is None:
            self.config["additional-options"] = list()
        # Audio/Video options
        if self.audionly_opts.props.active:
            # Audio only options
            self.config["additional-options"].append("--extract-audio")
            self.config["additional-options"].append("--audio-quality=0")
            selected_format = self.aformat_opts.get_selected_item()
            self.config["additional-options"].append(f"--audio-format={selected_format.props.string}")
        else:
            # Video preference options
            format_sort = "" 
            res_str = self.resolution_opts.get_selected_item().props.string
            ext_str = self.vformat_opts.get_selected_item().props.string
            if "best" != res_str:
                format_sort = f"res:{res_str.rsplit(sep='x')[-1]}"
            if "best" != ext_str:
                format_sort += f",ext:{ext_str}"
            if len(format_sort) > 0:
                self.config["additional-options"].append(f"--format-sort={format_sort}")
            # otherwise, use the default -f "bv*+ba/b"

        # construct threading task to download file
        self.task_get_file = TaskGetFile(
            config=self.config,
            url=self.meta["original_url"],
            on_progress_callback=self.on_download_progress,
            on_done_callback=self.on_get_file_task_done
        )
        self.title.set_progress_fraction(0.0)
        self.task_get_file.start()
    
    def on_download_progress(self, status: str, percent: float):
        """
        callback for downloading task to update the progress
        """
        self.title.set_progress_fraction(percent)
        self.set_tooltip_text(f"{status}: {percent}")

    def on_get_file_task_done(self, retcode: int, strerr: str):
        """
        callback when downloading task ended
        """
        if 0 == retcode:
            self.set_tooltip_text(f"File downloaded in: {self.config['download-folder']}")
        else:
            self.set_tooltip_text(f"Failed to download ({retcode}): {strerr}")
            # TODO: also change the thumbnail to indicate error status
    
    def is_ready_for_download(self) -> bool:
        """
        """
        if self.meta is None or 1.0 == self.title.props.progress_fraction:
            return False
        else:
            return True

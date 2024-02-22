import sys
import gi
gi.require_version("Gtk", "4.0")

from gi.repository import GLib, Gio, Gtk
from pathlib import Path
from PygytWin import PygytWin

class Pygyt(Gtk.Application):
    """
    The main applicatino of pygyt
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        GLib.set_application_name("Pygyt")

        self.mainwin = None

        self.add_main_option(
            "download-folder",
            ord("d"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.STRING,
            "The folder to store download files. (default: '~/Downloads')",
            None
        )
        self.add_main_option(
            "additional-options",
            ord("a"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.STRING_ARRAY,
            "Append additional options for yt-dlp, multiple uses of '-a' are allowed.",
            "'OPTION ARG(s)'")

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action_about = Gio.SimpleAction.new("about", None)
        action_about.connect("activate", self.on_about)
        self.add_action(action_about)

        action_quit = Gio.SimpleAction.new("quit", None)
        action_quit.connect("activate", self.on_quit)
        self.add_action(action_quit)

    def do_activate(self):
        # setup default configuration
        # TODO: should have a single configuration manager
        #       instead of multiple copies in different module instances
        config_opts = {
            "download-folder": str(Path("~/Downloads").expanduser()),
            "additional-options": None
        }
        # update default configuration if option from command line is not None
        if self.options is not None:
            for key, value in config_opts.items():
                if self.options.get(key) is not None and self.options.get(key) != value:
                    config_opts[key] = self.options.get(key)
        self.config = config_opts
        # check and setup the download folder properly
        self.check_download_folder()

        # only allow a single window and raise any existing one
        if not self.mainwin:
            self.mainwin = PygytWin(config=self.config, application=self, title="Pygyt")
        self.mainwin.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        # convert GVariantDict -> GVariant -> dict
        self.options = options.end().unpack()

        self.activate()
        return 0
    
    def check_download_folder(self):
        """
        Checking the download folder setting, rules and assumptions are:
            - Default download folder is ~/Downloads/ and it is always available.
            - Users can specify a preferred folder to replace the default setting.
            - The folder specified by the user must be an existing one.
            - If the folder specified by the user does not exist, the default folder is used.
        """
        default_path = Path("~/Downloads").expanduser()
        config_path = Path(self.config["download-folder"])
        if (str(config_path) != str(default_path) and
            (not config_path.exists() or not config_path.is_dir())):
            self.config["download-folder"] = str(default_path)

    def on_about(self, action, param):
        about_dialog = Gtk.AboutDialog(transient_for=self.mainwin, modal=True)
        about_dialog.set_website("https://github.com/twMr7/pygyt")
        about_dialog.set_version("0.2")
        about_dialog.set_authors(["James Chang <twmr7@outlook.com>"])
        about_dialog.set_comments("python gtk frontend of yt-dlp")
        logo_image = Gtk.Image.new_from_file(str(Path(__file__).parent.joinpath("assets/pygyt_gleaner.png")))
        about_dialog.set_logo(logo_image.get_paintable())
        about_dialog.present()

    def on_quit(self, action, param):
        self.quit()


if __name__ == "__main__":
    app = Pygyt(application_id="twMr7.Pygyt", flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)

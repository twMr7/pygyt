import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib
from DownloadItem import DownloadItem

class PygytWin(Gtk.ApplicationWindow):
    """
    The main window of pygyt
    """
    def __init__(self, config: dict, **kwargs):
        super().__init__(**kwargs)

        self.config = config
        self.set_default_size(800, 600)

        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(True)
        self.set_titlebar(header_bar)

        menu = Gio.Menu()
        menu.append_item(Gio.MenuItem.new("About", "app.about"))
        menu.append_item(Gio.MenuItem.new("Quit", "app.quit"))

        menu_button = Gtk.MenuButton()
        menu_button.set_menu_model(menu)
        menu_button.set_icon_name("open-menu-symbolic")
        header_bar.pack_end(menu_button)

        # Toolbar
        self.action_bar = Gtk.ActionBar()
        add_button = Gtk.Button().new_from_icon_name("list-add-symbolic")
        add_button.connect("clicked", self.on_add_clicked)
        add_button.set_tooltip_text("add download item")
        self.action_bar.pack_start(add_button)
        remove_button = Gtk.Button().new_from_icon_name("list-remove-symbolic")
        remove_button.connect("clicked", self.on_remove_clicked)
        remove_button.set_tooltip_text("remove download item")
        self.action_bar.pack_start(remove_button)

        self.url_entry = Gtk.Entry()
        self.url_entry.set_hexpand(True)
        self.action_bar.set_center_widget(self.url_entry)

        download_button = Gtk.Button.new_from_icon_name("folder-download-symbolic")
        download_button.connect("clicked", self.on_download_clicked)
        download_button.set_tooltip_text("download selected/all")
        self.action_bar.pack_end(download_button)
        preference_button = Gtk.Button.new_from_icon_name("preferences-other-symbolic")
        preference_button.connect("clicked", self.on_preference_clicked)
        preference_button.set_tooltip_text("preference settings (NOT implemented)")
        self.action_bar.pack_end(preference_button)

        # Download list
        self.download_list = Gtk.ListBox()
        self.download_list.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.download_list.set_show_separators(True)
        self.download_list.set_hexpand(True)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.append(self.action_bar)
        vbox.append(self.download_list)

        self.set_child(vbox)

    def on_add_clicked(self, button):
        # don't bother to do further if entry is empty
        if 0 == self.url_entry.get_text_length(): return
        # add a new list row
        newitem = DownloadItem(
            config=self.config,
            url=self.url_entry.get_text()
        )
        newitem.connect("meta_ready", self.on_meta_ready)
        newitem.set_hexpand(True)
        self.download_list.append(newitem)
        # disable actions
        self.action_bar.set_sensitive(False)
        newitem.get_meta()

    def on_meta_ready(self, obj, title):
        #print(f"item {title} is ready")
        self.url_entry.set_text("")
        self.action_bar.set_sensitive(True)

    def on_remove_clicked(self, button):
        row_list = self.download_list.get_selected_rows()
        #if len(row_list) == 0:
        # TODO: ask before delete all
        if len(row_list) > 0:
            for row in row_list:
                if row is not None:
                    self.download_list.remove(row)

    def on_download_clicked(self, button):
        row_list = self.download_list.get_selected_rows()
        if len(row_list) == 0:
            # select all automatically
            self.download_list.select_all()
            # get the list again
            row_list = self.download_list.get_selected_rows()
        # invoke download method if item is ready
        if len(row_list) > 0:
            for row in row_list:
                self.download_list.unselect_row(row)
                item = row.get_child()
                if item is not None:
                    item.get_file()

    def on_preference_clicked(self, button):
        print("preference clicked")
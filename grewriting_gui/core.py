from grewriting_gui.helper import is_connected
from datetime import datetime
from os import path, makedirs, remove
from pathlib import Path
from grewritingpool import get_list

import gi
import random
import json

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gio

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="GRE Writing")
        self.set_border_width(10)
        self.set_default_size(800, 600)

        self.argument_lib = {}
        self.issue_lib = {}

        # header bar section
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "GRE Writing"
        self.set_titlebar(hb)

        self.help_btn = Gtk.Button.new_from_icon_name(
            "help-about-symbolic", Gtk.IconSize.MENU)
        self.help_btn.connect("clicked", self.help_dig)
        hb.pack_end(self.help_btn)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box.get_style_context(), "linked")

        self.start_btn = Gtk.Button.new_from_icon_name(
            "media-playback-start-symbolic", Gtk.IconSize.MENU)
        self.start_btn.connect("clicked", self.start)
        box.add(self.start_btn)

        hb.pack_start(box)

        # core window

        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(box_outer)

        update_sect = Gtk.Box()

        self.update_info = Gtk.Label(label="Last Updated: -")
        self.update_info.set_justify(Gtk.Justification.LEFT)
        update_sect.pack_start(self.update_info, True, True, 0)

        self.upd_btn = Gtk.Button.new_with_label("Update Definitions")
        update_sect.pack_start(self.upd_btn, False, True, 0)

        box_outer.pack_start(update_sect, False, False, 0)

        self.main_field = Gtk.Label()
        self.main_field.set_justify(Gtk.Justification.CENTER)
        self.main_field.set_markup("\n\n\n\n<i>Press Refresh to get a article</i>\n\n\n\n")
        self.main_field.set_line_wrap(True)
        box_outer.pack_start(self.main_field, False, False, 2)

        self.writing_field = Gtk.TextView()
        box_outer.pack_start(self.writing_field, True, True, 0)

        self.update_def()

    def update_def(self, force_update=False):
        # first time initializing the folder
        def_loc = path.join(Path.home(), ".local/share/grewriting-gui")
        makedirs(def_loc, exist_ok=True)
        def_1_file = path.join(def_loc, "def_argument.json")
        def_2_file = path.join(def_loc, "def_issue.json")
        tm_file = path.join(def_loc, "last_update")
        def_files_exist = path.isfile(def_1_file) and path.isfile(def_2_file)
        all_file_exist = path.isfile(tm_file) and def_files_exist

        if all_file_exist and not force_update:
            with open(tm_file, "r") as f:
                tm = f.read()
            self.update_info.set_label("Last Updated: {}".format(tm))
            with open(def_1_file, "r") as f:
                self.argument_lib = json.load(f)
            with open(def_2_file, "r") as f:
                self.issue_lib = json.load(f)
        else:
            for a in (def_1_file, def_2_file, tm_file):
                try:
                    remove(a)
                except FileNotFoundError:
                    pass
                
            if is_connected():
                self.argument_lib = json.loads(get_list('argument'))
                self.issue_lib = json.loads(get_list('issue'))
                tm = str(datetime.now())
                with open(tm_file, "w") as f:
                    f.write(tm)
                self.update_info.set_label("Last Updated: {}".format(tm))
            else:
                dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Error",
                )
                dialog.format_secondary_text(
                    "No Internet Connection. Failed to get definitions."
                )
                dialog.run()
                print("INFO dialog closed")
                dialog.destroy()

    def help_dig(self, widget):
        pass

    def start(self, widget):
        
        content = ""
        secure_random = random.SystemRandom()
        writing_list = secure_random.choice([self.argument_lib, self.issue_lib])
        secure_random = random.SystemRandom()
        writingitem = secure_random.choice(writing_list)
        content = writingitem['type'].title() + ' Writing Pool\n\nQuestion:\n' + \
                  writingitem['first'] + '\n'
        if 'second' in writingitem.keys():
            content = content + '\n' + writingitem['second'] + '\n'
        content = content + '\nInstruction:\n' + writingitem['instru'] + "\n"
        self.main_field.set_justify(Gtk.Justification.LEFT)
        self.main_field.set_text(content)


win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

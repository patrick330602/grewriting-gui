from grewriting_gui.helper import is_connected
from datetime import datetime
from os import path, makedirs, remove
from pathlib import Path
from grewritingpool import get_list

import gi
import random
import json

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, GLib

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="GRE Writing")
        self.set_border_width(10)
        self.set_default_size(800, 600)

        self.default_lib = "all"
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
        
        cfg_sect = Gtk.Box()
        self.type_info = Gtk.Box(spacing=6)
        old_btn = None
        for type in ('Both', 'Argument', 'Issue'):
            type_btn = Gtk.RadioButton.new_with_label_from_widget(old_btn, type)
            type_btn.connect("toggled", self.on_type_toggled, type)
            self.type_info.pack_start(type_btn, False, False, 0)
            if old_btn is None:
                old_btn = type_btn

        cfg_sect.pack_start(self.type_info, True, True, 0)

        self.timer_lb = Gtk.Label(label="Timer: 30:00")
        cfg_sect.pack_start(self.timer_lb, False, True, 0)
        
        box_outer.pack_start(cfg_sect, False, False, 2)

        
        self.main_field = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.type_title = Gtk.Label()
        self.main_field.pack_start(self.type_title, False, False, 0)
        
        self.g_in = Gtk.Label()
        self.g_in.set_justify(Gtk.Justification.LEFT)
        self.g_in.set_line_wrap(True)
        self.main_field.pack_start(self.g_in, False, False, 0)
        

        main_sect = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        q_sect = Gtk.Frame()
        
        self.q_sect = Gtk.Label()
        self.q_sect.set_markup("\n\n\n\n<i>Press Start to take a test</i>\n\n\n\n")
        self.q_sect.set_margin_start(60)
        self.q_sect.set_margin_end(60)
        main_sect.pack_start(self.q_sect, False, False, 5)
        
        self.i_sect = Gtk.Label()
        self.i_sect.set_line_wrap(True)
        self.i_sect.set_justify(Gtk.Justification.LEFT)
        main_sect.pack_start(self.i_sect, False, False, 0)
        main_sect.set_margin_start(40)
        main_sect.set_margin_end(40)
        self.main_field.pack_start(main_sect, False, False, 5)
        box_outer.pack_start(self.main_field, False, False, 5)

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
                dialog.destroy()

    def on_type_toggled(self, widget, type):
        self.default_lib = type.lower()
    
    def help_dig(self, widget):
        helpdig = Gtk.AboutDialog()
        helpdig.set_program_name("GRE Writing Pool GUI")
        helpdig.set_version("0.1")
        helpdig.set_copyright("Copyleft 2022 Patirck Wu\nAll the sample "
                              "writing are retrived via ETS website. GRE "
                              "is a registered trademark by ETS. All "
                              "rights reserved by ETS.")
        helpdig.set_comments("A GUI for GRE Writing Pool")
        helpdig.set_authors(["Patirck Wu"])
        helpdig.set_license_type(Gtk.License.GPL_3_0)
        helpdig.run()

    def start(self, widget):
        content = ""
        if self.default_lib == "both":
            secure_random = random.SystemRandom()
            writing_list = secure_random.choice([self.argument_lib, self.issue_lib])
        else:
            writing_list = self.argument_lib if self.default_lib == "argument" else self.issue_lib
        secure_random = random.SystemRandom()
        writingitem = secure_random.choice(writing_list)
        
        self.type_title.set_markup("<b>ANALYSE AN {}</b>\n".format(writingitem["type"].upper()))
        if writingitem["type"] == "issue":
            q_in_t = ("You have 30 minutes to plan and compose a response to the issue below. "
                      "A response to any other issue will receive a score of zero. Make sure "
                      "that you respond according to the specific instructions and support your "
                      "position on the issue with reasons and examples drawn from such areas as "
                      "your reading, experience, observations, and/or academic studies.")
        elif writingitem["type"] == "argument":
            q_in_t = ("You have 30 minutes to plan and compose a response in which you evaluate "
                      "the argument passage that appears below. A response to any other argument "
                      "will receive a score of zero. Make sure that you respond according to the "
                      "specific instructions and support your evaluation with relevant reasons "
                      "and/or examples.\n\n<b>Note that you are NOT being asked to present your "
                      "own views on the subject.</b>")
        self.g_in.set_markup(q_in_t)
        content = writingitem['first'] + '\n'
        if 'second' in writingitem.keys():
            content = content + '\n' + writingitem['second'] + '\n'
        self.q_sect.set_text(content)
        self.q_sect.set_line_wrap(True)
        self.q_sect.set_justify(Gtk.Justification.LEFT)
        self.i_sect.set_text(writingitem['instru'] + "\n")
        
        self.start_btn.set_sensitive(False)
        self.start_timer()

    def start_timer(self):
        counter = 1800
        while counter >= 0:
            GLib.timeout_add(counter * 1000, self.countdown, 1800 - counter)
            counter -= 1

    def countdown(self, counter):
        self.timer_lb.set_text("Timer: {:02d}:{:02d}".format(counter // 60, counter % 60))


win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

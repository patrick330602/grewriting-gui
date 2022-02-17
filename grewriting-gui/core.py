import gi
import random

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

from grewritingpool.main import _random_article

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="GRE Writing")
        self.set_border_width(10)
        self.set_default_size(800, 600)

        # header bar section
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "GRE Writing"
        self.set_titlebar(hb)

        self.help_btn = Gtk.Button.new_from_icon_name("help-about-symbolic", Gtk.IconSize.MENU)
        self.help_btn.connect("clicked", self.help_dig)
        hb.pack_end(self.help_btn)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box.get_style_context(), "linked")

        self.refresh_btn = Gtk.Button.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.MENU)
        self.refresh_btn.connect("clicked", self.ref)
        box.add(self.refresh_btn)

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
        self.main_field.set_lines(30)
        self.main_field.set_justify(Gtk.Justification.LEFT)
        self.main_field.set_line_wrap(True)
        box_outer.pack_start(self.main_field, False, False, 2)

        self.writing_field = Gtk.TextView()
        box_outer.pack_start(self.writing_field, True, True, 0)
        # initial the folder
        def_loc = path.join(Path.home(), ".local/share/grewriting-gui")
        makedirs(def_loc, exist_ok=True)
        def_file = path.join(def_loc, "def.json")

    def help_dig(self, widget):
        pass

    def ref(self, widget):
        content = ""
        secure_random = random.SystemRandom()
        writing_type = secure_random.choice(['argument', 'issue'])
        writingitem = _random_article(writing_type)
        content = writingitem['type'].title() + ' Writing Pool\n\nQuestion:\n' + \
                  writingitem['first'] + '\n'
        if 'second' in writingitem.keys():
            content = content + '\n' + writingitem['second'] + '\n'
        content = content + '\nInstruction:\n' + writingitem['instru']
        self.main_field.set_text(content)


win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
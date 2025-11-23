import sys
import time
from pathlib import Path
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango

from .core import SubtitleDownloader
from .utils import show_notification

class DownloadThreadGtk:
    def __init__(self, file_path, update_callback, progress_callback, finished_callback):
        self.file_path = file_path
        self.update_callback = update_callback
        self.progress_callback = progress_callback
        self.finished_callback = finished_callback
        self.downloader = SubtitleDownloader()

    def run(self):
        try:
            GLib.idle_add(self.progress_callback, 30, "Searching for Portuguese subtitles...")
            GLib.idle_add(self.update_callback, "log", "🌎 Searching for Portuguese subtitles...")
            
            success, message = self.downloader.download_for_file(self.file_path)
            
            if success:
                GLib.idle_add(self.progress_callback, 100, "Download completed!")
                GLib.idle_add(self.update_callback, "log", f"✅ {message}")
                GLib.idle_add(self.finished_callback, True, message)
            else:
                GLib.idle_add(self.progress_callback, 0, "No subtitles found")
                GLib.idle_add(self.update_callback, "log", f"❌ {message}")
                GLib.idle_add(self.finished_callback, False, message)
                
        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            GLib.idle_add(self.update_callback, "log", error_msg)
            GLib.idle_add(self.finished_callback, False, error_msg)

class SubtitleDownloaderWindowGtk:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = Path(file_path).name
        self.download_thread = None
        self.create_ui()

    def create_ui(self):
        self.window = Gtk.Window(title="Download Subtitle")
        self.window.set_default_size(600, 500)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_border_width(10)
        self.window.set_resizable(False)
        
        self.window.connect("destroy", Gtk.main_quit)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.window.add(vbox)
        
        # Header
        header_frame = Gtk.Frame()
        header_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        header_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        header_frame.add(header_vbox)
        
        file_label = Gtk.Label()
        file_label.set_markup(f"<b>File:</b> {self.file_name}")
        file_label.set_halign(Gtk.Align.START)
        file_label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        
        path_label = Gtk.Label()
        path_label.set_text(f"Folder: {Path(self.file_path).parent}")
        path_label.set_halign(Gtk.Align.START)
        path_label.set_ellipsize(Pango.EllipsizeMode.START)
        
        header_vbox.pack_start(file_label, False, False, 5)
        header_vbox.pack_start(path_label, False, False, 5)
        
        # Progress bar
        progress_frame = Gtk.Frame(label="Progress")
        progress_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        progress_frame.add(progress_vbox)
        
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("Ready to start...")
        
        self.status_label = Gtk.Label()
        self.status_label.set_text("Click Start to begin")
        self.status_label.set_halign(Gtk.Align.START)
        
        progress_vbox.pack_start(self.progress_bar, False, False, 5)
        progress_vbox.pack_start(self.status_label, False, False, 5)
        
        # Log area
        log_frame = Gtk.Frame(label="Details")
        log_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        log_frame.add(log_vbox)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(150)
        
        self.log_text = Gtk.TextView()
        self.log_text.set_editable(False)
        self.log_text.set_wrap_mode(Gtk.WrapMode.WORD)
        self.log_text.set_monospace(True)
        
        scrolled.add(self.log_text)
        log_vbox.pack_start(scrolled, True, True, 0)
        
        # Buttons
        button_box = Gtk.Box(spacing=10)
        button_box.set_halign(Gtk.Align.END)
        
        self.start_button = Gtk.Button.new_with_label("Start Download")
        self.start_button.connect("clicked", self.on_start_clicked)
        
        self.close_button = Gtk.Button.new_with_label("Close")
        self.close_button.connect("clicked", self.on_close_clicked)
        
        button_box.pack_start(self.start_button, False, False, 0)
        button_box.pack_start(self.close_button, False, False, 0)
        
        vbox.pack_start(header_frame, False, False, 0)
        vbox.pack_start(progress_frame, False, False, 0)
        vbox.pack_start(log_frame, True, True, 0)
        vbox.pack_start(button_box, False, False, 0)
        
    def log_message(self, message):
        text_buffer = self.log_text.get_buffer()
        end_iter = text_buffer.get_end_iter()
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        text_buffer.insert(end_iter, formatted_message)
        
        mark = text_buffer.create_mark(None, end_iter, True)
        self.log_text.scroll_to_mark(mark, 0.0, True, 0.0, 0.0)
        
        while Gtk.events_pending():
            Gtk.main_iteration()
    
    def update_progress(self, text, fraction=None):
        if fraction is not None:
            self.progress_bar.set_fraction(fraction / 100.0)
        self.progress_bar.set_text(text)
        self.status_label.set_text(text)
        
        while Gtk.events_pending():
            Gtk.main_iteration()
    
    def show_message_dialog(self, message_type, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=message_type,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
    
    def on_start_clicked(self, button):
        self.start_button.set_sensitive(False)
        self.start_download()
    
    def on_close_clicked(self, button):
        self.window.destroy()
    
    def handle_update(self, update_type, message):
        if update_type == "log":
            self.log_message(message)
        elif update_type == "progress":
            percent, text = message
            self.update_progress(text, percent)
    
    def handle_finished(self, success, message):
        self.start_button.set_sensitive(True)
        if success:
            self.show_message_dialog(Gtk.MessageType.INFO, "Success", message)
        else:
            self.show_message_dialog(Gtk.MessageType.ERROR, "Error", message)
    
    def start_download(self):
        self.log_text.get_buffer().set_text("")
        
        def run_download():
            downloader = DownloadThreadGtk(
                self.file_path,
                self.handle_update,
                lambda percent, text: GLib.idle_add(self.handle_update, "progress", (percent, text)),
                lambda success, msg: GLib.idle_add(self.handle_finished, success, msg)
            )
            downloader.run()
        
        import threading
        thread = threading.Thread(target=run_download)
        thread.daemon = True
        thread.start()
    
    def run(self):
        self.window.show_all()
        Gtk.main()

def main_gtk(file_path):
    """Main function for GTK GUI"""
    app = SubtitleDownloaderWindowGtk(file_path)
    app.run()
    return 0 # GTK GUI implementation will be implemented here

try:
    from pathlib import Path
    import sys
    src_path = Path(__file__).resolve().parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    import customtkinter as ctk
    from CTkMessagebox import CTkMessagebox
    from collectors.basic_audit import BasicAudit
    from collectors.medium_audit import MediumAudit
    from PIL import Image, ImageTk
    import os
    import pathlib
    import threading
    import webbrowser
except ImportError as e:
    print("Required packages are not installed")
    exit(0)

PARENT_PATH = Path(__file__).resolve().parent.parent.parent 
COLORS_PATH = PARENT_PATH / "config" / "colors.json"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(str(COLORS_PATH))

class CreateTripleBox(ctk.CTkFrame):
    def __init__(self, master, box_values=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        if box_values is None:
            box_values = {}
        self.grid_columnconfigure((0, 1, 2), weight=1)
        
        categories = [
            {"title": "critical", "color": "#F87171", "bg": "#2D1818"},
            {"title": "suspicious", "color": "#FB923C", "bg": "#2D2318"},
            {"title": "informational", "color": "#94A3B8", "bg": "#1E2937"}
        ]
        
        for i in range(3):
            box = ctk.CTkFrame(
                self, 
                corner_radius=8, 
                border_width=2,
                border_color=categories[i]["color"],
                fg_color=categories[i]["bg"]
            )
            box.grid(row=0, column=i, sticky="nsew", padx=8, pady=8)
            
            category = categories[i]["title"]
            results = box_values.get(category, [])
            
            title_frame = ctk.CTkFrame(
                box,
                corner_radius=6,
                fg_color=categories[i]["color"],
                height=40
            )
            title_frame.pack(fill="x", padx=10, pady=(10, 5))
            title_frame.pack_propagate(False)
            
            title_label = ctk.CTkLabel(
                title_frame,
                text=category.upper(),
                font=("Arial", 14, "bold"),
                text_color="#FFFFFF"
            )
            title_label.pack(expand=True)            
            count_label = ctk.CTkLabel(
                box,
                text=f"{len(results)} item(s)" if results else "",
                font=("Arial", 10),
                text_color=categories[i]["color"]
            )
            count_label.pack(pady=(0, 5))
            
            if results:
                scroll_frame = ctk.CTkScrollableFrame(
                    box,
                    fg_color="transparent",
                    corner_radius=0
                )
                scroll_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))
                
                for binary_path in results:
                    binary_name = os.path.basename(binary_path)
                    
                    item_frame = ctk.CTkFrame(
                        scroll_frame,
                        fg_color="transparent",
                        corner_radius=4
                    )
                    item_frame.pack(fill="x", pady=2)
                    
                    binary_btn = ctk.CTkButton(
                        item_frame,
                        text=f"📄 {binary_name}",
                        font=("Arial", 12),
                        fg_color="transparent",
                        hover_color=categories[i]["color"],
                        text_color=categories[i]["color"],
                        anchor="w",
                        border_width=1,
                        border_color=categories[i]["color"],
                        corner_radius=4,
                        height=32,
                        command=lambda b=binary_name: self.open_gtfo(b)
                    )
                    binary_btn.pack(side="left", fill="x", expand=True)
                    binary_btn.full_path = binary_path
                    
            else:
                empty_frame = ctk.CTkFrame(
                    box,
                    fg_color="transparent"
                )
                empty_frame.pack(expand=True, pady=30)
                
                empty_icon = ctk.CTkLabel(
                    empty_frame,
                    text="✓",
                    font=("Arial", 40),
                    text_color="#4ADE80"
                )
                empty_icon.pack()
                
                empty_label = ctk.CTkLabel(
                    empty_frame,
                    text="No issues found",
                    font=("Arial", 13),
                    text_color="#94A3B8"
                )
                empty_label.pack(pady=(5, 0))
    
    def open_gtfo(self, binary):
        url = f"https://gtfobins.github.io/gtfobins/{binary}/"
        webbrowser.open(url)

class LiarGUI(ctk.CTk):
    def __init__(self):
        try:
            super().__init__()
            self.title("BlueEyedGirl Linux auditing system")
            self.geometry("800x460")
            self.grid_columnconfigure(0, weight=1)

            try:
                icon_path = os.path.join(pathlib.Path(__file__).parent.parent.parent, "assets", "RedEyed4-glow.png")
                img = ImageTk.PhotoImage(Image.open(icon_path))
                self.wm_iconphoto(True, img)
            except FileNotFoundError as e:
                CTkMessagebox("Icon error", f"{e}")

            self.is_running = False

            self.font_registry = {
                "default": ctk.CTkFont(family="undefined", size=16),
                "title": ctk.CTkFont(family="Undefined", size=20, weight="bold"),
                "subtitle": ctk.CTkFont(family="Undefined", size=18, weight="bold"),
                "small": ctk.CTkFont(family="Undefined", size=13),
                "medium": ctk.CTkFont(family="Undefined", size=15),
                "mono": ctk.CTkFont(family="JetBrains Mono", size=14)
            }
            self._build_ui()
            self.basic_audit = BasicAudit()
            self.medium_audit = MediumAudit()
            self.progress_var = ctk.DoubleVar(value=0)
            self.progress_bar = None
            self.progress_label = None
        except Exception as e:
            print(f"Error during initialization: {e}")
            CTkMessagebox("Initialization error", f"{e}")

    def _build_ui(self):
        try:
            self.label = ctk.CTkLabel(self, text="BlueEyedGirl", font=self.font_registry["title"], text_color="#67E8F9")
            self.label.grid(row=0, column=0, pady=(50, 10))

            self.button_frame = ctk.CTkFrame(self)
            self.button_frame.grid(row=1, column=0)

            self.easy_mode = ctk.CTkButton(self.button_frame, text="Easy mode", font=self.font_registry["small"], command=self.easy)
            self.easy_mode.grid(row=1, column=0, padx=4)

            self.medium_mode = ctk.CTkButton(self.button_frame, text="Medium mode", font=self.font_registry["small"], command=self.medium)
            self.medium_mode.grid(row=1, column=1, padx=4)

            self.results_frame = ctk.CTkScrollableFrame(
                self,
                label_text="Audit Results",
                label_font=self.font_registry["title"]
            )
            self.results_frame.grid(row=2, column=0, padx=20, pady=20, sticky='nsew')
            self.grid_rowconfigure(2, weight=1)
            self.results_frame.grid_remove()
        except Exception as e:
            CTkMessagebox(title="Initialization error", message=f"{e}", icon="cancel")

    def clear_results(self):
        try:
            for widget in self.results_frame.winfo_children():
                widget.destroy()
            self.results_frame.update_idletasks()  
        except Exception as e:
            CTkMessagebox(title="Error while clearing screen", message=f"{e}", icon="cancel")
            return False
        
    def show_progress_bar(self):
        try:
            if self.progress_bar is None:
                # Progress label
                self.progress_label = ctk.CTkLabel(
                    self.results_frame,
                    text="Starting audit...",
                    font=self.font_registry["medium"],
                    text_color="#67E8F9"
                )
                self.progress_label.pack(pady=(10, 5))
                
                # Progress bar
                self.progress_bar = ctk.CTkProgressBar(
                    self.results_frame,
                    mode="determinate",
                    variable=self.progress_var,
                    width=400,
                    height=20,
                    progress_color="#67E8F9"
                )
                self.progress_bar.pack(pady=(0, 10))
                self.progress_var.set(0)
        except Exception as e:
            print(f"Error showing progress bar: {e}")

    def update_progress(self, value, message="Processing..."):
        """Update progress bar value and message"""
        try:
            if self.progress_bar:
                self.progress_var.set(value)
                if self.progress_label:
                    self.progress_label.configure(text=message)
                self.results_frame.update_idletasks()
        except Exception as e:
            print(f"Error updating progress: {e}")

    def hide_progress_bar(self):
        """Hide and destroy progress bar"""
        try:
            if self.progress_bar:
                self.progress_bar.destroy()
                self.progress_bar = None
            if self.progress_label:
                self.progress_label.destroy()
                self.progress_label = None
            self.progress_var.set(0)
        except Exception as e:
            print(f"Error hiding progress bar: {e}")

    def result_display(self, result=None, font_size: str = "medium", title: str = None, pady=10, padx=0, fill: str = 'x'):
        try:
            result_card = ctk.CTkFrame(self.results_frame)
            result_card.pack(pady=pady, padx=padx, fill=fill)

            if result is None:
                info = ctk.CTkLabel(result_card, text="Error with the application", font=self.font_registry[font_size])
                info.pack(padx=8, pady=1)
                return False
            
            if isinstance(result, str):
                info = ctk.CTkLabel(result_card, text=f"{result}", font=self.font_registry[font_size])
                info.pack(padx=8, pady=1)

            if isinstance(result, list):
                for result_elements in result:
                    print(result_elements)
                    if len(result_elements) == 0:
                        return False
                    info = ctk.CTkLabel(result_card, text=f"{result_elements.replace(' ', '')}", font=self.font_registry[font_size])
                    info.pack(padx=8, pady=1)

            if isinstance(result, dict):
                for key, values in result.items():
                    info = ctk.CTkLabel(result_card, text=f"{key}: {values}", font=self.font_registry["medium"], wraplength=700)
                    info.pack(padx=8, pady=1)
        except Exception as e:
            CTkMessagebox(title="Display error", message=f"{e}", icon="cancel")
            return False

    def pc_check(self):
        try:
            pc_checks = self.basic_audit.important_check()
            is_run = pc_checks.pop("is_run", False)
            if not is_run:
                self.after(0, self.result_display, pc_checks)
                return False
            else:
                self.after(0, self.result_display, "PC check completed. The app will run shortly", pady=0)
            return True
        except KeyError as e:
            CTkMessagebox(title="Json error", message=f"{e}", icon="cancel")
            return False
        except Exception as e:
            CTkMessagebox(title="PC check error", message=f"{e}", icon="cancel")
            return False
        finally:
            self.is_running = False
        
    def starter(self):
        try:
            self.results_frame.grid()
            self.is_running = True
        except Exception as e:
            CTkMessagebox(title="Start error", message="Error with starter function", icon="cancel")

    def user_details(self):
        try:
            user_detail = self.basic_audit.user_details()
            self.after(0, self.result_display, user_detail, pady=0)
            return True
        except Exception as e:
            CTkMessagebox(title="User detail error", message=f"{e}", icon="cancel")
            return False
        
    def file_check(self):
        try:
            file_results = self.basic_audit.file_system_check()
            critical_tuple = tuple(file_results.get('critical', []))
            standard_tuple = tuple(file_results.get('standard', []))
            unknown_tuple = tuple(file_results.get('unknown', []))
            all_suids = {
                "critical": critical_tuple,
                "suspicious": standard_tuple,
                "informational": unknown_tuple
            }
            if not all_suids:
                self.after(0, self.result_display, "No suid binaries found")
                return True
            self.after(0, self.result_display, "SUID binaries (grouped)")
            self.after(0, self.render_triple_box, all_suids)
            return True
        except Exception as e:
            print(f"Error in file_check: {e}")
            return False
    
    def cron_check(self):
        try:
            cron_results = self.medium_audit.run_audit()
            critical_cron = tuple(cron_results.get('critical', []))
            warning_cron = tuple(cron_results.get('warning', []))
            permission_issue_cron = tuple(cron_results.get('permission_issues', []))
            all_crons = {
                "critical": critical_cron,
                "suspicious": warning_cron,
                "informational": permission_issue_cron
            }
            if not all_crons:
                self.after(0, self.result_display, "No cron misconfigurations found")
                return True
            self.after(0, self.result_display, "CRON misconfigurations")
            self.after(0, self.render_triple_box, all_crons)
            return True
        except Exception as e:
            print(f"Error in cron_check: {e}")
            return False

    def render_triple_box(self, values):
        box = CreateTripleBox(master=self.results_frame, box_values=values)
        box.pack(fill="x", padx=10, pady=5)

    def easy(self):
        if self.is_running: 
            return True
        self.is_running = True
        audit_thread = threading.Thread(target=self.run_audit_sequence, daemon=True)
        audit_thread.start()

    def medium(self):
        if self.is_running:
            return True
        self.is_running = True
        audit_thread = threading.Thread(target=lambda: self.run_audit_sequence(level=2), daemon=True)
        audit_thread.start()

    def run_audit_sequence(self, level=1):
        try:
            self.clear_results()
            app_flow = [
                ("Initializing...", self.starter, 0.1),
                ("Checking system compatibility...", self.pc_check, 0.25),
                ("Gathering user details...", self.user_details, 0.4),
                ("Scanning file system...", self.file_check, 0.7),
            ]
            if level == 2:
                app_flow.append(("cron check", self.cron_check, 0.95))
            self.is_running = True
            self.after(0, self.show_progress_bar)
            total_steps = len(app_flow)
            for idx, (message, flow_method, progress) in enumerate(app_flow):
            # Update progress
                self.after(0, self.update_progress, progress, message)
                
                if flow_method():
                    print(f"{message} completed")
                    continue
            
            # Complete progress
            self.after(0, self.update_progress, 1.0, "Audit complete!")
            
            # Hide progress bar after a short delay
            self.after(1000, self.hide_progress_bar)
        except Exception as e:
            CTkMessagebox(title="Sequence error", message=f"{e}", icon="cancel")
            return False
        finally:
            self.is_running = False

if __name__ == "__main__":
    app = LiarGUI()
    app.mainloop()

def main():
    """Entry point for the application"""
    app = LiarGUI()
    app.mainloop()

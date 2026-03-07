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
# Using custom color scheme instead of json file
# ctk.set_default_color_theme(str(COLORS_PATH))

class CreateTripleBox(ctk.CTkFrame):
    def __init__(self, master, box_values=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        if box_values is None:
            box_values = {}
        self.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Clean minimal color scheme
        categories = [
            {"title": "critical", "color": "#ef4444", "bg": "#1c1917", "gradient": "#7f1d1d"},
            {"title": "suspicious", "color": "#f59e0b", "bg": "#1c1917", "gradient": "#78350f"},
            {"title": "informational", "color": "#3b82f6", "bg": "#1c1917", "gradient": "#1e3a8a"}
        ]
        
        for i in range(3):
            box = ctk.CTkFrame(
                self, 
                corner_radius=12, 
                border_width=0,
                fg_color=categories[i]["bg"]
            )
            box.grid(row=0, column=i, sticky="nsew", padx=12, pady=12)
            
            category = categories[i]["title"]
            results = box_values.get(category, [])
            
            # Clean header
            title_frame = ctk.CTkFrame(
                box,
                corner_radius=0,
                fg_color="transparent",
                height=60
            )
            title_frame.pack(fill="x", padx=20, pady=(20, 10))
            title_frame.pack_propagate(False)
            
            title_label = ctk.CTkLabel(
                title_frame,
                text=category.upper(),
                font=("SF Pro Display", 18, "bold"),
                text_color=categories[i]["color"]
            )
            title_label.pack(anchor="w")
            
            # Count
            count_label = ctk.CTkLabel(
                title_frame,
                text=f"{len(results)} detected" if results else "0 detected",
                font=("SF Pro Display", 13),
                text_color="#64748b"
            )
            count_label.pack(anchor="w", pady=(5, 0))
            
            # Divider line
            divider = ctk.CTkFrame(
                box,
                height=1,
                fg_color=categories[i]["color"],
                corner_radius=0
            )
            divider.pack(fill="x", padx=20, pady=(0, 15))
            
            if results:
                scroll_frame = ctk.CTkScrollableFrame(
                    box,
                    fg_color="transparent",
                    corner_radius=0
                )
                scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
                
                for binary_path in results:
                    binary_name = os.path.basename(binary_path)
                    
                    binary_btn = ctk.CTkButton(
                        scroll_frame,
                        text=binary_name,
                        font=("SF Mono", 12),
                        fg_color="transparent",
                        hover_color="#27272a",
                        text_color="#e2e8f0",
                        anchor="w",
                        border_width=0,
                        corner_radius=8,
                        height=40,
                        command=lambda b=binary_name: self.open_gtfo(b)
                    )
                    binary_btn.pack(fill="x", pady=4)
                    binary_btn.full_path = binary_path
                    
            else:
                empty_frame = ctk.CTkFrame(
                    box,
                    fg_color="transparent"
                )
                empty_frame.pack(expand=True, pady=40)
                
                empty_label = ctk.CTkLabel(
                    empty_frame,
                    text="All clear",
                    font=("SF Pro Display", 14),
                    text_color="#64748b"
                )
                empty_label.pack()
    
    def open_gtfo(self, binary):
        url = f"https://gtfobins.github.io/gtfobins/{binary}/"
        webbrowser.open(url)

class LiarGUI(ctk.CTk):
    def __init__(self):
        try:
            super().__init__()
            
            # Clean modern color scheme
            self.colors = {
                "bg_primary": "#0f0f0f",
                "bg_secondary": "#1c1917",
                "bg_tertiary": "#18181b",
                "accent_blue": "#3b82f6",
                "accent_cyan": "#06b6d4",
                "accent_red": "#ef4444",
                "accent_yellow": "#f59e0b",
                "accent_green": "#10b981",
                "text_primary": "#f1f5f9",
                "text_secondary": "#94a3b8",
                "border_subtle": "#27272a"
            }
            
            self.configure(fg_color=self.colors["bg_primary"])
            
            self.title("BlueEyedGirl - Linux Auditing System")
            self.geometry("1100x750")
            self.grid_columnconfigure(0, weight=1)

            try:
                icon_path = os.path.join(pathlib.Path(__file__).parent.parent.parent, "assets", "RedEyed4-glow.png")
                img = ImageTk.PhotoImage(Image.open(icon_path))
                self.wm_iconphoto(True, img)
            except FileNotFoundError as e:
                CTkMessagebox(title="Icon error", message=f"{e}", icon="cancel")

            self.is_running = False

            # Clean modern fonts
            self.font_registry = {
                "default": ctk.CTkFont(family="SF Pro Display", size=14),
                "title": ctk.CTkFont(family="SF Pro Display", size=32, weight="bold"),
                "subtitle": ctk.CTkFont(family="SF Pro Display", size=20, weight="bold"),
                "small": ctk.CTkFont(family="SF Pro Display", size=12),
                "medium": ctk.CTkFont(family="SF Pro Display", size=14),
                "mono": ctk.CTkFont(family="SF Mono", size=13)
            }
            self._build_ui()
            self.basic_audit = BasicAudit()
            self.medium_audit = MediumAudit()
            self.progress_var = ctk.DoubleVar(value=0)
            self.progress_bar = None
            self.progress_label = None
        except Exception as e:
            CTkMessagebox(title="Initialization error", message=f"{e}", icon="cancel")

    def _build_ui(self):
        try:
            # Spacious header
            header_frame = ctk.CTkFrame(
                self,
                fg_color="transparent",
                corner_radius=0,
                height=140
            )
            header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=30)
            header_frame.pack_propagate(False)
            
            self.label = ctk.CTkLabel(
                header_frame,
                text="BlueEyedGirl",
                font=self.font_registry["title"],
                text_color=self.colors["accent_cyan"]
            )
            self.label.pack(pady=(20, 8))
            
            subtitle = ctk.CTkLabel(
                header_frame,
                text="Linux Security Auditing System",
                font=self.font_registry["medium"],
                text_color=self.colors["text_secondary"]
            )
            subtitle.pack()

            # Minimal button panel
            self.button_frame = ctk.CTkFrame(
                self,
                fg_color="transparent"
            )
            self.button_frame.grid(row=1, column=0, pady=(0, 30))

            self.easy_mode = ctk.CTkButton(
                self.button_frame,
                text="Basic Scan",
                font=self.font_registry["medium"],
                command=self.easy,
                fg_color=self.colors["accent_blue"],
                hover_color="#2563eb",
                text_color="#ffffff",
                border_width=0,
                corner_radius=10,
                height=50,
                width=180
            )
            self.easy_mode.grid(row=0, column=0, padx=12)

            self.medium_mode = ctk.CTkButton(
                self.button_frame,
                text="Deep Scan",
                font=self.font_registry["medium"],
                command=self.medium,
                fg_color=self.colors["accent_red"],
                hover_color="#dc2626",
                text_color="#ffffff",
                border_width=0,
                corner_radius=10,
                height=50,
                width=180
            )
            self.medium_mode.grid(row=0, column=1, padx=12)

            # Clean results container
            results_container = ctk.CTkFrame(
                self,
                fg_color=self.colors["bg_secondary"],
                corner_radius=16,
                border_width=0
            )
            results_container.grid(row=2, column=0, padx=40, pady=(0, 40), sticky='nsew')
            self.grid_rowconfigure(2, weight=1)
            
            # Scrollable results frame
            self.results_frame = ctk.CTkScrollableFrame(
                results_container,
                fg_color="transparent",
                corner_radius=0
            )
            self.results_frame.pack(fill="both", expand=True, padx=25, pady=25)
            
            # Initial empty state message
            initial_msg = ctk.CTkLabel(
                self.results_frame,
                text="Select a scan mode to begin auditing",
                font=self.font_registry["medium"],
                text_color=self.colors["text_secondary"]
            )
            initial_msg.pack(pady=60)
            
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
                    text_color=self.colors["text_primary"]
                )
                self.progress_label.pack(pady=(30, 15))
                
                # Progress bar
                self.progress_bar = ctk.CTkProgressBar(
                    self.results_frame,
                    mode="determinate",
                    variable=self.progress_var,
                    width=500,
                    height=8,
                    progress_color=self.colors["accent_cyan"],
                    fg_color=self.colors["bg_tertiary"],
                    corner_radius=4
                )
                self.progress_bar.pack(pady=(0, 30))
                self.progress_var.set(0)
        except Exception as e:
            CTkMessagebox(title="Progress bar error", message=f"{e}", icon="cancel")

    def update_progress(self, value, message="Processing..."):
        """Update progress bar value and message"""
        try:
            if self.progress_bar:
                self.progress_var.set(value)
                if self.progress_label:
                    self.progress_label.configure(text=message)
                self.results_frame.update_idletasks()
        except Exception as e:
            CTkMessagebox(title="Progress update error", message=f"{e}", icon="cancel")

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
            CTkMessagebox(title="Progress bar error", message=f"{e}", icon="cancel")

    def result_display(self, result=None, font_size: str = "medium", title: str = None, pady=10, padx=0, fill: str = 'x'):
        try:
            # Clean result card
            result_card = ctk.CTkFrame(
                self.results_frame,
                fg_color=self.colors["bg_tertiary"],
                corner_radius=12,
                border_width=0
            )
            result_card.pack(pady=pady, padx=padx, fill=fill)

            if result is None:
                info = ctk.CTkLabel(
                    result_card,
                    text="Error with the application",
                    font=self.font_registry[font_size],
                    text_color=self.colors["accent_red"]
                )
                info.pack(padx=20, pady=15)
                return False
            
            if isinstance(result, str):
                info = ctk.CTkLabel(
                    result_card,
                    text=result,
                    font=self.font_registry[font_size],
                    text_color=self.colors["text_primary"]
                )
                info.pack(padx=20, pady=15, anchor="w")

            if isinstance(result, list):
                for result_elements in result:
                    print(result_elements)
                    if len(result_elements) == 0:
                        return False
                    info = ctk.CTkLabel(
                        result_card,
                        text=f"{result_elements.replace(' ', '')}",
                        font=self.font_registry[font_size],
                        text_color=self.colors["text_secondary"]
                    )
                    info.pack(padx=20, pady=6, anchor="w")

            if isinstance(result, dict):
                for key, values in result.items():
                    info = ctk.CTkLabel(
                        result_card,
                        text=f"{key}: {values}",
                        font=self.font_registry["medium"],
                        wraplength=950,
                        text_color=self.colors["text_primary"],
                        justify="left"
                    )
                    info.pack(padx=20, pady=6, anchor="w")
        except Exception as e:
            CTkMessagebox(title="Display error", message=f"{e}", icon="cancel")
            return False

    def pc_check(self):
        try:
            pc_checks = self.basic_audit.important_check()
            is_run = pc_checks.pop("is_run", False)
            if not is_run:
                CTkMessagebox(title="Package error", message=pc_checks['error'])
            else:
                self.after(0, self.result_display, "PC check completed. The app will run shortly", pady=8)
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
            self.is_running = True
            return True
        except Exception as e:
            CTkMessagebox(title="Start error", message="Error with starter function", icon="cancel")
            return False

    def user_details(self):
        try:
            user_detail = self.basic_audit.user_details()
            self.after(0, self.result_display, user_detail, pady=8)
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
            
            # Section header
            header_label = ctk.CTkLabel(
                self.results_frame,
                text="SUID Binary Analysis",
                font=self.font_registry["subtitle"],
                text_color=self.colors["text_primary"]
            )
            header_label.pack(pady=(20, 15), anchor="w")
            
            self.after(0, self.render_triple_box, all_suids)
            return True
        except Exception as e:
            CTkMessagebox(title="File check error", message=f"{e}", icon="cancel")
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
            
            # Section header
            header_label = ctk.CTkLabel(
                self.results_frame,
                text="Cron Configuration Analysis",
                font=self.font_registry["subtitle"],
                text_color=self.colors["text_primary"]
            )
            header_label.pack(pady=(20, 15), anchor="w")
            
            self.after(0, self.render_triple_box, all_crons)
            return True
        except Exception as e:
            CTkMessagebox(title="Cron check error", message=f"{e}", icon="cancel")
            return False

    def render_triple_box(self, values):
        box = CreateTripleBox(master=self.results_frame, box_values=values)
        box.pack(fill="x", padx=0, pady=10)

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
                ("Initializing", self.starter, 0.1),
                ("Checking system compatibility", self.pc_check, 0.25),
                ("Gathering user details", self.user_details, 0.4),
                ("Scanning file system", self.file_check, 0.7),
            ]
            if level == 2:
                app_flow.append(("Analyzing cron configurations", self.cron_check, 0.95))
            
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
            self.after(0, self.update_progress, 1.0, "Audit complete")
            
            # Hide progress bar after a short delay
            self.after(1200, self.hide_progress_bar)
            
        except Exception as e:
            CTkMessagebox(title="Sequence error", message=f"{e}", icon="cancel")
            return False
        finally:
            self.is_running = False

if __name__ == "__main__":
    app = LiarGUI()
    app.mainloop()
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
    print(f"Required packages are not installed: {e}")
    sys.exit(0)

PARENT_PATH = Path(__file__).resolve().parent.parent.parent 
COLORS_PATH = PARENT_PATH / "config" / "colors.json"

ctk.set_appearance_mode("dark")
# Using custom color scheme
ctk.set_default_color_theme(str(COLORS_PATH))

class CreateTripleBox(ctk.CTkFrame):
    def __init__(self, master, box_values=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        if box_values is None:
            box_values = {}
        self.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Original color scheme from the code
        categories = [
            {"title": "critical", "color": "#F87171", "bg": "#2D1818"},
            {"title": "suspicious", "color": "#FB923C", "bg": "#2D2318"},
            {"title": "informational", "color": "#94A3B8", "bg": "#1E2937"}
        ]
        
        for i in range(3):
            # Outer glow container
            glow_container = ctk.CTkFrame(
                self,
                corner_radius=12,
                fg_color="transparent"
            )
            glow_container.grid(row=0, column=i, sticky="nsew", padx=15, pady=15)
            
            box = ctk.CTkFrame(
                glow_container, 
                corner_radius=10, 
                border_width=2,
                border_color=categories[i]["color"],
                fg_color=categories[i]["bg"]
            )
            box.pack(fill="both", expand=True)
            
            category = categories[i]["title"]
            results = box_values.get(category, [])
            
            # Gradient-style header
            title_frame = ctk.CTkFrame(
                box,
                corner_radius=8,
                fg_color=categories[i]["color"],
                height=55
            )
            title_frame.pack(fill="x", padx=15, pady=15)
            title_frame.pack_propagate(False)
            
            title_label = ctk.CTkLabel(
                title_frame,
                text=category.upper(),
                font=("Arial", 16, "bold"),
                text_color="#FFFFFF"
            )
            title_label.pack(expand=True)
            
            # Count badge with styling
            count_frame = ctk.CTkFrame(
                box,
                fg_color="transparent",
                height=30
            )
            count_frame.pack(fill="x", padx=15, pady=(0, 10))
            count_frame.pack_propagate(False)
            
            count_label = ctk.CTkLabel(
                count_frame,
                text=f"{len(results)} item(s) found" if results else "No issues detected",
                font=("Arial", 11),
                text_color=categories[i]["color"]
            )
            count_label.pack(anchor="w")
            
            if results:
                # Scrollable content area
                scroll_frame = ctk.CTkScrollableFrame(
                    box,
                    fg_color="transparent",
                    corner_radius=0
                )
                scroll_frame.pack(fill="both", expand=True, padx=15, pady=(5, 15))
                
                for idx, binary_path in enumerate(results):
                    binary_name = os.path.basename(binary_path)
                    
                    # Item container with hover effect
                    item_container = ctk.CTkFrame(
                        scroll_frame,
                        fg_color="transparent"
                    )
                    item_container.pack(fill="x", pady=3)
                    
                    # Number badge
                    number_badge = ctk.CTkLabel(
                        item_container,
                        text=f"{idx + 1:02d}",
                        font=("Arial", 10, "bold"),
                        text_color=categories[i]["color"],
                        width=30
                    )
                    number_badge.pack(side="left", padx=(0, 8))
                    
                    binary_btn = ctk.CTkButton(
                        item_container,
                        text=f"{binary_name}",
                        font=("Arial", 12),
                        fg_color="transparent",
                        hover_color=categories[i]["color"],
                        text_color="#E0E0E0",
                        anchor="w",
                        border_width=1,
                        border_color=categories[i]["color"],
                        corner_radius=6,
                        height=36,
                        command=lambda b=binary_name: self.open_gtfo(b)
                    )
                    binary_btn.pack(side="left", fill="x", expand=True)
                    binary_btn.full_path = binary_path
                    
            else:
                # Empty state with icon
                empty_frame = ctk.CTkFrame(
                    box,
                    fg_color="transparent"
                )
                empty_frame.pack(expand=True, pady=40)
                
                # Circle background for checkmark
                check_bg = ctk.CTkFrame(
                    empty_frame,
                    width=70,
                    height=70,
                    corner_radius=35,
                    fg_color="#4ADE80"
                )
                check_bg.pack()
                check_bg.pack_propagate(False)
                
                empty_icon = ctk.CTkLabel(
                    check_bg,
                    text="✓",
                    font=("Arial", 35, "bold"),
                    text_color="#FFFFFF"
                )
                empty_icon.pack(expand=True)
                
                empty_label = ctk.CTkLabel(
                    empty_frame,
                    text="Secure",
                    font=("Arial", 14, "bold"),
                    text_color="#4ADE80"
                )
                empty_label.pack(pady=(10, 0))
    
    def open_gtfo(self, binary):
        url = f"https://gtfobins.github.io/gtfobins/{binary}/"
        webbrowser.open(url)

class LiarGUI(ctk.CTk):
    def __init__(self):
        try:
            super().__init__()
            self.title("BlueEyedGirl Linux auditing system")
            self.geometry("900x550")
            self.grid_columnconfigure(0, weight=1)

            try:
                icon_path = os.path.join(pathlib.Path(__file__).parent.parent.parent, "assets", "RedEyed4-glow.png")
                img = ImageTk.PhotoImage(Image.open(icon_path))
                self.wm_iconphoto(True, img)
            except FileNotFoundError as e:
                CTkMessagebox(title="Icon error", message=f"{e}", icon="cancel")

            self.is_running = False

            # Original fonts from the code
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
            CTkMessagebox(title="Initialization error", message=f"{e}", icon="cancel")

    def _build_ui(self):
        try:
            # Spacious header with gradient effect
            header_container = ctk.CTkFrame(
                self,
                fg_color="transparent",
                height=100
            )
            header_container.grid(row=0, column=0, sticky="ew", pady=(25, 5))
            header_container.pack_propagate(False)
            
            self.label = ctk.CTkLabel(
                header_container,
                text="BlueEyedGirl",
                font=self.font_registry["title"],
                text_color="#67E8F9"
            )
            self.label.pack(pady=(15, 5))
            
            subtitle = ctk.CTkLabel(
                header_container,
                text="Advanced Linux Security Auditing",
                font=self.font_registry["small"],
                text_color="#94A3B8"
            )
            subtitle.pack()

            # Button panel with creative layout
            button_container = ctk.CTkFrame(
                self,
                fg_color="transparent"
            )
            button_container.grid(row=1, column=0, pady=(10, 25))

            self.button_frame = ctk.CTkFrame(
                button_container,
                fg_color="transparent"
            )
            self.button_frame.pack()

            # Styled buttons with icons/emojis
            self.easy_mode = ctk.CTkButton(
                self.button_frame,
                text="🔍  Easy mode",
                font=self.font_registry["small"],
                command=self.easy,
                fg_color="#3B82F6",
                hover_color="#2563EB",
                corner_radius=10,
                height=45,
                width=160
            )
            self.easy_mode.grid(row=0, column=0, padx=10)

            self.medium_mode = ctk.CTkButton(
                self.button_frame,
                text="⚡  Medium mode",
                font=self.font_registry["small"],
                command=self.medium,
                fg_color="#8B5CF6",
                hover_color="#7C3AED",
                corner_radius=10,
                height=45,
                width=160
            )
            self.medium_mode.grid(row=0, column=1, padx=10)

            # Results container with professional styling
            results_outer = ctk.CTkFrame(
                self,
                fg_color="transparent"
            )
            results_outer.grid(row=2, column=0, padx=30, pady=(0, 30), sticky='nsew')
            self.grid_rowconfigure(2, weight=1)
            
            # Header bar for results
            results_header = ctk.CTkFrame(
                results_outer,
                fg_color="#1E293B",
                corner_radius=10,
                height=45,
                border_width=1,
                border_color="#334155"
            )
            results_header.pack(fill="x", pady=(0, 10))
            results_header.pack_propagate(False)
            
            header_label = ctk.CTkLabel(
                results_header,
                text="Audit Results",
                font=self.font_registry["subtitle"],
                text_color="#67E8F9"
            )
            header_label.pack(side="left", padx=20)
            
            # Status indicator
            status_indicator = ctk.CTkFrame(
                results_header,
                width=10,
                height=10,
                corner_radius=5,
                fg_color="#10B981"
            )
            status_indicator.pack(side="right", padx=20)
            
            # Scrollable results
            self.results_frame = ctk.CTkScrollableFrame(
                results_outer,
                fg_color="#1E293B",
                corner_radius=10,
                border_width=1,
                border_color="#334155"
            )
            self.results_frame.pack(fill="both", expand=True)
            
            # Welcome message
            welcome_container = ctk.CTkFrame(
                self.results_frame,
                fg_color="transparent"
            )
            welcome_container.pack(expand=True, pady=50)
            
            welcome_icon = ctk.CTkLabel(
                welcome_container,
                text="🛡️",
                font=("Arial", 48)
            )
            welcome_icon.pack()
            
            welcome_text = ctk.CTkLabel(
                welcome_container,
                text="Ready to audit",
                font=self.font_registry["medium"],
                text_color="#94A3B8"
            )
            welcome_text.pack(pady=(10, 0))
            
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
                # Progress container
                progress_container = ctk.CTkFrame(
                    self.results_frame,
                    fg_color="#0F172A",
                    corner_radius=10,
                    border_width=1,
                    border_color="#334155"
                )
                progress_container.pack(pady=20, padx=20, fill="x")
                
                # Progress label with icon
                label_frame = ctk.CTkFrame(
                    progress_container,
                    fg_color="transparent"
                )
                label_frame.pack(pady=(15, 10), padx=20, fill="x")
                
                spinner_label = ctk.CTkLabel(
                    label_frame,
                    text="⚙️",
                    font=("Arial", 20)
                )
                spinner_label.pack(side="left", padx=(0, 10))
                
                self.progress_label = ctk.CTkLabel(
                    label_frame,
                    text="Starting audit...",
                    font=self.font_registry["medium"],
                    text_color="#67E8F9"
                )
                self.progress_label.pack(side="left")
                
                # Progress bar
                self.progress_bar = ctk.CTkProgressBar(
                    progress_container,
                    mode="determinate",
                    variable=self.progress_var,
                    width=400,
                    height=12,
                    progress_color="#67E8F9",
                    fg_color="#1E293B",
                    corner_radius=6
                )
                self.progress_bar.pack(pady=(0, 15), padx=20, fill="x")
                self.progress_var.set(0)
                
                self.progress_container = progress_container
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
            if hasattr(self, 'progress_container') and self.progress_container:
                self.progress_container.destroy()
                self.progress_container = None
            self.progress_bar = None
            self.progress_label = None
            self.progress_var.set(0)
        except Exception as e:
            CTkMessagebox(title="Progress bar error", message=f"{e}", icon="cancel")

    def result_display(self, result=None, font_size: str = "medium", title: str = None, pady=10, padx=0, fill: str = 'x'):
        try:
            # Styled result card
            result_card = ctk.CTkFrame(
                self.results_frame,
                fg_color="#0F172A",
                corner_radius=8,
                border_width=1,
                border_color="#334155"
            )
            result_card.pack(pady=pady, padx=15, fill=fill)

            if result is None:
                info = ctk.CTkLabel(
                    result_card,
                    text="⚠️  Error with the application",
                    font=self.font_registry[font_size],
                    text_color="#F87171"
                )
                info.pack(padx=15, pady=12)
                return False
            
            if isinstance(result, str):
                info = ctk.CTkLabel(
                    result_card,
                    text=f"✓  {result}",
                    font=self.font_registry[font_size],
                    text_color="#10B981"
                )
                info.pack(padx=15, pady=12)

            if isinstance(result, list):
                for result_elements in result:
                    print(result_elements)
                    if len(result_elements) == 0:
                        return False
                    info = ctk.CTkLabel(
                        result_card,
                        text=f"• {result_elements.replace(' ', '')}",
                        font=self.font_registry[font_size],
                        text_color="#E0E0E0"
                    )
                    info.pack(padx=15, pady=4, anchor="w")

            if isinstance(result, dict):
                for key, values in result.items():
                    # Key-value pair styling
                    pair_frame = ctk.CTkFrame(
                        result_card,
                        fg_color="transparent"
                    )
                    pair_frame.pack(fill="x", padx=15, pady=4)
                    
                    key_label = ctk.CTkLabel(
                        pair_frame,
                        text=f"{key}:",
                        font=self.font_registry["medium"],
                        text_color="#67E8F9",
                        anchor="w",
                        width=150
                    )
                    key_label.pack(side="left")
                    
                    value_label = ctk.CTkLabel(
                        pair_frame,
                        text=str(values),
                        font=self.font_registry["medium"],
                        wraplength=600,
                        text_color="#E0E0E0",
                        anchor="w"
                    )
                    value_label.pack(side="left", fill="x", expand=True)
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
            
            # Section divider
            section_header = ctk.CTkFrame(
                self.results_frame,
                fg_color="transparent",
                height=50
            )
            section_header.pack(fill="x", pady=(15, 10), padx=15)
            section_header.pack_propagate(False)
            
            header_label = ctk.CTkLabel(
                section_header,
                text="🔐  SUID Binary Analysis",
                font=self.font_registry["subtitle"],
                text_color="#67E8F9"
            )
            header_label.pack(anchor="w")
            
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
            
            # Section divider
            section_header = ctk.CTkFrame(
                self.results_frame,
                fg_color="transparent",
                height=50
            )
            section_header.pack(fill="x", pady=(15, 10), padx=15)
            section_header.pack_propagate(False)
            
            header_label = ctk.CTkLabel(
                section_header,
                text="⏰  Cron Configuration Analysis",
                font=self.font_registry["subtitle"],
                text_color="#67E8F9"
            )
            header_label.pack(anchor="w")
            
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
                ("Initializing...", self.starter, 0.1),
                ("Checking system compatibility...", self.pc_check, 0.25),
                ("Gathering user details...", self.user_details, 0.4),
                ("Scanning file system...", self.file_check, 0.7),
            ]
            if level == 2:
                app_flow.append(("Analyzing cron configurations...", self.cron_check, 0.95))
            
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
            self.after(1500, self.hide_progress_bar)
            
            # Completion message
            def show_completion():
                completion_card = ctk.CTkFrame(
                    self.results_frame,
                    fg_color="#0F172A",
                    corner_radius=8,
                    border_width=1,
                    border_color="#10B981"
                )
                completion_card.pack(pady=15, padx=15, fill="x")
                
                completion_label = ctk.CTkLabel(
                    completion_card,
                    text="✅  Audit completed successfully",
                    font=self.font_registry["medium"],
                    text_color="#10B981"
                )
                completion_label.pack(pady=12)
            
            self.after(1500, show_completion)
            
        except Exception as e:
            CTkMessagebox(title="Sequence error", message=f"{e}", icon="cancel")
            return False
        finally:
            self.is_running = False

if __name__ == "__main__":
    app = LiarGUI()
    app.mainloop()
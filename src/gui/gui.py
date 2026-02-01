try:
    import customtkinter as ctk, os, pathlib
    from CTkMessagebox import CTkMessagebox
    from collectors.basic_audit import BasicAudit
    from pathlib import Path
    from PIL import Image, ImageTk
except ImportError as e:
    CTkMessagebox("Required packages are not installed")
    exit(0)

PARENT_PATH = Path(__file__).resolve().parent.parent.parent 
COLORS_PATH = PARENT_PATH / "config" / "colors.json"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(str(COLORS_PATH))
class CreateTripleBox(ctk.CTkFrame):
    def __init__(self, master, box_values=["A", "B", "C"], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.labels = [] 

        for i in range(3):
            box = ctk.CTkFrame(self, corner_radius=5, border_width=2)
            box.grid(row=0, column=i, sticky="nsew", padx=2)
            
            label = ctk.CTkLabel(box, text=box_values[i], font=("Arial", 14))
            label.pack(expand=True, pady=10)
            
            self.labels.append(label)

class BlueEyedGirl(ctk.CTk):
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
                CTkMessagebox(title="Error", message=f"{e}", icon="cancel")

            
            self.basic_audit = BasicAudit()
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
        except Exception as e:
            CTkMessagebox(title="Error", message=f"{e}", icon="cancel")

    def _build_ui(self):
        try:
            self.label = ctk.CTkLabel(self, text="BlueEyedGirl", font=self.font_registry["title"], text_color="#67E8F9")
            self.label.grid(row=0, column=0, pady=(50, 10))

            self.button_frame = ctk.CTkFrame(self)
            self.button_frame.grid(row=1, column=0)

            self.easy_mode = ctk.CTkButton(self.button_frame, text="Easy mode", font=self.font_registry["small"], command=self.main)
            self.easy_mode.grid(row=1, column=0, padx=4)

            self.medium_mode = ctk.CTkButton(self.button_frame, text="Medium mode", font=self.font_registry["small"], command=self.main)
            self.medium_mode.grid(row=1, column=1, padx=4)

            self.results_frame = ctk.CTkScrollableFrame(
                self,
                label_text="Audit Results",
                label_font=self.font_registry["title"]
            )
            self.results_frame.grid(row=2, column=0, padx=20, pady=20,sticky='nsew')
            self.grid_rowconfigure(2, weight=1)
            self.results_frame.grid_remove()
        except Exception as e:
            CTkMessagebox(title="Error", message=f"{e}", icon="cancel")

    def clear_results(self):
        try:
            for widget in self.results_frame.winfo_children():
                widget.destroy()
        except Exception as e:
            CTkMessagebox(title="Error while clearing screen", message=f"{e}", icon="cancel")
            return False
    
    def suid_result_display(self, result=None, pady=10, padx=10):
        try:
            result_card = ctk.CTkFrame(master=app, 
                       width=200, 
                       height=150, 
                       corner_radius=15,
                       border_width=2,
                       border_color="gray")
            result_card.pack(pady=pady, padx=padx)
            result_card.configure((0,1,2), weight=1)

            
        except Exception as e:
            CTkMessagebox(title="Error", message=f"{e}", icon="cancel")

    def result_display(self, result=None, font_size: str = "medium", title: str = None, pady=10, padx=0, fill: str = 'x'):
        try:
            # self.results_frame.grid()

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
                    info = ctk.CTkLabel(result_card, text = f"{result_elements.replace(" ", "")}", font=self.font_registry[font_size])
                    info.pack(padx=8,  pady=1)

            if isinstance(result, dict):
                for key, values in result.items():
                    info = ctk.CTkLabel(result_card, text=f"{key}: {values}", font=self.font_registry["medium"], wraplength=700)
                    info.pack(padx=8, pady=1)
        except Exception as e:
            CTkMessagebox(title="Error", message=f"{e}", icon="cancel")
            return False

    def pc_check(self):
        try:
            basic_audit = BasicAudit()
            pc_checks = basic_audit.important_check()
            is_run = pc_checks.pop("is_run", False)
            if not is_run:
                self.after(0, self.result_display,  pc_checks)
                return False
            else:
                self.after(0, self.result_display, "PC check completed. The app will run shortly", pady=0)
            return True
        except KeyError as e:
            CTkMessagebox(title="Json error", message=f"{e}", icon="cancel")
            return False
        except Exception as e:
            CTkMessagebox(title="Error", message=f"{e}", icon="cancel")
            return False
        
    def starter(self):
        try:
            self.results_frame.grid()
            self.is_running = True
        except Exception as e:
            CTkMessagebox(title="Error", message="Error with starter function", icon="cancel")

    def user_details(self):
        try:
            basic_audit = BasicAudit()
            user_detail = basic_audit.user_details()
            self.after(0, self.result_display, user_detail, pady=0)
            return True
        except Exception as e:
            CTkMessagebox(title="User detail error", message=f"{e}", icon="cancel")
            return False
        
    def file_check(self):
        try:
            basic_audit = BasicAudit()
            file_check = basic_audit.file_system_check()
            if len(file_check["suspicious"]) != 0:
                self.after(0, self.result_display, "Suspicious bins", font_size="subtitle")
                self.after(0, self.result_display, file_check["suspicious"], pady=0, padx=0, fill=None)
                self.after(0, self.result_display, "You might want to check these bins and according to your needs remove suid if possible.", pady=0, padx=0, fill=None)
            if len(file_check["critical"]) != 0:
                self.after(0, self.result_display, "Critical bins", font_size="default")
                self.after(0, self.result_display, file_check["critical"], pady=0, padx=0, fill=None)
                self.after(0, self.result_display, "You have to remove suids from these bins.", pady=0, padx=0, fill=None)
        except Exception as e:
            CTkMessagebox(title="Bash error", message=f"{e}", icon="cancel")
    def main(self):
        try:
            app_flow= [
                ("starter", self.starter),
                ("pc check", self.pc_check),
                ("user details", self.user_details),
                ("file check", self.file_check)
            ]
            self.is_running = True
            for flow_name, flow_method in app_flow:
                if flow_method():
                    print(f"{flow_name} is true")
                    continue
        except Exception as e:
            ctk.CTkMessageBox(title="Error", message=f"{e}", icon="cancel")

if __name__ == "__main__":
    app = BlueEyedGirl()
    app.mainloop()
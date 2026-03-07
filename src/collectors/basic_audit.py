try:
    import subprocess, json, os, platform, importlib.metadata, sys
    from pathlib import Path
    from rich.panel import Panel
    from rich.table import Table
    from rich.console import Console
    from rich.text import Text
    from rich.rule import Rule
    from rich import box
    from rich.align import Align
except ImportError as e:
    print(e)
    exit(0)

def _find_project_root():
    """Find project root by looking for config directory with bins.json"""
    current = Path(__file__).resolve()
    
    for _ in range(6):  
        if (current / "config" / "bins.json").exists():
            return current
        if (current / "config" / "colors.json").exists():
            return current
        current = current.parent
    
    return Path(__file__).resolve().parent.parent.parent

PARENT_PATH = _find_project_root()

class BasicAudit:
    def __init__(self):
        with open(str(PARENT_PATH / "config" / "bins.json"), "r") as f:
            self.set_classfication = json.load(f)
        self.suid_classification = self.set_classfication["suid"]
        self.sgid_classification = self.set_classfication["sgid"]
        self.world_writable = self.set_classfication["world_writable"]
        self.classification = {
            "critical": [],
            "suspicious": [],
            "unknown": [],
            "standard": []
        }

    def run_bash(self, function_name):
        try:
            result = subprocess.run(
                [str(PARENT_PATH / "scripts" / "basic_info_check.sh"), function_name],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            return {"error": f"ERROR: {e.stderr.strip()}"}
        except json.JSONDecodeError as e:
            return {"error": f"JSON decode error: {e}"}
        except Exception as e:
            return {"error": f"Exception: {e}"}

    def check_accordingly(self, basename, register):
        try:
            for severity, bins in register.items():
                if basename in bins:
                    return severity
            return "unknown"
        except Exception as e:
            print(f"Error has occured: {e}")
            return "unknown"

    def classify_binaries(self, path, bin_to_check):
        try:
            if bin_to_check == "suid_check":
                return self.check_accordingly(path.split('/')[-1], self.suid_classification)
            elif bin_to_check == "sgid_check":
                return self.check_accordingly(path.split('/')[-1], self.sgid_classification)
            elif bin_to_check == "world_writable_check":  # Fixed typo
                return self.check_accordingly(os.path.dirname(path), self.world_writable)  # Added return
            return "unknown"
        except Exception as e:
            print(f"Error has occured: {e}")
            return "unknown"

    def calculate_binaries(self, bins_to_check):
        try:
            bins = self.run_bash(bins_to_check)
            if isinstance(bins, dict) and "error" in bins:
                print(f"Error running {bins_to_check}: {bins['error']}")
                return False
            
            if not isinstance(bins, list):
                print(f"Unexpected result type from {bins_to_check}: {type(bins)}")
                return False
            
            for path in bins:
                severity = self.classify_binaries(path, bins_to_check)
                self.classification[severity].append(path)
            return True
        except Exception as e:
            print(f"Error has occured: {e}")
            return False

    def user_details(self):
        try:
            user_detail = self.run_bash("user_detail")
            return user_detail
        except Exception as e:
            print(f"Error has occured {e}")
            return False

    def important_check(self):
        status = {
            "error": [],
            "warning": [],
            "is_run": True
        }
        try:
            os_name = platform.system()
            system = platform.freedesktop_os_release()['ID_LIKE']
            python_version = sys.version_info
            
            if os_name.lower() != "linux":
                status["error"].append("Not linux")
                status["is_run"] = False
            
            if system.lower() not in ["arch"]:
                status["error"].append("Linux distro not supported")
                status["is_run"] = False
            
            if not python_version >= (3, 10):
                status["warning"].append(f"python version {sys.version_info.major}.{sys.version_info.minor} is not compatible")
            
            with open(PARENT_PATH / "requirements.txt", "r") as f:
                requirements = f.readlines()

            for line in requirements:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                package_name = line.split('>=')[0].split('==')[0].split('>')[0].strip()
                
                try:
                    version = importlib.metadata.version(package_name)
                except importlib.metadata.PackageNotFoundError:
                    status["error"].append(f"Missing dependency: {package_name}")
                    status["is_run"] = False
        except Exception as e:
            status["error"].append(str(e))
        
        return status

    def file_system_check(self):
        try:
            check_list = ['suid_check', 'sgid_check', 'world_writable_check']  # Fixed typo
            for check_type in check_list:
                self.calculate_binaries(check_type)
            return self.classification
        except Exception as e:
            print(f'Error has occured: {e}')
            return 

class RichResultDisplay:
    """Professional security audit display system using Rich"""
    
    def __init__(self, width=100):
        self.console = Console(width=width, force_terminal=True)
        self.width = width
        self.findings = {"critical": 0, "suspicious": 0, "unknown": 0, "standard": 0}
    
    def header(self, title, icon="📋"):
        """Display section header"""
        self.console.print()
        self.console.print(Panel(
            Text(f" {title} ", style="bold white"),
            title=f"[bold cyan]{icon}[/bold cyan]",
            border_style="cyan",
            padding=(0, 2),
            box=box.ROUNDED
        ))
    
    def footer(self, message, status="success"):
        """Display footer/completion message"""
        if status == "success":
            style = "green"
            icon = "✓"
        elif status == "warning":
            style = "yellow"
            icon = "⚠️"
        else:
            style = "red"
            icon = "✗"
        
        self.console.print(Panel(
            f"[bold {style}]{icon} {message}[/bold {style}]",
            border_style=style,
            padding=(0, 2),
            box=box.ROUNDED
        ))
    
    def add_result(self, label, value=None, severity=None):
        """Display a result row"""
        if value is None:
            if isinstance(label, list):
                for item in label:
                    self.console.print(f"  [red]✗[/red] {item}")
            else:
                self.console.print(f"  [red]✗[/red] {label}")
        else:
            if severity:
                severity_upper = severity.upper()
                if severity_upper == "CRITICAL":
                    style = "bold white on red"
                    self.findings["critical"] += 1
                elif severity_upper == "SUSPICIOUS":
                    style = "bold black on yellow"
                    self.findings["suspicious"] += 1
                elif severity_upper == "UNKNOWN":
                    style = "bold yellow"
                    self.findings["unknown"] += 1
                else:  # STANDARD
                    style = "bold green"
                    self.findings["standard"] += 1
                
                self.console.print(f"  [{style}] {severity_upper:12} [/] : {value}")
            else:
                self.console.print(f"  [cyan]{label:<30}[/cyan] : [white]{value}[/white]")
    
    def add_table_result(self, headers, rows):
        """Display results in a table format"""
        table = Table(show_header=True, box=box.ROUNDED, padding=(0, 1))
        
        for header in headers:
            table.add_column(header, style="cyan")
        
        for row in rows:
            table.add_row(*row)
        
        self.console.print(table)
    
    def summary(self):
        """Display audit summary with findings"""
        total = sum(self.findings.values())
        
        if total == 0:
            return
        
        self.console.print()
        self.console.print(Rule("[bold]📊 Audit Summary[/bold]", style="cyan"))
        self.console.print()
        
        summary_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        summary_table.add_column("Category", style="cyan", width=15)
        summary_table.add_column("Count", style="bold", width=10)
        summary_table.add_column("Percentage", width=15)
        
        for category, count in self.findings.items():
            if count == 0:
                continue
            
            percentage = f"{(count/total*100):.1f}%"
            
            if category == "critical":
                color = "red"
                icon = "🚨"
            elif category == "suspicious":
                color = "yellow"
                icon = "⚠️"
            elif category == "unknown":
                color = "blue"
                icon = "❓"
            else:
                color = "green"
                icon = "✓"
            
            summary_table.add_row(
                f"[{color}]{icon} {category.title()}[/]",
                f"[{color} bold]{count}[/]",
                f"[dim]{percentage}[/]"
            )
        
        self.console.print(summary_table)
        
        # Final status
        self.console.print()
        if self.findings["critical"] > 0:
            status_text = "[bold red]🚨 CRITICAL: Immediate action required![/bold red]"
            border_color = "red"
        elif self.findings["suspicious"] > 0:
            status_text = "[bold yellow]⚠️  WARNING: Suspicious files detected[/bold yellow]"
            border_color = "yellow"
        elif self.findings["unknown"] > 0:
            status_text = "[bold blue]ℹ️  INFO: Unknown files found - review recommended[/bold blue]"
            border_color = "blue"
        else:
            status_text = "[bold green]✓ ALL CLEAR: No security issues detected[/bold green]"
            border_color = "green"
        
        self.console.print(Panel(
            status_text,
            border_style=border_color,
            padding=(1, 2),
            box=box.HEAVY
        ))
    
    def reset(self):
        """Reset findings counter"""
        self.findings = {"critical": 0, "suspicious": 0, "unknown": 0, "standard": 0}
    
    def print_error(self, message):
        """Print error message"""
        self.console.print(f"  [bold red]✗ ERROR:[/bold red] {message}")
    
    def print_warning(self, message):
        """Print warning message"""
        self.console.print(f"  [bold yellow]⚠️  WARNING:[/bold yellow] {message}")
    
    def print_success(self, message):
        """Print success message"""
        self.console.print(f"  [bold green]✓[/bold green] {message}")

class LiarBanner:
    """Professional banner display for Liar Security Audit Tool"""
    
    def __init__(self, width=80):
        self.console = Console(width=width, force_terminal=True)
        self.width = width
        self.version = "1.0.0"
        self.author = "Security Team"

    def show_banner(self):
        banner = Text()
        banner.append("\n  L.I.A.R\n", style="bold cyan")
        banner.append("  🔒 Security Audit Tool\n", style="bold white")
        banner.append(f"  Version: {self.version}\n", style="dim yellow")
        banner.append(f"  Author: {self.author}\n\n", style="dim yellow")
        
        self.console.print(Panel(
            Align.center(banner),
            border_style="cyan",
            title="[bold white]🛡️  LIAR SECURITY AUDIT  🛡️[/bold white]",
            subtitle="[dim]System Security Assessment Tool[/dim]"
        ))

if __name__ == "__main__":
    c = BasicAudit()
    show_results = RichResultDisplay()
    banner = LiarBanner()
    banner.show_banner()
    show_results.header("System Checks", "🔍")
    important_checks = c.important_check()
    
    if important_checks["is_run"] == False:
        for error in important_checks["error"]:
            show_results.add_result(error)
        show_results.footer("System checks failed", "error")
        sys.exit(1)
    
    show_results.footer("Checks have been completed", "success")    
    show_results.header("User Details", "👤")
    user_data = c.user_details()
    
    if isinstance(user_data, dict) and "error" not in user_data:
        for column, data in user_data.items():
            show_results.add_result(f"{column}", f"{data}")
        show_results.footer("User details displayed", "success")
    else:
        show_results.add_result("Failed to retrieve user details")    
    show_results.header("File Check System Results", "📁")
    file_data = c.file_system_check()
    
    if file_data:
        for severity, paths in file_data.items():
            for path in paths:
                show_results.add_result(severity, path, severity=severity)        
        show_results.summary()
        show_results.footer("File check completed", "success")
    else:
        show_results.add_result("Failed to run file system check")

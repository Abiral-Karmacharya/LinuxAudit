try:
    import subprocess, json, os, sys, re, importlib.metadata
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
    """Find project root by looking for scripts directory"""
    current = Path(__file__).resolve()
    
    for _ in range(6):
        if (current / "scripts" / "medium_info_check.sh").exists():
            return current
        if (current / "config" / "bins.json").exists():
            return current
        current = current.parent
    
    return Path(__file__).resolve().parent.parent.parent

PARENT_PATH = _find_project_root()

class MediumAudit:
    def __init__(self):
        # Suspicious patterns to look for
        self.suspicious_patterns = [
            r'curl\s+',
            r'wget\s+',
            r'\bnc\b|\bnetcat\b',
            r'/tmp/',
            r'base64',
            r'chmod\s+[0-9]*7',
            r'/dev/tcp',
            r'bash\s+-i',
            r'sh\s+-i',
            r'python.*-c',
            r'perl.*-e',
            r'\.sh\s*&',
            r'mkfifo',
            r'nohup',
        ]
        
        self.classification = {
            "critical": [],      
            "warning": [],       # Potentially suspicious
            "permission_issues": [],
            "info": []          # Normal entries
        }

    def run_bash(self, function_name):
        try:
            result = subprocess.run(
                [str(PARENT_PATH / "scripts" / "medium_info_check.sh"), function_name],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            return {"error": f"ERROR: {e.stderr.strip()}"}
        except json.JSONDecodeError as e:
            return {"error": f"JSON decode error: {e}"}

    def analyze_cron_entry(self, entry_text):
        try:
            matches = []
            for pattern in self.suspicious_patterns:
                if re.search(pattern, entry_text, re.IGNORECASE):
                    matches.append(pattern.replace('\\', ''))
            
            if len(matches) >= 2:
                return "critical", matches
            elif len(matches) == 1:
                return "warning", matches
            else:
                return "info", []
        except Exception as e:
            print(f"Error analyzing entry: {e}")
            return "info", []

    def audit_cron_jobs(self):
        """Main cron audit function"""
        try:
            cron_entries = self.run_bash("cron_files_check")
            
            if isinstance(cron_entries, dict) and "error" in cron_entries:
                print(f"Error fetching cron entries: {cron_entries['error']}")
                return False
            
            if not isinstance(cron_entries, list):
                print(f"Unexpected result type: {type(cron_entries)}")
                return False
            
            for cron_job in cron_entries:
                path = cron_job.get("path", "")
                user = cron_job.get("user", "")
                entry = cron_job.get("entry", "")
                
                severity, patterns = self.analyze_cron_entry(entry)
                
                job_data = {
                    "path": path,
                    "user": user,
                    "entry": entry,
                    "matched_patterns": patterns
                }
                
                self.classification[severity].append(job_data)
            
            return True
        except Exception as e:
            print(f"Error has occured: {e}")
            return False

    def run_audit(self):
        """Run complete medium audit"""
        try:
            self.audit_cron_jobs()
            # self.check_cron_permissions()
            return self.classification
        except Exception as e:
            print(f"Error has occured: {e}")
            return False
        
class RichResultDisplay:
    """Professional security audit display system using Rich"""
    
    def __init__(self, width=120):
        self.console = Console(width=width, force_terminal=True)
        self.width = width
        self.findings = {"critical": 0, "warning": 0, "permission_issues": 0, "info": 0}
    
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
    
    def display_cron_entry(self, job_data, severity):
        """Display a single cron job entry with proper formatting"""
        
        # Severity color mapping
        severity_styles = {
            "critical": ("red", "🚨", "bold white on red"),
            "warning": ("yellow", "⚠️", "bold black on yellow"),
            "permission_issues": ("blue", "🔓", "bold white on blue"),
            "info": ("green", "✓", "bold green")
        }
        
        color, icon, badge_style = severity_styles.get(severity, ("white", "•", "white"))
        
        # Update findings counter
        if severity in self.findings:
            self.findings[severity] += 1
        
        # Create entry panel
        entry_text = Text()
        
        # Header line with severity badge
        entry_text.append(f" {icon} ", style=badge_style)
        entry_text.append(f" {severity.upper()} ", style=f"bold {color}")
        entry_text.append(f"│ User: {job_data.get('user', 'N/A')} ", style="dim")
        entry_text.append(f"│ Path: {job_data.get('path', 'N/A')}", style="dim cyan")
        entry_text.append("\n\n", style="white")
        
        # Cron entry (the actual command)
        entry_text.append("  📌 Entry:\n", style="bold cyan")
        entry = job_data.get('entry', 'N/A')
        # Truncate long entries
        if len(entry) > 80:
            entry = entry[:77] + "..."
        entry_text.append(f"     {entry}\n", style="white")
        
        # Matched patterns (if any)
        matched = job_data.get('matched_patterns', [])
        if matched:
            entry_text.append("\n  ⚠️  Matched Suspicious Patterns:\n", style="bold yellow")
            for pattern in matched:
                entry_text.append(f"     • {pattern}\n", style="yellow")
        else:
            entry_text.append("\n  ✓ No suspicious patterns detected\n", style="dim green")
        
        # Print the entry panel
        self.console.print(Panel(
            entry_text,
            border_style=color,
            padding=(1, 2),
            box=box.ROUNDED
        ))
    
    def display_cron_results(self, classification):
        """Display all cron audit results organized by severity"""
        
        # Display Critical first (most important)
        if classification.get("critical"):
            self.console.print()
            self.console.print(Rule("[bold red]🚨 CRITICAL FINDINGS[/bold red]", style="red"))
            self.console.print()
            for job in classification["critical"]:
                self.display_cron_entry(job, "critical")
        
        # Display Warnings
        if classification.get("warning"):
            self.console.print()
            self.console.print(Rule("[bold yellow]⚠️  WARNINGS[/bold yellow]", style="yellow"))
            self.console.print()
            for job in classification["warning"]:
                self.display_cron_entry(job, "warning")
        
        # Display Permission Issues
        if classification.get("permission_issues"):
            self.console.print()
            self.console.print(Rule("[bold blue]🔓 PERMISSION ISSUES[/bold blue]", style="blue"))
            self.console.print()
            for job in classification["permission_issues"]:
                self.display_cron_entry(job, "permission_issues")
        
        # Display Info (normal entries)
        if classification.get("info"):
            self.console.print()
            self.console.print(Rule("[bold green]✓ INFO - Normal Entries[/bold green]", style="green"))
            self.console.print()
            
            # Show info entries in a compact table instead of individual panels
            table = Table(show_header=True, box=box.SIMPLE, padding=(0, 1))
            table.add_column("Path", style="cyan", width=40)
            table.add_column("User", style="white", width=15)
            table.add_column("Entry", style="dim", width=60)
            
            for job in classification["info"]:
                entry = job.get('entry', 'N/A')
                if len(entry) > 57:
                    entry = entry[:54] + "..."
                table.add_row(
                    job.get('path', 'N/A'),
                    job.get('user', 'N/A'),
                    entry
                )
            
            self.console.print(table)
    
    def summary(self):
        """Display audit summary with findings"""
        total = sum(self.findings.values())
        
        if total == 0:
            return
        
        self.console.print()
        self.console.print(Rule("[bold]📊 Audit Summary[/bold]", style="cyan"))
        self.console.print()
        
        summary_table = Table(show_header=False, box=box.SIMPLE_HEAVY, padding=(0, 2))
        summary_table.add_column("Category", style="cyan", width=20)
        summary_table.add_column("Count", style="bold", width=10)
        summary_table.add_column("Percentage", width=15)
        
        for category, count in self.findings.items():
            if count == 0:
                continue
            
            percentage = f"{(count/total*100):.1f}%"
            
            if category == "critical":
                color = "red"
                icon = "🚨"
            elif category == "warning":
                color = "yellow"
                icon = "⚠️"
            elif category == "permission_issues":
                color = "blue"
                icon = "🔓"
            else:
                color = "green"
                icon = "✓"
            
            summary_table.add_row(
                f"[{color}]{icon} {category.replace('_', ' ').title()}[/]",
                f"[{color} bold]{count}[/]",
                f"[dim]{percentage}[/]"
            )
        
        self.console.print(summary_table)
        
        # Final status
        self.console.print()
        if self.findings["critical"] > 0:
            status_text = "[bold red]🚨 CRITICAL: Immediate action required! Suspicious cron jobs detected.[/bold red]"
            border_color = "red"
        elif self.findings["warning"] > 0:
            status_text = "[bold yellow]⚠️  WARNING: Review recommended. Potentially suspicious entries found.[/bold yellow]"
            border_color = "yellow"
        elif self.findings["permission_issues"] > 0:
            status_text = "[bold blue]ℹ️  INFO: Permission issues detected. Review recommended.[/bold blue]"
            border_color = "blue"
        else:
            status_text = "[bold green]✓ ALL CLEAR: No security issues detected in cron jobs.[/bold green]"
            border_color = "green"
        
        self.console.print(Panel(
            status_text,
            border_style=border_color,
            padding=(1, 2),
            box=box.HEAVY
        ))
    
    def reset(self):
        """Reset findings counter"""
        self.findings = {"critical": 0, "warning": 0, "permission_issues": 0, "info": 0}

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
    # Show banner
    banner = LiarBanner()
    banner.show_banner()
    
    # Run audit
    c = MediumAudit()
    show_results = RichResultDisplay()
    
    # Header
    show_results.header("Cron Job Security Audit", "⏰")
    
    # Run audit
    results = c.run_audit()
    
    if results:
        # Display cron results
        show_results.display_cron_results(results)
        
        # Show summary
        show_results.summary()
        
        # Footer
        show_results.footer("Cron audit completed", "success")
    else:
        show_results.print_error("Failed to run cron audit")
        sys.exit(1)
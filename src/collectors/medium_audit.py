try:
    import subprocess, json, os, sys, re
    from pathlib import Path
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
        """Analyze a single cron entry for suspicious patterns"""
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

    # def check_cron_permissions(self):
    #     """Check file permissions on cron files"""
    #     try:
    #         perms = self.run_bash("cron_permissions_check")
            
    #         if isinstance(perms, dict) and "error" in perms:
    #             print(f"Error checking permissions: {perms['error']}")
    #             return False
            
    #         for file_info in perms:
    #             perm = file_info.get("permissions", "")
    #             owner = file_info.get("owner", "")
    #             path = file_info.get("path", "")
                
    #             # Check for world-writable or group-writable permissions
    #             if perm and len(perm) == 3:
    #                 if perm[2] in ['2', '3', '6', '7']:  # World writable
    #                     self.classification["permission_issues"].append({
    #                         "path": path,
    #                         "permissions": perm,
    #                         "owner": owner,
    #                         "issue": "World-writable cron file"
    #                     })
    #                 elif perm[1] in ['6', '7'] and owner != "root":  # Group writable by non-root
    #                     self.classification["permission_issues"].append({
    #                         "path": path,
    #                         "permissions": perm,
    #                         "owner": owner,
    #                         "issue": "Group-writable cron file"
    #                     })
            
        #     return True
        # except Exception as e:
        #     print(f"Error has occured: {e}")
        #     return False

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

if __name__ == "__main__":
    c = MediumAudit()
    results = c.run_audit()
    print(json.dumps(results, indent=2))
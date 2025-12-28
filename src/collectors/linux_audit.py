import subprocess, json, os
from pathlib import Path

PARENT_PATH = Path.cwd().parent.parent



class LinuxAudit:
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
                [str(PARENT_PATH /"scripts" /"basic_info_check.sh"), function_name],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            return f"ERROR: {e.stderr.strip()}"
        
    def check_accordingly(self, basename, register): 
        try:
            for severity, bins in register.items():
                if basename in bins:
                    return severity
            return "unknown"
        except Exception as e:
            print(f"Error has occured: {e}")
            return False
    

    def classify_binaries(self, path, bin_to_check):
        try:
            if bin_to_check == "suid_check":
                return self.check_accordingly(path.split('/')[-1], self.suid_classification)
            elif bin_to_check == "sgid_check":
                return self.check_accordingly(path.split('/')[-1], self.sgid_classification)
            elif bin_to_check == "world_writabable_check":
                self.check_accordingly(os.path.dirname(path), self.world_writable)
            return "unknown"
        except Exception as e:
            print(f"Error has occured: {e}")
            return False

    def calculate_binaries(self, bins_to_check):
        try:
            bins = self.run_bash(bins_to_check)
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
            for i in user_detail:
                print(i)
            return user_detail
        except Exception as e:
            print(f"Error has occured {e}")
            return False
    
    def file_system_check(self):
        try:
            list = ['suid_check', 'sgid_check', 'world_writable_check']
            for check_type in list:
                self.calculate_binaries(check_type)
            
            print(self.classification)
        except Exception as e:
            print(f'Error has occured: {e}')
            return False

main = LinuxAudit()
main.file_system_check()
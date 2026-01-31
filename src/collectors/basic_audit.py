import subprocess, json, os, platform, importlib.util, sys
from pathlib import Path

PARENT_PATH = Path(__file__).resolve().parent.parent.parent

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
            
            if not python_version >= (3,10):
                status["warning"].append(f"python version {sys.version_info.major} {sys.version_info.minor} is not compaitable")
            
            with open(PARENT_PATH / "requirements.txt", "r") as f:
                requirements = f.readlines()
                for i in requirements:
                    package = i.split('==')[0].split('>=')[0].split('>')[0].strip()
                    if package and not package.startswith('#'):
                        if importlib.util.find_spec(package.replace("-","_")) is None:
                            status["error"].append(f"Missing dependency: {package}")
                            status["is_run"] = False
        except Exception as e:
            status["error"].append(e)

        return status

    def file_system_check(self):
        try:
            list = ['suid_check', 'sgid_check', 'world_writable_check']
            for check_type in list:
                self.calculate_binaries(check_type)
            
            return self.classification
        except Exception as e:
            print(f'Error has occured: {e}')
            return False

if __name__ == "__main__":
    c = BasicAudit()
    c.file_system_check()
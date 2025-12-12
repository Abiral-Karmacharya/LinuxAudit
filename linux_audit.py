import subprocess
import json


class LinuxAudit:
    def __init__(self):
        with open('./bins.json', "r") as f:
            self.suid_classifcation = json.load(f)['suid']
        self.classification = {
            "critical": [],
            "suspicious": [],
            "unknown": [],
            "standard": []
        }
        
    def run_bash(self, function_name):
        try:
            result = subprocess.run(
                ["./bash.sh", function_name],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            return f"ERROR: {e.stderr.strip()}"
    
    def classify_binaries(self, path):
        basename = path.split('/')[-1]
        for severity, bins in self.suid_classifcation.items():
            if basename in bins:
                return severity
            
        return "unknown"


    def calculate_binaries(self, bins_to_check):
        bins = self.run_bash(bins_to_check)
        for path in bins:
            severity = self.classify_binaries(path)
            self.classification[severity].append(path)

        return True
    
    def file_system_check(self):
        list = ['suid_check']
        for i in list:
            self.calculate_binaries(i)
        
        print(self.classification)


main = LinuxAudit()
main.file_system_check()
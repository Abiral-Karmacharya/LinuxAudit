# LinuxAudit

LinuxAudit is a JavaScript-based Linux security auditing tool focused on identifying
privilege escalation risks and insecure filesystem configurations.

## Features

- Detects **SUID** and **SGID** binaries
- Identifies **world-writable files and directories**
- Classifies findings into **critical**, **suspicious**, and **standard**
- Uses configurable JSON-based rules for flexible auditing
- Designed for easy extension and automation

## What It Checks

- SUID / SGID binaries and their risk level
- World-writable paths with contextual severity
- Unknown or unexpected privileged binaries

## Requirements

- js

```bash
sudo pacman -S js
```

```bash
sudo apt install js
```

## Usage

Run the tool with sufficient privileges to allow full filesystem inspection:

```bash
sudo python /src/collector/basic_audit.py
```

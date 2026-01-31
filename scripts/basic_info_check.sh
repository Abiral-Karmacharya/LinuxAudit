#!/bin/bash

suid_check() {
    find / -path /proc -prune -o -path /sys -prune -o -path /dev -prune -o -type f \( -perm -04000  \) -exec ls -ld {} \; 2>/dev/null | awk '{print $NF}' | jq -R . | jq -s .
}

sgid_check() {
    find / -path /proc -prune -o -path /sys -prune -o -path /dev -prune -o -type f \( -perm -02000 \) -exec ls -ld {} \; 2>/dev/null | awk '{print $NF}' | jq -R . | jq -s .
}

world_writable_check() {
    find / -xdev -type d -perm -0002 -exec ls -ld {} \; 2>/dev/null \
        | awk '{print $NF}' | jq -R . | jq -s .
}

user_detail() {
    jq -n --arg un "$(whoami)" --arg uid "$(id -u)" --arg gid "$(id -g)" --arg utime "$(uptime -p)" '{Username: $un, UserID: $uid, GroupID: $gid, Uptime: $utime}'
}

# Dispatch based on argument
case "$1" in
    suid_check)
        suid_check
        ;;
    
    world_writable_check)
        world_writable_check
        ;;
    user_detail)
        user_detail
        ;;
    
    *)
        echo "Unknown function: $1" >&2
        exit 1
        ;;
esac

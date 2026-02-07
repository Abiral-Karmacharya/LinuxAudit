#!/bin/bash
cron_files_check() {
    {
        # /etc/crontab
        if [ -f /etc/crontab ]; then
            while IFS= read -r line; do
                case "$line" in
                    \#*|""|SHELL=*|PATH=*|MAILTO=*|HOME=*) continue ;;
                esac
                printf "%s\n" "/etc/crontab|system|$line"
            done < /etc/crontab 2>/dev/null
        fi
        
        # cron.d and other directories
        for dir in /etc/cron.d /etc/cron.daily /etc/cron.hourly /etc/cron.monthly /etc/cron.weekly; do
            if [ -d "$dir" ]; then
                find "$dir" -type f 2>/dev/null | while read -r file; do
                    while IFS= read -r line; do
                        case "$line" in
                            \#*|"") continue ;;
                        esac
                        printf "%s\n" "$file|system|$line"
                    done < "$file" 2>/dev/null
                done
            fi
        done
        
        # User crontabs
        for user_cron in /var/spool/cron/crontabs/* /var/spool/cron/*; do
            [ -f "$user_cron" ] || continue

            username=$(basename "$user_cron")
            while IFS= read -r line; do
                case "$line" in
                    \#*|"") continue ;;
                esac
                printf "%s\n" "$user_cron|$username|$line"
            done < "$user_cron" 2>/dev/null
        done
    } | jq -R 'split("|") | {path: .[0], user: .[1], entry: .[2]}' | jq -s .
}


case "$1" in
    cron_files_check)
        cron_files_check
        ;;
    cron_permissions_check)
        cron_permissions_check
        ;;
    systemd_timers_check)
        systemd_timers_check
        ;;
    *)
        echo "Unknown function: $1" >&2
        exit 1
        ;;
esac

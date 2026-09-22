critical_errors = ["ERROR", "CRITICAL", "FATAL"]
ip_counter = {}

with open("server.log", "r", encoding="utf-8") as file:
    for line in file:
        line_lower = line.upper()
        
        has_error = False
        for err in critical_errors:
            if err in line_lower:
                has_error = True
                break
                
        if has_error:
            parts = line.split()
            if len(parts) > 0:
                ip = parts[0]
                if ip in ip_counter:
                    ip_counter[ip] += 1
                else:
                    ip_counter[ip] = 1

with open("report.txt", "w", encoding="utf-8") as report:
    report.write("IP addresses with critical errors:\n")
    for ip, count in ip_counter.items():
        report.write(f"{ip}: {count}\n")

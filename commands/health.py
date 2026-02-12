import datetime
import time

try:
    import psutil
except ModuleNotFoundError:
    psutil = None

from commands.formatting import format_response


def get_server_status():
    if psutil is None:
        return format_response(
            "Server Health",
            [
                "CPU Usage: Unavailable",
                "Memory Usage: Unavailable",
                "Disk Usage: Unavailable",
                "CPU Temperature: Unavailable",
                "Uptime: Unavailable",
            ],
        )

    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    uptime_seconds = time.time() - psutil.boot_time()
    uptime = str(datetime.timedelta(seconds=int(uptime_seconds)))
    disk_usage = psutil.disk_usage("/").percent

    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as temp_file:
            cpu_temp = int(temp_file.read()) / 1000
    except (FileNotFoundError, PermissionError, OSError, ValueError):
        cpu_temp = None

    if cpu_temp is None:
        temp_display = "Unavailable"
    else:
        temp_display = f"{cpu_temp}°C"

    return format_response(
        "Server Health",
        [
            f"CPU Usage: {cpu_usage}%",
            f"Memory Usage: {memory_usage}%",
            f"Disk Usage: {disk_usage}%",
            f"CPU Temperature: {temp_display}",
            f"Uptime: {uptime}",
        ],
    )

import psutil
import subprocess
import shutil
from typing import Union
from sys import platform

def GetBatteryPercentage() -> float:
    return psutil.sensors_battery().percent

def GetCPUUsage() -> float:
    return psutil.cpu_percent(2)

def GetCPUPhysicalCoreCount() -> int:
    return psutil.cpu_count(logical = False)

def GetCPULogicalCoreCount() -> int:
    return psutil.cpu_count(logical = True)

def GetCPUMaxFrequency() -> int:
    return psutil.cpu_freq().max

def GetCPUMinFrequency() -> int:
    return psutil.cpu_freq().min

def GetCPUCurrentFrequency() -> int:
    return psutil.cpu_freq().current

def GetMemoryUsage() -> float:
    return psutil.virtual_memory()[2]

def GetDiskUsage() -> float:
    return float(shutil.disk_usage("/").used) / float(shutil.disk_usage("/").total)

def GetOS() -> str:
    return platform

def GetUsersLoggedOn() -> str:
    message: str = ""
    for user in psutil.users():
        message += f"{user.name} "
    return message.strip()

def GetRunningProccesses() -> str:
    message: str = ""
    for process in psutil.process_iter():
        message += f"{process.pid} {process.name()} "
    return message.strip()

def Reboot() -> str:
    if platform.system().lower() == "windows":
        subprocess.run(["shutdown", "/r", "/t", "10"], check=True)
    elif platform.system().lower() == "linux" or platform.system().lower() == "darwin":
        subprocess.run(["sudo", "shutdown", "-r", "+0.1"], check=True)
    return "rebooting"

def ProcessQuestion(question: str) -> Union[str, int]:
    try:
        match question:
            case "BatteryP":
                return str(GetBatteryPercentage())
            case "CPUP":
                return str(GetCPUUsage())
            case "CPUPC":
                return str(GetCPUPhysicalCoreCount())
            case "CPULC":
                return str(GetCPULogicalCoreCount())
            case "CPUFB":
                return str(GetCPUMaxFrequency())
            case "CPUFS":
                return str(GetCPUMinFrequency())
            case "CPUFC":
                return str(GetCPUCurrentFrequency())
            case "MemP":
                return str(GetMemoryUsage())
            case "DiskP":
                return str(GetDiskUsage())
            case "UserL":
                return str(GetUsersLoggedOn())
            case "OS":
                return str(GetOS())
            case "ProcR":
                return str(GetRunningProccesses())
            case "Reboot":
                return str(Reboot())
        return 0
    except:
        return 1
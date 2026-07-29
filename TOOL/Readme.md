


# DoS Launcher

> **Educational Lab Tool** for studying Denial-of-Service (DoS) concepts in a **private, isolated, and authorized** virtual lab.

---

## Overview

`dos_launcher.py` is a Python 3 script designed to automate multiple DoS testing techniques against machines that **you own or have explicit permission to test**.

The launcher runs several attack methods simultaneously using:

* **Metasploit Framework (****`msfconsole`****)**
* **hping3**
* **ping**

It was created for use with **Kali Linux** and **Metasploitable 2** inside an isolated virtual network (Host-Only or Internal Network).

> **Warning**
>
> This project is intended **only for cybersecurity education and defensive testing in authorized lab environments.**
> Never use it against systems you do not own or have permission to test.

---

# Features

* Interactive target IP prompt
* 5-second safety countdown before launch
* Multi-threaded execution
* Runs multiple DoS techniques simultaneously
* Graceful shutdown with **Ctrl+C**
* Automatically terminates spawned processes

---

# Requirements

| Requirement                           | Purpose                                     |
| ------------------------------------- | ------------------------------------------- |
| Kali Linux (or similar)               | Recommended operating system                |
| Python 3                              | Runs the launcher                           |
| Root privileges (`sudo`)            | Required for packet generation              |
| Metasploit Framework                  | Used for supported Metasploit modules       |
| hping3                                | Packet generation                           |
| Target VM (example: Metasploitable 2) | Authorized testing target                   |
| Isolated virtual network              | Prevents unintended traffic outside the lab |

---

# Installation

Update packages:

```bash
sudo apt update
```

```bash
git clone https://github.com/ghost-1920/Dos-Ddos_Launcher.git
```

Install required tools:

```bash
sudo apt install -y metasploit-framework hping3
```

---

# Usage

Navigate to the project directory:

```bash
 cd Dos-Ddos_Launcher && cd TOOL 
```

(Optional) Make the script executable:

```bash
chmod +x dos_launcher.py
```

Run as root:

```bash
sudo python3 dos_launcher.py
```

---

# Typical Workflow

1. Launch the script.
2. Enter the target IP address.
3. Review the warning message.
4. Wait for the countdown.
5. The configured test routines begin.
6. Press **Ctrl+C** when finished.
7. The launcher terminates spawned processes and exits.

Example:

```text
[?] Enter target IP address: 192.168.56.101

[+] Target set to: 192.168.56.101

[!] Starting in 5 seconds...

5...
4...
3...
2...
1...

[+] Test routines started.

[*] Press Ctrl+C to stop.
```

---

# Stopping the Launcher

Press:

```text
Ctrl + C
```

The launcher will:

* Stop all running threads
* Termatively end child processes
* Clean up remaining Metasploit and hping3 processes
* Exit safely

---

# Included Test Techniques

The launcher coordinates multiple network stress-testing methods in parallel to demonstrate how different traffic patterns affect a system under load. The implementation uses Metasploit modules together with packet-generation utilities.

---

# Monitoring the Target

During testing, you can observe the target from another terminal or using wireshark.

Examples include:

```bash
ping <target_ip>
```

```bash
nc -zv <target_ip> 22
```

```bash
nc -zv <target_ip> 80
```

```bash
nmap -Pn -p 21,22,80,445 <target_ip>
```

You can use Wireshark to observer Dos Attack:

```bash
ip-addr == <target.ip>
```

On the target VM you may also monitor system resources:

```bash
top
```

```bash
free -m
```

Typical indicators during controlled lab testing may include:

* Increased latency
* Packet loss
* Slower service response
* Elevated CPU usage
* Increased memory consumption

---

# Cleanup

After stopping the launcher:

Check for remaining processes:

```bash
ps aux | grep -E 'msfconsole|hping3|ping -f' | grep -v grep
```

If necessary:

```bash
sudo pkill -9 -f msfconsole
```

```bash
sudo pkill -9 -f hping3
```

If the virtual machine becomes unresponsive, reset it and restore a clean snapshot before additional testing.

---

# Configuration

The script can be customized by editing `dos_launcher.py`.

Common adjustments include:

* Network interface used by Metasploit
* Countdown duration
* Thread configuration
* Individual test routines
* Target-specific settings

---

# Safety Guidelines

* Only test systems you own or are explicitly authorized to assess.
* Use a private Host-Only or Internal virtual network.
* Never target public systems or Internet hosts.
* Snapshot virtual machines before testing.
* Expect high CPU and network usage during experiments.
* Restore your lab environment after heavy testing.

---

# Troubleshooting

| Problem                              | Solution                                            |
| ------------------------------------ | --------------------------------------------------- |
| Permission denied                    | Run with`sudo`                                    |
| `hping3` missing                   | Install with`sudo apt install hping3`             |
| Metasploit initialization is slow    | Launch`msfconsole` once before running the script |
| Target not responding as expected    | Verify IP address and lab network configuration     |
| Launcher leaves background processes | Use`pkill` commands shown above                   |
| Host machine becomes slow            | Stop the launcher and reduce workload               |
| Target VM freezes                    | Reset or restore a VM snapshot                      |

---

# Disclaimer

This Tool is provided **solely for educational purposes and authorized security testing** within isolated laboratory environments.

The author assumes **no responsibility** for misuse, unauthorized testing, or damage resulting from improper use. Always obtain explicit permission before conducting any security assessment.

---

## License

Use responsibly for cybersecurity education and defensive research.

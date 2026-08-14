# Module 2 — Digital Forensics & Incident Response

## The Case of the Stolen Szechuan Sauce

This project was developed as part of **Cybersecurity Laboratories — Module 2** at the **University of Minho**.

The objective of this module was to conduct a complete **Digital Forensics and Incident Response (DFIR)** investigation based on the DFIR Madness case **"The Case of the Stolen Szechuan Sauce"**.

The scenario simulates a real-world security incident in which a confidential document — the Szechuan Sauce recipe — was discovered on the dark web. The investigation aimed to determine how the attacker entered the network, what systems were compromised, which malware was deployed, how persistence was established, whether lateral movement occurred, and which sensitive files were accessed or exfiltrated.

The investigation correlated evidence from:

- Network traffic
- Volatile memory
- Disk images
- Windows Event Logs
- Windows Registry
- NTFS artifacts
- Browser history
- `.lnk` files
- USN Journal
- Malware analysis
- Threat intelligence sources

---

# 1. Investigation Objectives

The investigation was designed to answer the following questions:

- What operating systems were running on the server and workstation?
- Was an intrusion successful?
- What was the initial access vector?
- Was malware used?
- Which process was malicious?
- What infrastructure was used to deliver the malware?
- What Command & Control infrastructure was used?
- Was persistence established?
- Which malicious IP addresses were involved?
- Did the attacker move laterally to other systems?
- Were sensitive files accessed?
- Were sensitive files exfiltrated?
- Was the Szechuan Sauce recipe stolen?
- Were additional confidential files compromised?
- What was the attack timeline?
- What was the last known contact with the attacker?
- Which architectural changes could have prevented or limited the incident?

---

# 2. Investigation Methodology

The investigation followed a structured DFIR workflow.

```text
Forensic Evidence
       │
       ├── Network Capture (PCAP)
       ├── Memory Images
       ├── Disk Images (E01)
       ├── Windows Event Logs
       ├── Registry Hives
       └── File System Artifacts
              │
              ▼
     Initial Investigation
              │
      ┌───────┼────────┐
      ▼       ▼        ▼
   Network  Memory    Disk
  Analysis  Analysis  Analysis
      │       │        │
      └───────┼────────┘
              ▼
        Artifact Correlation
              │
              ▼
       Timeline Reconstruction
              │
              ▼
        Incident Reconstruction
```

The analysis began with network traffic, followed by volatile memory analysis and disk forensics. Evidence from the different sources was then correlated to reconstruct the complete attack chain.

---

# 3. Forensic Evidence

The case included several types of forensic artifacts.

## Disk Evidence

Forensic disk images in the **E01** format were provided for the Domain Controller and Desktop workstation. These images were analyzed using tools including Autopsy, Arsenal Image Mounter and Eric Zimmerman's Tools.

## Memory Evidence

Memory captures from the compromised machines were analyzed to identify running processes, network connections, injected code, suspicious memory regions, malware artifacts, process relationships and command-line arguments.

## Network Evidence

The network capture was analyzed for suspicious IP addresses, RDP connections, malware downloads, Command & Control traffic, internal lateral movement and data exfiltration.

## Windows Artifacts

Several Windows forensic artifacts were analyzed, including:

- `Security.evtx`
- Terminal Services logs
- Windows Registry hives
- Autoruns
- `.lnk` files
- Browser history
- NTFS USN Journal
- Recent files
- Service configuration

---

# 4. Forensic Toolkit

A broad set of DFIR tools was used throughout the investigation.

| Category | Tools |
|---|---|
| Network Forensics | Wireshark, NetworkMiner, capinfos |
| Memory Forensics | Volatility 3 |
| Disk Forensics | Autopsy, Arsenal Image Mounter |
| Windows Forensics | Eric Zimmerman's Tools, Timeline Explorer, Registry Explorer |
| Event Log Analysis | EvtxECmd |
| Registry Analysis | RECmd |
| NTFS Forensics | MFTECmd |
| Malware Analysis | REMnux, ClamAV, FLOSS, capa |
| Dynamic Malware Analysis | Joe Sandbox |
| Payload Analysis | CyberChef |
| Threat Intelligence | VirusTotal, AlienVault OTX |
| DFIR Environment | SIFT Workstation |
| Automation | Python, PowerShell |

---

# 5. Network Forensics

## Wireshark

Wireshark was used as the starting point for the network investigation.

The IPv4 conversation statistics revealed two internal systems:

```text
10.42.85.10   CITADEL-DC01
10.42.85.115  DESKTOP-SDN1RPT
```

A particularly suspicious conversation was identified between `194.61.24.102` and the Domain Controller `10.42.85.10`.

Approximately **44 MB of traffic** was exchanged between the external IP address and the Domain Controller. Further analysis showed that most of this communication occurred over `TCP/3389`, corresponding to **Remote Desktop Protocol (RDP)**.

Direct Internet-facing RDP access to a Domain Controller was identified as a critical security weakness.

## NetworkMiner

NetworkMiner was used to extract files, credentials and other forensic artifacts from the PCAP.

Analysis identified two suspicious executable transfers:

```text
coreupdater.exe
coreupdater[1].exe
```

The executable was downloaded from `194.61.24.102` and delivered to both the Domain Controller and the Desktop.

NetworkMiner also identified suspicious RDP cookies:

```text
mstshash=nmap
mstshash=Administrator
```

These artifacts provided evidence of scanning and brute-force activity against RDP.

---

# 6. Initial Access

The initial access vector was identified as an **RDP brute-force attack**.

Windows Security Event Logs were analyzed using `EvtxECmd` and PowerShell. Filtering for `Event ID 4625` revealed more than **95 failed authentication attempts** against the `Administrator` account in approximately 21 seconds.

The attack began around `2020-09-19 02:21:25 UTC` and the failed authentication sequence ended around `2020-09-19 02:21:46 UTC`.

The evidence confirms an automated brute-force attack against RDP.

---

# 7. Malware Analysis

## coreupdater.exe

Shortly after the RDP compromise, the attacker downloaded `coreupdater.exe` to the Domain Controller.

The PCAP analysis identified the download at approximately `2020-09-19 02:24:06 UTC`.

## VirusTotal

The SHA-256 hash of `coreupdater.exe` was calculated and submitted to VirusTotal. The file was detected as malicious by a large majority of antivirus engines and was associated with the **Metasploit Meterpreter** framework.

## Meterpreter

The malware used during the intrusion was identified as **Meterpreter**.

Meterpreter provided capabilities including:

- Remote system access
- Process migration
- Encrypted communication
- Credential theft
- Privilege abuse
- Lateral movement
- Command execution

---

# 8. Memory Forensics

Memory analysis was performed using **Volatility 3**.

The following plugins were particularly relevant:

```text
windows.info
windows.netscan
windows.malfind
windows.pstree
windows.cmdline
```

`windows.info` was used to recover general operating-system and memory-image information.

`windows.netscan` was used to identify active and historical network connections.

`windows.malfind` was used to detect suspicious executable memory regions and injected code.

`windows.pstree` was used to reconstruct process relationships and identify abnormal process behavior.

`windows.cmdline` was used to inspect process paths and command-line arguments.

---

# 9. Process Injection

The investigation identified the legitimate Windows process `spoolsv.exe` containing injected Meterpreter code.

```text
coreupdater.exe
        │
        ▼
    Meterpreter
        │
        ▼
Process Migration
        │
        ▼
    spoolsv.exe
```

The malicious executable was downloaded at approximately `02:24:06 UTC` and by `02:29:40 UTC` Meterpreter code was already present inside `spoolsv.exe`.

This demonstrated that the attacker migrated execution from the original malicious process into a legitimate Windows process.

---

# 10. FLOSS Analysis

**FLOSS — FireEye Labs Obfuscated String Solver** was used to extract both static and obfuscated strings from malware and memory dumps.

The analysis provided additional Indicators of Compromise and information about Meterpreter capabilities. FLOSS was particularly useful because normal string-extraction tools could not recover all of the obfuscated content.

---

# 11. ClamAV

ClamAV was used against memory dumps extracted during the investigation.

It identified malicious Meterpreter-related memory regions such as:

```text
Win.Exploit.Meterpreter
Win.Malware.Meterpreter
```

This provided another independent source confirming the presence of Meterpreter.

---

# 12. CyberChef and capa

A suspicious Base64-encoded PowerShell payload was recovered from the Windows Registry.

**CyberChef** was used to decode the payload. The decoded content contained behavior involving APIs such as `VirtualAlloc` and `CreateThread`, indicating in-memory shellcode execution.

**capa** was then used to analyze the capabilities of the recovered shellcode.

---

# 13. Persistence

Two persistence mechanisms were identified on the Domain Controller.

## 13.1. Registry-Based Fileless Persistence

A suspicious PowerShell command was identified in:

```text
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
```

The command executed a Base64-encoded payload in hidden mode. The payload allocated memory and executed shellcode directly in memory.

## 13.2. Malicious Windows Service

The second persistence mechanism involved `coreupdater.exe` being installed as a Windows service under:

```text
HKLM\System\CurrentControlSet\Services
```

Because Windows services can start automatically with the operating system, this provided persistent access after a reboot.

Dynamic analysis with Joe Sandbox further confirmed malicious behavior and associated the sample with the C2 infrastructure.

---

# 14. Command & Control

The investigation identified the Meterpreter Command & Control server as:

```text
203.78.103.109:443
```

Meterpreter communicated with the attacker using encrypted traffic. Threat-intelligence checks were also performed using VirusTotal and AlienVault OTX.

---

# 15. Lateral Movement

After compromising the Domain Controller, the attacker moved laterally to:

```text
DESKTOP-SDN1RPT
10.42.85.115
```

The lateral movement occurred using **RDP** and compromised administrator credentials.

Windows Terminal Services logs were analyzed to reconstruct the session. Important RDP Event IDs included:

```text
21
22
23
24
41
42
```

`Event ID 21` was particularly important because it records a successful RDP session logon.

Evidence confirmed that the compromised Domain Controller `10.42.85.10` was used as the source of an authenticated RDP session to the Desktop.

---

# 16. Windows Event Log Analysis

Windows Event Logs played a central role in reconstructing the incident.

The investigation included analysis of:

```text
Security.evtx
Microsoft-Windows-TerminalServices-LocalSessionManager
```

The logs provided evidence of failed authentication attempts, successful logons, RDP session creation, RDP session termination, lateral movement and attacker session timing.

Python scripts were created to automate parts of this analysis.

---

# 17. Disk Forensics

## Autopsy

Autopsy was used to analyze the E01 disk images and identify operating-system information, user accounts, recently accessed files, browser history, installed software, USB history and sensitive files.

The Domain Controller was identified as running:

```text
Windows Server 2012 R2 Standard Evaluation
AMD64
```

The Desktop was identified as running:

```text
Windows 10 Enterprise Evaluation
```

## Arsenal Image Mounter

Because exporting artifacts directly from Autopsy was too slow in the available environment, **Arsenal Image Mounter** was used to mount E01 forensic images as local disks.

This provided direct access to artifacts such as `Security.evtx`, the `SYSTEM` Registry hive and the USN Journal.

---

# 18. Windows Registry Forensics

Registry analysis was performed using **RECmd** and Registry Explorer.

One important finding was the server's timezone configuration. The Domain Controller was configured for `Pacific Standard Time`, with an active offset inconsistent with the expected Colorado timezone.

This required special care when normalizing timestamps during the reconstruction of the incident.

Registry analysis was also essential for identifying the attacker's persistence mechanisms.

---

# 19. NTFS Forensics and USN Journal

The NTFS **USN Journal** was analyzed using `MFTECmd`.

This provided evidence of file creation, renaming and deletion.

Two particularly important archives were identified:

```text
Secret.zip
loot.zip
```

These artifacts were important in demonstrating the collection and exfiltration of sensitive data.

---

# 20. `.lnk` File Analysis

Windows shortcut (`.lnk`) files were analyzed to determine which files had been opened during the attack.

The user's `Recent` directory contained shortcuts pointing to files accessed during the incident. This provided additional evidence that sensitive files had been opened by the attacker.

---

# 21. Data Access

The attacker accessed the confidential network share:

```text
C:\FileShare\Secret
```

Evidence showed access to multiple sensitive files, including:

```text
Szechuan Sauce.txt
PortalGunPlans.txt
SECRET_beth.txt
Beth_Secret.txt
```

The `Szechuan Sauce.txt` file was accessed at approximately `2020-09-19 02:32:21 UTC`.

---

# 22. Data Exfiltration

Evidence from the USN Journal showed the creation of `Secret.zip` on the Domain Controller at approximately `2020-09-19 02:32:39 UTC`, followed by its deletion.

After moving laterally to the Desktop, another archive named `loot.zip` was created at approximately `2020-09-19 02:46:18 UTC` and deleted shortly afterwards.

This creation → exfiltration → deletion pattern was consistent with an attacker attempting to remove evidence after extracting data.

---

# 23. Reconstructed Attack Chain

```text
Internet
   │
   ▼
RDP exposed on TCP/3389
   │
   ▼
Automated RDP Brute Force
   │
   ▼
Administrator Account Compromised
   │
   ▼
Domain Controller Compromise
CITADEL-DC01 — 10.42.85.10
   │
   ▼
coreupdater.exe Downloaded
   │
   ▼
Meterpreter Execution
   │
   ▼
Process Migration
   │
   ▼
spoolsv.exe Injection
   │
   ├───────────────► C2: 203.78.103.109:443
   │
   ▼
Persistence
   │
   ├── Registry Run Key
   └── Malicious Windows Service
   │
   ▼
Sensitive File Access
   │
   ▼
Secret.zip
   │
   ▼
Data Exfiltration
   │
   ▼
Lateral Movement via RDP
   │
   ▼
DESKTOP-SDN1RPT — 10.42.85.115
   │
   ▼
Additional File Access
   │
   ▼
loot.zip
   │
   ▼
Additional Data Exfiltration
```

---

# 24. Attack Timeline

| Time — UTC | Evidence | Event |
|---|---|---|
| 02:21:25 | `Security.evtx` | RDP brute-force attack begins |
| 02:21:46 | `Security.evtx` | Brute-force sequence ends |
| 02:23:41 | Browser History | Access to attacker infrastructure |
| 02:24:06 | PCAP / NetworkMiner | `coreupdater.exe` downloaded to Domain Controller |
| 02:29:40 | Volatility 3 | Meterpreter code identified inside `spoolsv.exe` |
| 02:32:02 | Browser History | `PortalGunPlans.txt` accessed |
| 02:32:13 | Browser History | `SECRET_beth.txt` accessed |
| 02:32:21 | Browser History | `Szechuan Sauce.txt` accessed |
| 02:32:39 | USN Journal | `Secret.zip` created |
| 02:34:18 | USN Journal | `Secret.zip` deleted |
| 02:35:07 | Browser History | `Beth_Secret.txt` accessed |
| 02:46:18 | USN Journal | `loot.zip` created on Desktop |
| 02:47:09 | USN Journal | `loot.zip` deleted |

> The investigation identified timezone inconsistencies on the Domain Controller. Times in the reconstructed timeline were normalized during forensic analysis.

---

# 25. Indicators of Compromise

## Network Indicators

| Indicator | Description |
|---|---|
| `194.61.24.102` | External attacker / malware delivery infrastructure |
| `203.78.103.109` | Meterpreter Command & Control server |
| `TCP/3389` | RDP used for initial access and lateral movement |
| `TCP/443` | Encrypted C2 communication |

## Host Indicators

```text
C:\Windows\System32\coreupdater.exe
C:\Windows\System32\spoolsv.exe
```

## Registry Indicators

```text
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
HKLM\System\CurrentControlSet\Services
```

## File Indicators

```text
coreupdater.exe
Secret.zip
loot.zip
```

---

# 26. Compromised Systems

## Domain Controller

```text
Hostname: CITADEL-DC01
IP:       10.42.85.10
Domain:   c137.local
OS:       Windows Server 2012 R2
```

## Desktop

```text
Hostname: DESKTOP-SDN1RPT
IP:       10.42.85.115
Domain:   c137.local
OS:       Windows 10 Enterprise
```

---

# 27. Custom Analysis Scripts

Several Python scripts were developed to assist with forensic artifact processing and timeline reconstruction.

```text
script1_terminal_services_events.py
script2_lnk_files.py
script3_lateral_movement.py
script4_event21_xml.py
script5_security_evtx_desktop.py
script6_rdp_summary_table.py
script7_aba_patterns.py
```

- `script1_terminal_services_events.py` — Processes Terminal Services artifacts related to RDP sessions.
- `script2_lnk_files.py` — Supports analysis of Windows `.lnk` artifacts associated with recently accessed files.
- `script3_lateral_movement.py` — Supports investigation of lateral movement between compromised systems.
- `script4_event21_xml.py` — Extracts and processes information associated with Event ID 21.
- `script5_security_evtx_desktop.py` — Supports analysis of Windows Security Event Logs from the Desktop.
- `script6_rdp_summary_table.py` — Consolidates RDP-related event information into a summary representation.
- `script7_aba_patterns.py` — Additional artifact-processing script developed during the forensic investigation.

---

# 28. Project Structure

```text
module-2-digital-forensics-incident-response/
│
├── README.md
├── lcib2526_report_pg59797_pg60307_pg60986.pdf
├── lcib2526_presentation_pg59797_pg60307_pg60986.pdf
├── script1_terminal_services_events.py
├── script2_lnk_files.py
├── script3_lateral_movement.py
├── script4_event21_xml.py
├── script5_security_evtx_desktop.py
├── script6_rdp_summary_table.py
└── script7_aba_patterns.py
```

---

# 29. Key Findings

The investigation established that:

1. The Domain Controller was directly exposing RDP to the Internet.
2. The attacker performed an automated brute-force attack against the Administrator account.
3. The Domain Controller was successfully compromised.
4. `coreupdater.exe` was downloaded from attacker-controlled infrastructure.
5. The executable deployed a Meterpreter payload.
6. Meterpreter migrated into the legitimate `spoolsv.exe` process.
7. Encrypted C2 communication was established with `203.78.103.109:443`.
8. Two persistence mechanisms were identified.
9. Sensitive files on the Domain Controller were accessed.
10. Sensitive data was collected into `Secret.zip`.
11. The attacker moved laterally to the Desktop using RDP.
12. Additional sensitive data was collected into `loot.zip`.
13. The archives were deleted after use, indicating an attempt to remove forensic evidence.
14. Correlation across network, memory, disk and Windows artifacts allowed the complete incident to be reconstructed.

---

# 30. Security Recommendations

## Remove Internet-Facing RDP

RDP should never be directly exposed to the Internet on critical infrastructure such as a Domain Controller.

Remote administrative access should instead use mechanisms such as:

```text
VPN
   ↓
MFA
   ↓
Controlled Administrative Network
   ↓
Management Host / Jump Server
```

## Network Segmentation

The Domain Controller should be isolated from user workstations and external-facing systems.

## Multi-Factor Authentication

Administrative accounts should require MFA for remote access.

## Account Protection

Controls should include:

- Account lockout
- Authentication rate limiting
- Strong password policies
- Monitoring of failed authentication events

Particular attention should be paid to `Windows Event ID 4625`.

## SIEM Monitoring

Centralized security monitoring should detect patterns such as:

- Large numbers of failed RDP logins
- New Windows services
- Suspicious Registry Run keys
- Encoded PowerShell commands
- Process injection
- Unusual outbound connections
- Large file archives created before outbound transfers
- RDP connections between unusual internal systems

## Endpoint Detection

EDR or equivalent endpoint monitoring should be deployed to detect:

- Process injection
- Meterpreter behavior
- Suspicious PowerShell
- Process migration
- Persistence through Windows services
- Registry-based persistence

---

# 31. Investigation Challenges

## ARM Compatibility

Some members of the investigation environment used ARM hardware. The SIFT Workstation and REMnux images used during the project were only available for x86-64 in the tested setup, requiring alternative infrastructure and remote access to an x86-64 system.

## SIFT + REMnux

SIFT Workstation was used as the primary forensic environment. REMnux was installed as an addon:

```bash
sudo remnux install --mode=addon
sudo remnux update
sudo remnux upgrade
```

## Autopsy Performance

Autopsy proved slow when processing the forensic disk images in the available virtual-machine environment.

Instead of exporting large artifacts directly through Autopsy, the team used Arsenal Image Mounter to mount the E01 images directly and then processed artifacts with `EvtxECmd`, `RECmd` and `MFTECmd`.

---

# 32. Skills Demonstrated

This project demonstrates practical experience in:

- Digital Forensics
- Incident Response
- Network Forensics
- Memory Forensics
- Disk Forensics
- Windows Forensics
- Malware Analysis
- Threat Hunting
- Timeline Reconstruction
- Windows Event Log Analysis
- Registry Forensics
- NTFS Forensics
- PCAP Analysis
- Process Injection Analysis
- Indicators of Compromise
- Command & Control Analysis
- Persistence Analysis
- Lateral Movement Analysis
- Data Exfiltration Analysis
- Python Automation
- PowerShell
- Security Architecture Analysis

---

# 33. Reports

The repository includes the complete investigation report:

[`lcib2526_report_pg59797_pg60307_pg60986.pdf`](./lcib2526_report_pg59797_pg60307_pg60986.pdf)

and the project presentation:

[`lcib2526_presentation_pg59797_pg60307_pg60986.pdf`](./lcib2526_presentation_pg59797_pg60307_pg60986.pdf)

The report contains the complete forensic investigation, evidence, screenshots, commands, reasoning and reconstructed timeline.

---

# 34. Academic Context

**Course:** Cybersecurity Laboratories  
**Module:** Module 2 — Digital Forensics & Incident Response  
**Institution:** University of Minho — School of Engineering  
**Academic Year:** 2025/2026

---

# 35. Disclaimer

This repository documents an **academic digital-forensics investigation performed in a controlled environment**.

Malware names, IP addresses, attack techniques and forensic evidence are included exclusively for educational, defensive and research purposes.

Malicious binaries, private credentials and original sensitive forensic evidence are intentionally not distributed through this repository.

# Indicators of Compromise

## Network

- `194.61.24.102` — RDP / malware delivery infrastructure
- `203.78.103.109` — Meterpreter C2
- TCP/3389 — RDP
- TCP/443 — C2 communication

## Malware

- `coreupdater.exe`
- Meterpreter
- Injected process: `spoolsv.exe`

## Persistence

- PowerShell payload stored in:
  `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`

- `coreupdater.exe` installed as a Windows service

## Compromised Systems

- `CITADEL-DC01` — Domain Controller
- `DESKTOP-SDN1RPT` — Workstation

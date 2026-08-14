# Script 6 - Tabela resumo eventos RDP (03:36 e 03:52)
# Executar na SIFT Workstation com a imagem do Desktop montada

from Evtx.Evtx import Evtx
from Evtx.Views import evtx_file_xml_view
import re

print(f"{'EventID':<10} {'Hora (UTC)':<35} {'Utilizador':<25} {'IP Origem':<20} {'Significado'}")
print('-' * 110)

significado = {
    '21': 'Logon RDP bem-sucedido',
    '22': 'Shell RDP iniciada',
    '41': 'Sessao RDP iniciada',
    '42': 'Sessao RDP reconectada',
    '23': 'Sessao RDP terminada',
    '24': 'Sessao RDP desligada',
}

with Evtx('/mnt/desktop/Windows/System32/winevt/Logs/Microsoft-Windows-TerminalServices-LocalSessionManager%40Operational.evtx') as log:
    for xml, record in evtx_file_xml_view(log):
        if '03:36' in xml or '03:52' in xml:
            eventid = re.search(r'EventID Qualifiers="">(\d+)<', xml)
            time = re.search(r'SystemTime="(.*?)"', xml)
            user = re.search(r'User>(.*?)<', xml)
            ip = re.search(r'Address>(.*?)<', xml)
            if eventid:
                print(f'{eventid.group(1):<10} {time.group(1) if time else "?":<35} {user.group(1) if user else "?":<25} {ip.group(1) if ip else "-":<20} {significado.get(eventid.group(1), "?")}')

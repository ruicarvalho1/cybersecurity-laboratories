# Script 3 - Prova de movimento lateral (Event ID 21)
# Executar na SIFT Workstation com a imagem do Desktop montada

from Evtx.Evtx import Evtx
from Evtx.Views import evtx_file_xml_view

with Evtx('/mnt/desktop/Windows/System32/winevt/Logs/Microsoft-Windows-TerminalServices-LocalSessionManager%40Operational.evtx') as log:
    for xml, record in evtx_file_xml_view(log):
        if 'EventID Qualifiers="">21<' in xml and '10.42.85.10' in xml:
            print('=== PROVA DE MOVIMENTO LATERAL ===')
            print('Event ID  : 21 - Remote Desktop Services: Session logon succeeded')
            print('Maquina   : DESKTOP-SDN1RPT.C137.local')
            print('Utilizador: C137\\Administrator')
            print('IP Origem : 10.42.85.10 (Domain Controller comprometido)')
            print('Hora UTC  : 2020-09-19 03:36:25')

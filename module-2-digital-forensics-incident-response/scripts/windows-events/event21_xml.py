# Script 4 - Evento XML completo Event ID 21 (03:36)
# Executar na SIFT Workstation com a imagem do Desktop montada

from Evtx.Evtx import Evtx
from Evtx.Views import evtx_file_xml_view

with Evtx('/mnt/desktop/Windows/System32/winevt/Logs/Microsoft-Windows-TerminalServices-LocalSessionManager%40Operational.evtx') as log:
    for xml, record in evtx_file_xml_view(log):
        if 'EventID Qualifiers="">21<' in xml and '03:36' in xml:
            print(xml)

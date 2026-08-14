# Script 1 - Eventos Terminal Services (Event IDs 23, 24, 39, 40)
# Executar na SIFT Workstation com a imagem do Desktop montada

python3 -c "
from Evtx.Evtx import Evtx
from Evtx.Views import evtx_file_xml_view
import re
with Evtx('/mnt/desktop/Windows/System32/winevt/Logs/Microsoft-Windows-TerminalServices-LocalSessionManager%40Operational.evtx') as log:
    for xml, record in evtx_file_xml_view(log):
        if '2020-09-19' in xml:
            eventid = re.search(r'EventID Qualifiers=\"\">(\d+)<', xml)
            time = re.search(r'SystemTime=\"(.*?)\"', xml)
            user = re.search(r'User>(.*?)<', xml)
            if eventid and eventid.group(1) in ['23','24','39','40']:
                print(f'EventID: {eventid.group(1)} | Hora: {time.group(1) if time else \"?\"} | User: {user.group(1) if user else \"?\"}')
"

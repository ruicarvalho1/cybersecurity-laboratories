# Script 5 - Event ID 4634/4647 Security.evtx Desktop
# Primeiro copiar o ficheiro Security.evtx do Desktop:
# sudo cp '/mnt/desktop/Windows/System32/winevt/Logs/Security.evtx' /home/sansforensics/trabalho/Security_desktop.evtx

from Evtx.Evtx import Evtx
from Evtx.Views import evtx_file_xml_view
import re

with Evtx('/home/sansforensics/trabalho/Security_desktop.evtx') as log:
    for xml, record in evtx_file_xml_view(log):
        if ('4634' in xml or '4647' in xml) and '2020-09-19' in xml:
            eventid = re.search(r'EventID Qualifiers="">(\d+)<', xml)
            time = re.search(r'SystemTime="(.*?)"', xml)
            user = re.search(r'TargetUserName>(.*?)<', xml)
            if eventid:
                print(f'EventID: {eventid.group(1)} | Hora: {time.group(1) if time else "?"} | User: {user.group(1) if user else "?"}')

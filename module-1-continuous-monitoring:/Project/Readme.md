# Monitoring CA Server

## Descrição Geral

Para este módulo desenvolvemos uma camada de **monitorização da segurança em tempo real**,sobre o sistema do projeto desenvolvido no semestre anterior. O projeto original implementava uma infraestrutura de **Autoridade de Certificação (CA)** com os componentes `CA_Server`, `Login_Client`, `Auction_Client`, `Peer_Server`, `TSA_Server` e `Blockchain`.

---

## O que é Novo — `Monitoring_CA_Server`

A pasta `Monitoring_CA_Server` é o novo componente o desenvolvido neste semestre e é composto pelos seguintes ficheiros:

- **`scripts/ca_logger.py`** — Módulo de logging que regista eventos de segurança do CA Server em formato JSON Lines (`logs/ca_server/events.jsonl`), com mapeamento para o framework MITRE ATT&CK.

- **`scripts/integrity_monitor.py`** — Script que corre em loop contínuo e monitoriza a base de dados PostgreSQL do CA Server, detetando adulteração de certificados e ligações externas não autorizadas.

- **`scripts/simulate_attacks_db.py`** — Simulador de ataques para testar o sistema de deteção, com 3 cenários: substituição do certificado da CA, modificação de certificado de utilizador e simulação de exfiltração de dados.

- **`docker-compose.yml`** — Levanta a stack de monitorização com Elasticsearch (armazenamento de logs), Filebeat (recolha de logs) e Grafana (dashboards e alertas por email).

- **`config/filebeat/filebeat.yml`** — Configura o Filebeat para monitorizar os logs do CA Server e enviá-los para o Elasticsearch.

- **`config/grafana/provisioning/elasticsearch.yml`** — Provisiona automaticamente o datasource Elasticsearch no Grafana.

- **`config/grafana/provisioning/dashboard.yml`** — Dashboards no Grafana.

---

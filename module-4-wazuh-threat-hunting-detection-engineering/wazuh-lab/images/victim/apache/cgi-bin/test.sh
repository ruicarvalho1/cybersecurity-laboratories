#!/bin/bash
# Trivial CGI script. The Shellshock signature lives in the request envelope
# (a () { :; }; payload in any header that bash exports as an env var), not
# in the script body — Wazuh detects it from access.log.
echo "Content-Type: text/plain"
echo
echo "lab cgi ok"
echo "host: $(hostname)"
echo "date: $(date -u +%FT%TZ)"

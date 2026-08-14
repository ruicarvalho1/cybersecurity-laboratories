#!/bin/bash
echo "Content-Type: text/html"
echo ""

HOSTNAME=$(hostname)
DATE=$(date -u +"%-d %b %Y %H:%M UTC")
UPTIME=$(uptime -p 2>/dev/null | sed 's/^up //' || uptime)
LOAD=$(awk '{print $1", "$2", "$3}' /proc/loadavg)
MEM=$(free -h 2>/dev/null | awk '/^Mem:/{print $3" / "$2}' || echo "n/a")
KERNEL=$(uname -r)
APACHE_VER=$(apache2 -v 2>/dev/null | head -1 | sed 's/Server version: //')

cat <<HTML
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CorpNet — System status</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; background: #f4f5f7; color: #333; }
    header { background: #0052cc; color: white; padding: 12px 24px; }
    header h1 { margin: 0; font-size: 1.15rem; }
    nav { background: #fff; border-bottom: 1px solid #ddd; padding: 0 24px; }
    nav a { display: inline-block; padding: 11px 14px; text-decoration: none; color: #0052cc; font-size: .88rem; }
    .container { max-width: 700px; margin: 28px auto; padding: 0 24px; }
    .card { background: #fff; border: 1px solid #ddd; border-radius: 4px; padding: 18px 20px; }
    h2 { margin-top: 0; font-size: .8rem; color: #666; text-transform: uppercase; letter-spacing: .06em; }
    table { width: 100%; border-collapse: collapse; font-size: .88rem; }
    th { text-align: left; padding: 7px 10px; background: #f4f5f7; border-bottom: 2px solid #ddd; }
    td { padding: 7px 10px; border-bottom: 1px solid #eee; font-family: monospace; }
    td:first-child { font-family: Arial, sans-serif; color: #555; }
    tr:last-child td { border-bottom: none; }
    .dot { display:inline-block; width:8px; height:8px; border-radius:50%; background:#4caf50; margin-right:6px; }
    footer { text-align: center; font-size: .73rem; color: #aaa; padding: 22px; }
  </style>
</head>
<body>
<header><h1>CorpNet Internal Portal</h1></header>
<nav>
  <a href="/">Home</a>
  <a href="/employees">Employees</a>
  <a href="/reports">Reports</a>
  <a href="/admin/">Admin</a>
</nav>
<div class="container">
  <br>
  <div class="card">
    <h2><span class="dot"></span>System status &mdash; $HOSTNAME</h2>
    <table>
      <thead><tr><th>Metric</th><th>Value</th></tr></thead>
      <tbody>
        <tr><td>Hostname</td><td>$HOSTNAME</td></tr>
        <tr><td>Date</td><td>$DATE</td></tr>
        <tr><td>Uptime</td><td>$UPTIME</td></tr>
        <tr><td>Load average (1/5/15 min)</td><td>$LOAD</td></tr>
        <tr><td>Memory used / total</td><td>$MEM</td></tr>
        <tr><td>Kernel</td><td>$KERNEL</td></tr>
        <tr><td>Web server</td><td>$APACHE_VER</td></tr>
      </tbody>
    </table>
  </div>
</div>
<footer>CorpNet v2.1 &middot; Internal use only</footer>
</body>
</html>
HTML

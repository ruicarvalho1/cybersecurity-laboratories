#!/bin/bash
# Employee lookup endpoint.
echo "Content-Type: text/html"
echo ""

NAME=$(printf '%s' "$QUERY_STRING" \
      | sed 's/.*name=//;s/&.*//' \
      | python3 -c "import sys,urllib.parse; print(urllib.parse.unquote_plus(sys.stdin.read()),end='')" \
      2>/dev/null)
NAME=${NAME:-"guest"}

cat <<HTML
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CorpNet &mdash; Employee lookup</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 600px; margin: 48px auto; padding: 0 16px; color: #333; }
    a { color: #0052cc; }
  </style>
</head>
<body>
  <h2>Hello, $NAME!</h2>
  <p>No matching employee found in the directory.</p>
  <p><a href="/">&larr; Back to portal</a></p>
</body>
</html>
HTML

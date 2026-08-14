#!/bin/bash
# Login handler.
echo "Content-Type: text/html"
echo ""

BODY=""
if [ "${REQUEST_METHOD}" = "POST" ] && [ -n "${CONTENT_LENGTH}" ]; then
  BODY=$(dd bs=1 count="${CONTENT_LENGTH}" 2>/dev/null)
else
  BODY="$QUERY_STRING"
fi

USERNAME=$(printf '%s' "$BODY" | python3 -c "
import sys, urllib.parse
d = dict(urllib.parse.parse_qsl(sys.stdin.read()))
print(d.get('username', ''))
" 2>/dev/null)

if printf '%s' "$USERNAME" | python3 -c "
import sys, re; u = sys.stdin.read()
sys.exit(0 if re.search(r\"'\\s*or|--\", u, re.I) else 1)
" 2>/dev/null; then
  MSG='<h2 style="color:#2e7d32">&#x2714; Welcome, admin!</h2>
<p>Your input caused the WHERE clause to always evaluate true:</p>
<pre style="background:#f4f5f7;padding:10px;border-radius:3px;font-size:.85em">SELECT id, role FROM users
WHERE username=&#39;<strong>\'' OR 1=1 --</strong>&#39; AND password=MD5(&#39;...&#39;)</pre>
<p>In a real database this returns the first row — typically the admin account.</p>'
else
  MSG='<h2 style="color:#b71c1c">&#x2718; Login failed</h2><p>Incorrect username or password.</p>'
fi

cat <<HTML
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CorpNet — Sign in</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 540px; margin: 48px auto; padding: 0 16px; color: #333; }
    pre  { overflow-x: auto; }
  </style>
</head>
<body>
  $MSG
  <p><a href="/" style="color:#0052cc">&larr; Back to portal</a></p>
</body>
</html>
HTML

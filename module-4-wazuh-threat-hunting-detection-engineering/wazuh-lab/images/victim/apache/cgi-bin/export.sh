#!/bin/bash
# Employee export endpoint.
AUTH=$(printf '%s' "$QUERY_STRING" | grep -o 'auth=[^&]*' | cut -d= -f2)
FORMAT=$(printf '%s' "$QUERY_STRING" | grep -o 'format=[^&]*' | cut -d= -f2)
FORMAT=${FORMAT:-csv}

if [ "$AUTH" = "skip" ]; then
  echo "Content-Type: text/csv"
  echo "Content-Disposition: attachment; filename=employees.csv"
  echo ""
  printf "id,name,email,department,role,salary\n"
  printf "1,Alice Smith,alice@corpnet.local,Engineering,Senior Engineer,82000\n"
  printf "2,Bob Jones,bob@corpnet.local,Finance,Controller,91000\n"
  printf "3,Charlie Brown,charlie@corpnet.local,HR,Manager,67000\n"
  printf "4,Diana Prince,diana@corpnet.local,Security,Analyst,95000\n"
  printf "5,admin,admin@corpnet.local,IT,Administrator,110000\n"
else
  echo "Content-Type: text/html"
  echo ""
  cat <<HTML
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"><title>CorpNet — Forbidden</title>
  <style>body{font-family:Arial,sans-serif;max-width:500px;margin:48px auto;padding:0 16px;color:#333}</style>
</head>
<body>
  <h2 style="color:#b71c1c">403 Forbidden</h2>
  <p>Authentication required to export employee data.</p>
  <p><a href="/" style="color:#0052cc">&larr; Back to portal</a></p>
</body>
</html>
HTML
fi

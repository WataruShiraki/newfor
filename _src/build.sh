#!/bin/bash
set -e
cd /home/claude
python3 publish.py
python3 mkpages.py
python3 buildarticles.py
python3 assets.py
node png.js
node og.js
python3 extras.py
python3 fixlinks.py
python3 analytics.py
# 注意：gh/index.html と gh/companies/index.html は手で管理しているため、ここでは生成しません
echo "=== build done ==="
find dist -type f | wc -l


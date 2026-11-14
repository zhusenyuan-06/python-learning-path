#!/usr/bin/env bash
# 立即推送 —— 探活已命中活 IP，按 T20「探活与操作之间不插任何 sleep」立刻绑上推
# 用法：bash 工具/_push_now.sh
set -u
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
export NO_PROXY="*"
export GIT_TERMINAL_PROMPT=0

GIT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$GIT_DIR" || exit 1
PY="D:/AAAA/python.exe"

# 已由探活确认活着的 web 段 IP（T23：必须逐个试，不能只试第一个）
LIVE_WEB="140.82.112.3 140.82.112.4 140.82.113.3 140.82.113.4 140.82.116.4 140.82.121.4"

echo "=== 提交本地改动 ==="
git add -A
if git diff --cached --quiet; then
  echo "  [i] 无改动"
else
  git status --short
  git commit -q -m "${1:-chore: 更新学习记录}"
  echo "  [ok] 已提交"
fi

echo
echo "=== api 段单独探活（T17：web/api 不同网段）==="
LIVE_API=$("$PY" "$GIT_DIR/工具/probe_gh.py" api 2>/dev/null | sed -n 's/^LIVE_IPS=//p')
API_IP=$(echo "$LIVE_API" | awk '{print $1}')
if [ -n "$API_IP" ]; then
  git config --global --unset-all "http.https://api.github.com/.curloptResolve" 2>/dev/null
  git config --global --add "http.https://api.github.com/.curloptResolve" "api.github.com:443:${API_IP}"
  echo "  api 段绑到 $API_IP"
else
  echo "  [!] api 段没探到活 IP（可能不影响 push，push 主要走 github.com）"
fi

echo
PUSHED=0
for ip in $LIVE_WEB; do
  git config --global --unset-all "http.https://github.com/.curloptResolve" 2>/dev/null
  git config --global --add "http.https://github.com/.curloptResolve" "github.com:443:${ip}"
  echo "--- 尝试 github.com -> $ip ---"
  if timeout 45 git push origin main > /tmp/_gh_push.log 2>&1; then
    tail -4 /tmp/_gh_push.log
    PUSHED=1
    break
  fi
  echo "    [!] $(tail -1 /tmp/_gh_push.log)"
done

echo
if [ "$PUSHED" != "1" ]; then
  echo "[!] 全部 IP 都失败了 —— 按 T18 先校验远端（可能其实推上去了）"
  LOCAL=$(git rev-parse HEAD)
  REMOTE=$(git ls-remote origin refs/heads/main 2>/dev/null | cut -f1)
  echo "    本地: $LOCAL"
  echo "    远端: ${REMOTE:-连不上}"
  [ "$LOCAL" = "$REMOTE" ] && PUSHED=1
fi

echo
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git ls-remote origin refs/heads/main 2>/dev/null | cut -f1)
echo "本地: $LOCAL"
echo "远端: ${REMOTE:-连不上}"
if [ "$LOCAL" = "$REMOTE" ]; then
  echo "============================================================"
  echo "  [OK] 推送完成并已校验"
  echo "  https://github.com/zhusenyuan-06/python-learning-path"
  echo "============================================================"
  exit 0
else
  echo "  [!] 不一致 —— 窗口可能又关了，等 5~10 分钟重跑（IP 池会轮换，T20）"
  exit 1
fi

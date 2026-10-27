#!/usr/bin/env bash
# ============================================================
# GitCode 推送助手 · 2026-10-27
# ------------------------------------------------------------
# 背景：校园网到 GitHub 的 TCP 443 随机丢包（实测 0-40% 成功率），
#       但到 gitcode.com / gitee.com 是 100% 稳定（国内线路）。
#       所以作品集主仓库改放 GitCode（CSDN 旗下，有"求职名册"）。
#
# 用法：
#   ./push_gitcode.sh --test     # 只测连通性，不推送
#   ./push_gitcode.sh            # 正常推送
#   ./push_gitcode.sh "提交信息"  # 带提交信息
# ============================================================

# ---- 清掉 WorkBuddy 注入的代理（国内站点直连更快）----
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

# ---- 账号信息（第一次用要改成你自己的）----
GITCODE_USER="your_gitcode_username"
REPO_NAME="python-learning-path"
REMOTE_URL="https://gitcode.com/${GITCODE_USER}/${REPO_NAME}.git"

cd /d/pythonProject || { echo "[X] 找不到项目目录"; exit 1; }

echo "=== 1. 测试 GitCode 连通性 ==="
if git ls-remote https://gitcode.com/gh_mirrors/py/python.git >/dev/null 2>&1; then
  echo "[OK] GitCode 可访问"
else
  echo "[X] GitCode 连不上，检查网络"
  exit 1
fi

if [ "$1" = "--test" ]; then
  echo ""
  echo "[OK] 连通性测试通过，退出。"
  exit 0
fi

# ---- 检查 remote ----
if git remote | grep -q "^origin$"; then
  CURRENT=$(git remote get-url origin)
  if [ "$CURRENT" != "$REMOTE_URL" ]; then
    echo ""
    echo "[!] 当前 origin 指向 GitHub: $CURRENT"
    echo "    改为 GitCode: $REMOTE_URL"
    git remote set-url origin "$REMOTE_URL"
    echo "[OK] 已切换"
  fi
else
  git remote add origin "$REMOTE_URL"
  echo "[OK] 已添加 remote: $REMOTE_URL"
fi

# ---- 暂存提交 ----
echo ""
echo "=== 2. 暂存改动 ==="
git add -A
git status --short
echo ""

if git diff --cached --quiet; then
  echo "[i] 没有需要提交的改动"
else
  echo "=== 3. 提交 ==="
  git commit -m "${1:-chore: 更新学习记录}"
fi

echo ""
echo "=== 4. 推送 ==="
git push -u origin main
echo ""
echo "[OK] 完成！去 https://gitcode.com/${GITCODE_USER}/${REPO_NAME} 看看"

# 🔒 AlphaSignal 安全指南

## ⚠️ 紧急：如果你已经提交了 `.env` 文件

### 问题严重性

如果 `.env` 文件已经被提交到 Git 历史，**你的 API Key 已经泄露**！即使你现在删除它，历史记录中仍然存在。

### 立即行动清单

#### 1. 撤销所有 API Key（最重要！）

```bash
# Google Gemini
# 访问 https://makersuite.google.com/app/apikey
# 删除旧的 API Key，生成新的

# DeepSeek
# 访问 https://platform.deepseek.com/api_keys
# 删除旧的 API Key，生成新的

# 邮箱密码
# 如果使用 Gmail App Password，删除旧的，生成新的
```

#### 2. 从 Git 历史中完全移除敏感文件

**选项 A: 使用 BFG Repo-Cleaner（推荐）**

```bash
# 安装 BFG
brew install bfg  # macOS
# 或下载: https://rtyley.github.io/bfg-repo-cleaner/

# 备份仓库
cp -r .git .git.backup

# 删除 .env 文件的所有历史记录
bfg --delete-files .env

# 清理
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 强制推送（如果已推送到远程）
git push origin --force --all
```

**选项 B: 使用 git filter-branch**

```bash
# 警告：这会重写整个 Git 历史！
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all

# 清理
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 强制推送
git push origin --force --all
```

#### 3. 如果仓库是公开的

- ⚠️ **立即将仓库设为私有**（GitHub Settings -> Danger Zone）
- ⚠️ **考虑删除仓库并重新创建**（如果已被爬虫抓取）
- ⚠️ **检查是否有未授权的 API 使用**

---

## ✅ 当前安全措施（已实施）

### 1. `.gitignore` 配置

已创建完整的 `.gitignore` 文件，防止提交：
- ✅ `.env` 和所有环境变量文件
- ✅ 数据库文件（`*.db`）
- ✅ 日志文件
- ✅ 临时文件和缓存

### 2. `.env.example` 模板

已创建 `.env.example` 作为配置模板：
- ✅ 包含所有必需的环境变量
- ✅ 提供获取 API Key 的链接
- ✅ 包含详细的注释

### 3. 自动安全检查

已创建 `scripts/security-check.sh`，检查：
- ✅ `.env` 文件是否被 Git 跟踪
- ✅ 数据库文件是否被 Git 跟踪
- ✅ 代码中是否有硬编码的 API Key
- ✅ `.gitignore` 规则是否正确

### 4. Git Pre-commit Hook

已安装 pre-commit hook，每次提交前自动运行安全检查：
- ✅ 自动阻止提交敏感文件
- ✅ 可以手动绕过（`git commit --no-verify`），但不推荐

---

## 📋 安全最佳实践

### 开发环境

#### 1. 环境变量管理

```bash
# ✅ 正确：从环境变量读取
api_key = os.getenv('GEMINI_API_KEY')

# ❌ 错误：硬编码
api_key = 'AIzaSyABC123...'
```

#### 2. 配置文件

```python
# ✅ 正确：使用配置类
from src.alphasignal.config import settings
api_key = settings.GEMINI_API_KEY

# ❌ 错误：直接读取文件
with open('.env') as f:
    api_key = f.read()
```

#### 3. 日志记录

```python
# ✅ 正确：隐藏敏感信息
logger.info(f"Using API key: {api_key[:8]}...")

# ❌ 错误：记录完整 API Key
logger.info(f"API key: {api_key}")
```

---

### 生产环境

#### 1. 使用专用的密钥管理服务

**Vercel**:
```bash
# 在 Vercel Dashboard 设置环境变量
# Settings -> Environment Variables
vercel env add GEMINI_API_KEY
```

**GitHub Actions**:
```bash
# 在 GitHub 仓库设置 Secrets
# Settings -> Secrets and variables -> Actions
# 添加: GEMINI_API_KEY, DEEPSEEK_API_KEY
```

**Docker**:
```bash
# 使用 Docker secrets
docker secret create gemini_api_key ./gemini_key.txt
docker service create --secret gemini_api_key myapp
```

#### 2. 环境分离

```bash
# 开发环境
.env.development

# 测试环境
.env.test

# 生产环境（使用云服务的密钥管理）
# 不使用 .env 文件
```

#### 3. API Key 轮换

```bash
# 定期更换 API Key（建议每 3 个月）
# 1. 生成新的 API Key
# 2. 更新环境变量
# 3. 删除旧的 API Key
```

---

## 🛡️ 安全检查清单

### 每次提交前

- [ ] 运行 `./scripts/security-check.sh`
- [ ] 确认没有 `.env` 文件在 `git status` 中
- [ ] 确认没有硬编码的 API Key

### 每周

- [ ] 检查 GitHub 仓库是否为私有
- [ ] 检查是否有未授权的 API 使用
- [ ] 审查最近的提交历史

### 每月

- [ ] 轮换 API Key
- [ ] 审查访问日志
- [ ] 更新依赖包（安全补丁）

---

## 🚨 应急响应

### 如果发现 API Key 泄露

1. **立即撤销泄露的 API Key**
2. **生成新的 API Key**
3. **更新所有环境的配置**
4. **检查是否有未授权使用**
5. **从 Git 历史中移除（见上文）**
6. **通知团队成员**

### 如果发现数据库泄露

1. **立即将仓库设为私有**
2. **从 Git 历史中移除数据库文件**
3. **评估数据泄露影响**
4. **通知受影响的用户**（如果有）

---

## 📚 相关资源

- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [12-Factor App: Config](https://12factor.net/config)

---

## 🔍 定期审计

运行以下命令检查潜在的安全问题：

```bash
# 检查 Git 历史中的敏感信息
git log --all --full-history --source --pretty=format:"%H" -- .env

# 搜索可能的 API Key
git grep -E "(api_key|API_KEY|password|PASSWORD).*=.*['\"][A-Za-z0-9]{20,}"

# 检查大文件（可能是误提交的数据库）
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '/^blob/ {print substr($0,6)}' | \
  sort -n -k 2 | \
  tail -20
```

---

## ✅ 总结

**已实施的安全措施**：
- ✅ `.gitignore` 防止提交敏感文件
- ✅ `.env.example` 作为配置模板
- ✅ 自动安全检查脚本
- ✅ Git pre-commit hook
- ✅ 从 Git 中移除 `.env` 和 `*.db`

**下一步**：
1. 如果 `.env` 曾被推送到远程，立即撤销所有 API Key
2. 使用 BFG 清理 Git 历史
3. 定期运行安全审计

**记住**：安全是一个持续的过程，不是一次性的任务！

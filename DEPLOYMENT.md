# 🚀 部署指南 - 心桥 EduAI 后端

## 推荐部署方案：Render

> Render 是最简单的方案，自动部署，免费试用

### 步骤 1️⃣：准备代码

```bash
git add .
git commit -m "Flask backend ready for deployment"
git push origin backend-flask-setup
```

### 步骤 2️⃣：创建 Render 账户

1. 访问 [render.com](https://render.com)
2. 用 GitHub 账号登录
3. 授权 Render 访问你的仓库

### 步骤 3️⃣：创建 Web Service

1. 点击 "New+" → "Web Service"
2. 选择 `xin-qiao-eduai` 仓库
3. 选择 `backend-flask-setup` 分支
4. 配置：
   - **Name**: `xin-qiao-eduai-backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### 步骤 4️⃣：设置环境变量

在 Render 中添加这些变量：

```
CLAUDE_API_KEY=sk-ant-your-actual-key
DATABASE_URL=postgresql://[user]:[password]@[host]:[port]/[database]
JWT_SECRET=your-secret-key-min-32-chars
FLASK_ENV=production
FLASK_DEBUG=False
CORS_ORIGINS=https://your-frontend-domain.com,https://another-domain.com
```

### 步骤 5️⃣：部署

Render 会自动检测 `Procfile` 并部署

完成后获得 URL：
```
https://xin-qiao-eduai-backend.onrender.com
```

### 步骤 6️⃣：测试

```bash
# 测试健康检查
curl https://xin-qiao-eduai-backend.onrender.com/api/health

# 测试登录
curl -X POST https://xin-qiao-eduai-backend.onrender.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student001","password":"password123"}'
```

## 🔗 配置 Supabase 数据库

### 步骤 1️⃣：创建 Supabase 项目

1. 访问 [supabase.com](https://supabase.com)
2. 创建新项目
3. 等待项目初始化

### 步骤 2️⃣：获取连接字符串

1. 进入项目 → Settings → Database
2. 复制 "Connection string" (URI 格式)
3. 格式：`postgresql://[user]:[password]@[host]:[port]/[database]`

### 步骤 3️⃣：更新环境变量

在 Render 或本地 `.env` 中更新：

```
DATABASE_URL=postgresql://...
```

### 步骤 4️⃣：测试连接

```bash
# 本地测试
FLASK_ENV=production python app.py

# 访问
http://localhost:5000/api/health
```

## 📊 监控和日志

### Render 日志

1. 进入 Render 项目
2. 点击 "Logs" 标签
3. 查看实时日志

### 常见错误

#### ❌ ModuleNotFoundError

**原因**：缺少依赖

**解决**：确保所有依赖都在 `requirements.txt` 中

#### ❌ 无法连接数据库

**原因**：`DATABASE_URL` 错误

**解决**：
1. 检查连接字符串
2. 确保 Supabase 项目在线
3. 检查网络连接

#### ❌ Claude API 错误

**原因**：API Key 无效或过期

**解决**：去 [anthropic.com](https://anthropic.com) 重新获取

## 🔄 持续部署

Render 会自动监听 GitHub 推送：

```bash
# 修改代码后
git add .
git commit -m "Fix: update API"
git push origin backend-flask-setup

# Render 会自动重新部署
```

## 📱 前端配置

在前端项目的 `.env` 中更新：

```
VITE_API_BASE_URL=https://xin-qiao-eduai-backend.onrender.com
```

## ✅ 部署检查清单

- [ ] 代码推送到 GitHub
- [ ] Render 账户已创建
- [ ] Web Service 已创建
- [ ] 所有环境变量已设置
- [ ] Supabase 数据库已连接
- [ ] Claude API Key 已添加
- [ ] 部署完成（绿色状态）
- [ ] 测试 `/api/health` 成功
- [ ] 测试登录接口成功
- [ ] 前端 API_BASE_URL 已更新

## 🎯 部署完成后

1. ✅ 后端已在线
2. ⏳ 连接前端到后端
3. ⏳ 测试完整工作流
4. ⏳ 录制演示视频
5. ⏳ 提交项目

# 心桥 EduAI 后端 - Python Flask

> 基于 Python + Flask + PostgreSQL 的 AI 驱动学生成长支持平台后端

## 🚀 快速开始

### 1️⃣ 环境准备

```bash
# 克隆项目
git clone https://github.com/Z77839/xin-qiao-eduai.git
cd xin-qiao-eduai

# 切换到后端分支
git checkout backend-flask-setup

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2️⃣ 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env，填入真实信息
```

**必填项：**
```env
CLAUDE_API_KEY=sk-ant-your-actual-key
DATABASE_URL=postgresql://user:password@host:5432/xin_qiao_db
JWT_SECRET=your-secret-key-min-32-chars
```

### 3️⃣ 创建数据库

**使用 Supabase（推荐）：**

1. 访问 [supabase.com](https://supabase.com)
2. 创建新项目
3. 获取 PostgreSQL 连接字符串
4. 复制到 `.env` 中的 `DATABASE_URL`

### 4️⃣ 启动服务器

```bash
python app.py
```

服务器将在 `http://localhost:5000` 启动

## 📡 API 文档

### 认证

所有接口（除了登录/注册）都需要 JWT Token：

```
Authorization: Bearer <your-jwt-token>
Content-Type: application/json
```

### API 端点

#### 1️⃣ 注册

```bash
POST /api/register

{
  "username": "student001",
  "password": "password123",
  "name": "李同学",
  "role": "student"
}
```

**响应：**
```json
{
  "success": true,
  "user_id": "user_1234567890",
  "name": "李同学",
  "role": "student",
  "token": "eyJhbGc..."
}
```

#### 2️⃣ 登录

```bash
POST /api/login

{
  "username": "student001",
  "password": "password123"
}
```

#### 3️⃣ 获取用户信息

```bash
GET /api/user/info
Authorization: Bearer <token>
```

#### 4️⃣ 获取学生列表

```bash
GET /api/students?page=1&per_page=20&risk=high
Authorization: Bearer <token>
```

#### 5️⃣ 获取学生详情

```bash
GET /api/students/<student_id>
Authorization: Bearer <token>
```

#### 6️⃣ 获取预警列表

```bash
GET /api/alerts?severity=high
Authorization: Bearer <token>
```

#### 7️⃣ 热力图数据

```bash
GET /api/heatmap
Authorization: Bearer <token>
```

#### 8️⃣ AI 对话 ⭐ **最关键**

```bash
POST /api/chat
Authorization: Bearer <token>

{
  "message": "请分析我的学习数据",
  "student_id": "stu_001"  # 可选
}
```

**响应：**
```json
{
  "success": true,
  "reply": "你好李同学！根据数据分析..."
}
```

#### 9️⃣ 统计数据

```bash
GET /api/stats
Authorization: Bearer <token>
```

## 🔌 前端集成

### 环境变量

在前端 `.env` 中添加：

```
VITE_API_BASE_URL=http://localhost:5000
```

### 示例代码

```javascript
const API_BASE = import.meta.env.VITE_API_BASE_URL;

// 登录
async function login(username, password) {
  const res = await fetch(`${API_BASE}/api/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const { token } = await res.json();
  localStorage.setItem('token', token);
  return token;
}

// AI 对话
async function chatWithAI(message) {
  const token = localStorage.getItem('token');
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ message })
  });
  return await res.json();
}
```

## 🐛 常见问题

### Q: ModuleNotFoundError

A: 安装依赖
```bash
pip install -r requirements.txt
```

### Q: 数据库连接失败

A: 检查 `DATABASE_URL` 是否正确

### Q: Claude API Key 无效

A: 去 [anthropic.com](https://anthropic.com) 获取新密钥

## 📚 开发指南

### 添加新接口

```python
@app.route('/api/new-endpoint', methods=['POST'])
@token_required
def new_endpoint():
    data = request.get_json()
    # 业务逻辑
    return jsonify({'success': True}), 200
```

### 修改数据库模型

编辑 `app.py` 中的模型定义，重启服务器自动创建表

## ✅ 下一步

- [ ] 配置 Supabase 数据库
- [ ] 获取 Claude API Key
- [ ] 本地测试所有接口
- [ ] 部署到 Render
- [ ] 连接前端

# 心桥EduAI · 大学生成长支持平台

> 基于多模态学习行为分析的大学生成长支持平台

---

## 📁 项目结构

```
心桥EduAI项目完整包/
├── 心桥3.html              # 前端页面（直接在浏览器打开即可使用）
├── server.js               # 后端服务（Node.js）
├── package.json            # 后端依赖
├── .env.example            # 环境变量示例（部署时参考）
├── 产品原型全景图.png        # 产品原型截图
├── 心桥EduAI_15页省赛答辩PPT.pptx   # 答辩 PPT
├── 心桥EduAI...商业计划书 (2).docx  # 商业计划书 Word 版
├── 心桥EduAI...商业计划书 (2).pdf   # 商业计划书 PDF 版
└── 附录H-3_核心算法说明.docx        # 算法说明文档
```

---

## 🚀 快速启动

### 本地前端（无需后端，纯前端演示）
直接用浏览器打开 `心桥3.html` 即可体验。

### 接入 AI 对话功能

**1. 安装后端依赖**
```bash
cd 心桥EduAI项目完整包
npm install
```

**2. 配置环境变量**
将 `.env.example` 复制为 `.env`，填入你的 OpenAI API Key：
```bash
OPENAI_API_KEY=sk-your-key-here
```

**3. 启动后端**
```bash
npm start
```
后端运行在 `http://localhost:5000`

**4. 修改前端 API 地址**
打开 `心桥3.html`，找到：
```js
const API_BASE = 'http://localhost:5000';
```
确保值匹配后端地址即可。

---

## 🌐 部署到 Render（免费）

### 1. 上传到 GitHub
将 `server.js`、`package.json` 上传到 GitHub 仓库。

### 2. Render 部署
- [render.com](https://render.com) → New → Web Service
- 关联 GitHub 仓库
- 配置：
  - **Build Command**: `npm install`
  - **Start Command**: `npm start`
  - **Plan**: Free

### 3. 设置环境变量
Render 控制台 → Environment：
| 变量名 | 值 |
|---|---|
| `OPENAI_API_KEY` | 填入你的 OpenAI API Key |

### 4. 部署完成后
把 Render 给你的 URL（如 `https://xinqiao-backend.onrender.com`）填入前端 `API_BASE`，重新上传即可。

---

## ✅ 功能清单

- 🎓 **学生端**：成长中心、学习分析、成长档案、AI 导师对话
- 👩‍💼 **辅导员端**：管理看板、预警管理、学生名单、AI 辅导助手
- 🏫 **管理员端**：数据驾驶舱、风险分析、学院热力图
- 🤖 **AI 对话**：接入 OpenAI GPT-3.5-turbo
- 📊 **10 个 Chart.js 可视化图表**
- 📱 **移动端响应式原型**

---

## 📝 技术栈

- **前端**：HTML5 + CSS3 + JavaScript + Chart.js
- **后端**：Node.js + Express
- **AI**：OpenAI API (GPT-3.5-turbo)
- **部署**：Render（后端）/ 任意静态托管（前端）

const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5000;

const API_KEY = process.env.OPENAI_API_KEY;
const API_URL = 'https://api.openai.com/v1/chat/completions';

if (!API_KEY) {
  console.warn('⚠️ 未检测到 OPENAI_API_KEY，AI 对话功能暂时不可用');
}

app.use(cors());
app.use(express.json());

// 健康检查
app.get('/', (req, res) => {
  res.json({ status: 'ok', message: '心桥EduAI 后端服务运行中' });
});

// POST /api/chat — 核心对话接口
app.post('/api/chat', async (req, res) => {
  const { message, student_id } = req.body;

  if (!message) {
    return res.status(400).json({ reply: '消息内容不能为空' });
  }

  // 构建 system prompt（心桥EduAI 成长导师角色）
  const systemPrompt = `你是心桥EduAI平台的AI成长导师，专门为大学生提供学习、心理和成长方面的支持。
请用温暖、专业、简洁的语言回复，适当使用 emoji，回答控制在200字以内，提供实际可操作的建议。`;

  try {
    const openaiRes = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`,
      },
      body: JSON.stringify({
        model: 'gpt-3.5-turbo',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: message },
        ],
        max_tokens: 500,
        temperature: 0.8,
      }),
    });

    if (!openaiRes.ok) {
      const err = await openaiRes.text();
      console.error('OpenAI API 错误:', err);
      return res.status(openaiRes.status).json({ reply: `AI 服务出错 (${openaiRes.status})，请稍后重试` });
    }

    const data = await openaiRes.json();
    const reply = data.choices?.[0]?.message?.content || '抱歉，暂未获取到回复，请稍后重试。';

    return res.json({ reply });
  } catch (e) {
    console.error('后端异常:', e);
    return res.status(500).json({ reply: `服务器错误：${e.message}。请确保网络正常后重试。` });
  }
});

app.listen(PORT, () => {
  console.log(`\n✅ 心桥EduAI 后端服务已启动`);
  console.log(`📍 http://localhost:${PORT}`);
  console.log(`🔑 API: OpenAI GPT-3.5-turbo\n`);
});
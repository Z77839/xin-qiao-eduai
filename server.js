const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 5000;

const API_KEY = process.env.AGNES_API_KEY;
const API_URL = 'https://apihub.agnes-ai.com/v1/chat/completions';

if (!API_KEY) {
  console.warn('⚠️ 未检测到 AGNES_API_KEY，AI 对话功能暂时不可用');
}

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
  res.json({ status: 'ok', message: '心桥EduAI 后端服务运行中' });
});

app.post('/api/chat', async (req, res) => {
  const { message, student_id } = req.body;

  if (!message) {
    return res.status(400).json({ reply: '消息内容不能为空' });
  }

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
        model: 'agnes-2.0-flash',
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
      console.error('Agnes API 错误:', err);
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
  console.log(`🔑 API: Agnes AI agnes-2.0-flash（免费多模态模型）\n`);
});

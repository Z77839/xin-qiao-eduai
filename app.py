"""
心桥 EduAI 后端主应用
Python + Flask + Supabase PostgreSQL
集成 Claude AI 对话功能
"""

import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import json

# 加载环境变量
load_dotenv()

# ===== Flask 初始化 =====
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False

# 跨域配置
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, resources={
    r"/api/*": {
        "origins": CORS_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# JWT 配置
JWT_SECRET = os.getenv('JWT_SECRET', 'dev-secret-key-change-in-production')
JWT_EXPIRY_HOURS = 24

# ===== 数据库配置 =====
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///xin_qiao.db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ===== 数据库模型 =====
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default='student')  # student, counselor, admin
    created_at = Column(DateTime, default=datetime.utcnow)

class Student(Base):
    __tablename__ = "students"
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    student_id = Column(String, unique=True)
    class_id = Column(String)
    gpa = Column(Float, default=0)
    risk_level = Column(String, default='ok')  # ok, low, mid, high
    last_updated = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(String, primary_key=True)
    student_id = Column(String, nullable=False)
    alert_type = Column(String)  # academic, psychological, behavioral
    severity = Column(String)  # low, mid, high
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(String, default='pending')

class ChatHistory(Base):
    __tablename__ = "chat_histories"
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    student_id = Column(String)
    role = Column(String)  # user, assistant
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# 创建表
Base.metadata.create_all(engine)

# ===== JWT 工具函数 =====
def create_token(user_id, role):
    """生成 JWT Token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    """验证 JWT Token"""
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return data
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """JWT 认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': '无效的认证头'}), 401
        
        if not token:
            return jsonify({'error': '缺少认证 Token'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token 过期或无效'}), 401
        
        request.user_id = payload['user_id']
        request.user_role = payload['role']
        return f(*args, **kwargs)
    
    return decorated

# ===== API 路由 =====

# ===== 1. 注册接口 =====
@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    role = data.get('role', 'student')
    
    if not all([username, password, name]):
        return jsonify({'error': '缺少必填字段'}), 400
    
    session = SessionLocal()
    try:
        existing = session.query(User).filter_by(username=username).first()
        if existing:
            return jsonify({'error': '用户已存在'}), 409
        
        new_user = User(
            id=f"user_{int(datetime.utcnow().timestamp())}",
            username=username,
            password=password,
            name=name,
            role=role
        )
        session.add(new_user)
        session.commit()
        
        token = create_token(new_user.id, new_user.role)
        return jsonify({
            'success': True,
            'user_id': new_user.id,
            'name': new_user.name,
            'role': new_user.role,
            'token': token
        }), 201
    finally:
        session.close()

# ===== 2. 登录接口 =====
@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': '缺少用户名或密码'}), 400
    
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=username).first()
        
        if not user or user.password != password:
            return jsonify({'error': '用户名或密码错误'}), 401
        
        token = create_token(user.id, user.role)
        return jsonify({
            'success': True,
            'user_id': user.id,
            'name': user.name,
            'role': user.role,
            'token': token
        }), 200
    finally:
        session.close()

# ===== 3. 获取当前用户信息 =====
@app.route('/api/user/info', methods=['GET'])
@token_required
def get_user_info():
    """获取当前用户信息"""
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(id=request.user_id).first()
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        return jsonify({
            'user_id': user.id,
            'name': user.name,
            'username': user.username,
            'role': user.role,
            'created_at': user.created_at.isoformat()
        }), 200
    finally:
        session.close()

# ===== 4. 获取学生列表 =====
@app.route('/api/students', methods=['GET'])
@token_required
def get_students():
    """获取学生列表（辅导员/管理员）"""
    if request.user_role not in ['counselor', 'admin']:
        return jsonify({'error': '权限不足'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    risk_filter = request.args.get('risk')
    
    session = SessionLocal()
    try:
        query = session.query(Student)
        
        if risk_filter:
            query = query.filter_by(risk_level=risk_filter)
        
        total = query.count()
        students = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return jsonify({
            'total': total,
            'page': page,
            'per_page': per_page,
            'students': [{
                'id': s.id,
                'name': s.name,
                'student_id': s.student_id,
                'gpa': s.gpa,
                'risk_level': s.risk_level,
                'last_updated': s.last_updated.isoformat()
            } for s in students]
        }), 200
    finally:
        session.close()

# ===== 5. 获取学生详情 =====
@app.route('/api/students/<student_id>', methods=['GET'])
@token_required
def get_student_detail(student_id):
    """获取学生详情"""
    session = SessionLocal()
    try:
        student = session.query(Student).filter_by(id=student_id).first()
        if not student:
            return jsonify({'error': '学生不存在'}), 404
        
        alerts = session.query(Alert).filter_by(student_id=student_id).all()
        
        return jsonify({
            'id': student.id,
            'name': student.name,
            'student_id': student.student_id,
            'gpa': student.gpa,
            'risk_level': student.risk_level,
            'metadata': student.metadata or {},
            'alerts': [{
                'id': a.id,
                'type': a.alert_type,
                'severity': a.severity,
                'message': a.message,
                'created_at': a.created_at.isoformat()
            } for a in alerts]
        }), 200
    finally:
        session.close()

# ===== 6. 获取预警列表 =====
@app.route('/api/alerts', methods=['GET'])
@token_required
def get_alerts():
    """获取预警列表"""
    if request.user_role not in ['counselor', 'admin']:
        return jsonify({'error': '权限不足'}), 403
    
    severity = request.args.get('severity')
    
    session = SessionLocal()
    try:
        query = session.query(Alert).filter_by(resolved='pending')
        
        if severity:
            query = query.filter_by(severity=severity)
        
        alerts = query.order_by(Alert.created_at.desc()).all()
        
        return jsonify({
            'total': len(alerts),
            'alerts': [{
                'id': a.id,
                'student_id': a.student_id,
                'type': a.alert_type,
                'severity': a.severity,
                'message': a.message,
                'created_at': a.created_at.isoformat()
            } for a in alerts]
        }), 200
    finally:
        session.close()

# ===== 7. 热力图数据 =====
@app.route('/api/heatmap', methods=['GET'])
@token_required
def get_heatmap():
    """获取热力图数据"""
    if request.user_role != 'admin':
        return jsonify({'error': '仅管理员可访问'}), 403
    
    heatmap_data = {
        'dimensions': ['学习表现', '学习习惯', '活动参与', '心理状态', '发展潜力'],
        'colleges': [
            {'name': '信息学院', 'scores': [88, 82, 85, 75, 90]},
            {'name': '教育学院', 'scores': [78, 85, 88, 82, 76]},
            {'name': '商学院', 'scores': [85, 76, 86, 68, 84]}
        ]
    }
    
    return jsonify(heatmap_data), 200

# ===== 8. AI 对话接口 ⭐ =====
@app.route('/api/chat', methods=['POST'])
@token_required
def chat_with_ai():
    """与 AI 导师对话 - 使用 Claude API"""
    data = request.get_json()
    user_message = data.get('message')
    student_id = data.get('student_id')
    
    if not user_message:
        return jsonify({'error': '消息不能为空'}), 400
    
    try:
        from anthropic import Anthropic
        
        api_key = os.getenv('CLAUDE_API_KEY')
        if not api_key:
            return jsonify({'error': 'Claude API Key 未配置'}), 500
        
        client = Anthropic(api_key=api_key)
        
        system_prompt = f"""你是心桥 EduAI 平台的 AI 成长导师，专门为大学生提供学习、心理和成长方面的支持。

用户角色：{request.user_role}
当前时间：{datetime.utcnow().isoformat()}

如果用户是学生，帮助他们：
- 分析学习行为与成绩趋势
- 制定个性化学习计划
- 解答学习和生活中的困惑
- 提供心理支持与成长建议

如果用户是辅导员或管理员，帮助他们：
- 分析学生学习状态
- 制定干预策略
- 预测风险因素
- 提供班级管理建议

请用温暖、专业、简洁的语言回复，适当使用 emoji。
回答控制在 200-300 字以内，提供实际可操作的建议。"""
        
        session = SessionLocal()
        try:
            histories = session.query(ChatHistory).filter_by(
                user_id=request.user_id
            ).order_by(ChatHistory.created_at.desc()).limit(10).all()
        finally:
            session.close()
        
        messages = []
        for h in reversed(histories):
            messages.append({
                'role': h.role if h.role in ['user', 'assistant'] else 'user',
                'content': h.message
            })
        messages.append({
            'role': 'user',
            'content': user_message
        })
        
        response = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=1000,
            system=system_prompt,
            messages=messages
        )
        
        ai_reply = response.content[0].text
        
        session = SessionLocal()
        try:
            chat_user = ChatHistory(
                id=f"chat_{int(datetime.utcnow().timestamp())}_{request.user_id}",
                user_id=request.user_id,
                student_id=student_id,
                role='user',
                message=user_message
            )
            chat_ai = ChatHistory(
                id=f"chat_{int(datetime.utcnow().timestamp())}_{request.user_id}_ai",
                user_id=request.user_id,
                student_id=student_id,
                role='assistant',
                message=ai_reply
            )
            session.add(chat_user)
            session.add(chat_ai)
            session.commit()
        finally:
            session.close()
        
        return jsonify({
            'success': True,
            'reply': ai_reply
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': f'AI 服务暂时不可用：{str(e)}'
        }), 500

# ===== 9. 数据驾驶舱统计 =====
@app.route('/api/stats', methods=['GET'])
@token_required
def get_stats():
    """获取数据驾驶舱统计数据"""
    if request.user_role not in ['admin', 'counselor']:
        return jsonify({'error': '权限不足'}), 403
    
    session = SessionLocal()
    try:
        total_students = session.query(Student).count()
        at_risk = session.query(Student).filter(
            Student.risk_level.in_(['low', 'mid', 'high'])
        ).count()
        high_risk = session.query(Student).filter_by(risk_level='high').count()
        
        recent_alerts = session.query(Alert).filter_by(
            resolved='pending'
        ).order_by(Alert.created_at.desc()).limit(5).all()
        
        return jsonify({
            'total_students': total_students,
            'at_risk_count': at_risk,
            'high_risk_count': high_risk,
            'healthy_count': total_students - at_risk,
            'recent_alerts': [{
                'id': a.id,
                'student_id': a.student_id,
                'severity': a.severity,
                'message': a.message,
                'created_at': a.created_at.isoformat()
            } for a in recent_alerts]
        }), 200
    finally:
        session.close()

# ===== 健康检查 =====
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200

# ===== 错误处理 =====
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '未找到该资源'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误'}), 500

# ===== 启动 =====
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=port,
        debug=debug
    )

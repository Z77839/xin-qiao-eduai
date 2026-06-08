"""
Flask 配置管理
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """基础配置"""
    SECRET_KEY = os.getenv('JWT_SECRET', 'dev-secret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///xin_qiao_dev.db')

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    DATABASE_URL = os.getenv('DATABASE_URL')

class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)

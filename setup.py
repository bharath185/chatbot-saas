from setuptools import setup

setup(
    name='chatbot-saas',
    version='1.0.0',
    description='Customer Service Chatbot SaaS',
    packages=[],
    install_requires=[
        'Flask==2.3.3',
        'Flask-CORS==4.0.0',
        'Flask-SQLAlchemy==3.0.5',
        'Flask-JWT-Extended==4.4.4',
        'Werkzeug==2.3.7',
        'anthropic==0.9.0',
        'python-dotenv==1.0.0',
        'gunicorn==21.2.0',
        'razorpay==2.0.1',
        'httpx==0.24.1',
    ],
)

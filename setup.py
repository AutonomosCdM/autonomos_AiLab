"""
Configuración de instalación para Slack Bot.
"""
from setuptools import setup, find_packages

# Leer el README para la descripción larga
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Leer las dependencias del requirements.txt
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='slack_bot',
    version='0.1.0',
    author='Slack Bot Team',
    author_email='contacto@slack_bot.com',
    description='Bot de Slack impulsado por IA con Groq Llama3',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tu-usuario/slack-bot',
    packages=find_packages(exclude=['tests*', 'templates*']),
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ],
    keywords='slack bot ai groq llama3 chatbot',
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'slack-bot-generate=slack_bot.cli.generate:main',
            'slack-bot-deploy=slack_bot.cli.deploy:main'
        ]
    },
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
            'mypy',
            'black',
            'isort',
            'flake8'
        ],
        'docs': [
            'sphinx',
            'sphinx-rtd-theme'
        ]
    },
    project_urls={
        'Bug Reports': 'https://github.com/tu-usuario/slack-bot/issues',
        'Source': 'https://github.com/tu-usuario/slack-bot'
    }
)

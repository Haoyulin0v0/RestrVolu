"""
Setup脚本 - 用于pip安装
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ''

setup(
    name='volume-control',
    version='1.0.0',
    description='Windows系统音量控制工具 - 为每个应用独立控制音量',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/volume-control',
    license='MIT',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[
        'PyQt5==5.15.9',
        'pycaw==20230407',
        'psutil==5.9.6',
        'comtypes==1.2.0',
    ],
    extras_require={
        'dev': [
            'PyInstaller==6.1.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'volume-control=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: System :: Monitoring',
        'Topic :: Utilities',
    ],
    keywords=['volume', 'audio', 'windows', 'control', 'app'],
)

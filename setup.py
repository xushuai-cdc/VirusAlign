 """VirusAlign 安装脚本"""
 
 from setuptools import setup, find_packages
 
 setup(
     name="VirusAlign",
     version="1.0.0",
     description="基于 ICTV 病毒分类标准的物种名称对齐工具",
     long_description=open("README.md", encoding="utf-8").read(),
     long_description_content_type="text/markdown",
     author="VirusAlign Team",
     python_requires=">=3.9",
     packages=find_packages(include=["src", "src.*"]),
     include_package_data=True,
     install_requires=[
         "pandas>=1.4",
         "openpyxl>=3.0",
         "streamlit>=1.35",
     ],
     entry_points={
         "console_scripts": [
             "virusalign=src.cli_handler:main",
         ],
     },
     classifiers=[
         "Development Status :: 4 - Beta",
         "Intended Audience :: Science/Research",
         "Topic :: Scientific/Engineering :: Bio-Informatics",
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
     ],
 )

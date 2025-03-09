from setuptools import setup, find_packages

setup(
    name="aws-lambda-apigateway",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.26.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "aws-lambda-apigateway=aws_lambda_apigateway.cli.main:cli",
        ],
    },
    python_requires=">=3.8",
    author="Devin AI",
    author_email="devin-ai-integration[bot]@users.noreply.github.com",
    description="A Python package to create API Gateway endpoints that trigger AWS Lambda functions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jianhuanggo/aws_lambda_apigateway2",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

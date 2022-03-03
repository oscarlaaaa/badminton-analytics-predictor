#!/bin/bash  
cd package
7z -r ../deployment-package.zip
cd ..
7z -g deployment-package.zip lambda_function.py
aws lambda update-function-code --function-name badminton-anal-predict --zip-file fileb://deployment-package.zip

#!/bin/bash
# 把下面 TOKEN 换成你的 GitHub token，然后运行
cd /home/tcb/老科学家年表
TOKEN="你的token放这里"
git remote set-url origin "https://zksgithub:${TOKEN}@github.com/zksgithub/JAL.git"
git push -u origin main

#!/bin/bash

download_python_file() {
    local url="$1"
    local filename="$2"
    if command -v curl &> /dev/null; then
        curl -L "$url" -o "$filename"
    elif command -v wget &> /dev/null; then
        wget -O "$filename" "$url"
    else
        echo "错误：未找到 curl 或 wget。请安装其中之一以继续。"
        exit 1
    fi
    
    if [ $? -eq 0 ]; then
        echo "成功下载 $filename"
    else
        echo "下载 $filename 失败"
        exit 1
    fi
}

install_required_modules() {
    local filename="$1"
    echo "正在分析 $filename 所需的模块..."
    
    modules=$(grep -E "^import |^from " "$filename" | sed -E 's/^import //; s/^from ([^ ]+).*/\1/' | sort -u)
    
    for module in $modules; do
        if ! python3 -c "import $module" 2>/dev/null; then
            echo "正在安装模块: $module"
            pip3 install "$module"
        fi
    done
}

# 设置环境变量
export HOSTNAME="你的name.serv00.net"
export USERNAME="你的name"
export URL="http://你的name.serv00.net" #前提是你没有删除自己的默认网站，删除了就用自己搭建应用的网址
export SSH_PASSWORD="密码"
export BOT_TOKEN="2342342342342:dsfsddfsdfsfdfsfsdfsd" #上面获取的
export CHAT_ID="234234234"  #上面获取的


install_required_modules "Auto_connect_SSH-TG.py"

pip3 uninstall --user telegram
pip3 install --user python-telegram-bot


python3 Auto_connect_SSH-TG.py

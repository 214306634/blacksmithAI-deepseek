#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示欢迎信息
echo -e "${BLUE}================================${NC}"
echo -e "${BLACKSMITH}BlacksmithAI 启动脚本${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 显示选项
echo -e "${GREEN}请选择要使用的 LLM 提供商:${NC}"
echo -e "  ${YELLOW}1)${NC} DeepSeek (推荐，经济实惠)"
echo -e "  ${YELLOW}2)${NC} OpenRouter (多模型聚合，有免费模型)"
echo -e "  ${YELLOW}3)${NC} 使用配置文件默认值"
echo ""

# 获取用户输入
read -p "请输入选项 [1-3，默认: 1]: " choice

# 根据选择设置环境变量
case $choice in
    1)
        echo -e "${GREEN}✓ 已选择 DeepSeek${NC}"
        export BLACKSMITH_PROVIDER=deepseek
        ;;
    2)
        echo -e "${GREEN}✓ 已选择 OpenRouter${NC}"
        export BLACKSMITH_PROVIDER=openrouter
        ;;
    3)
        echo -e "${GREEN}✓ 使用配置文件默认值${NC}"
        unset BLACKSMITH_PROVIDER
        ;;
    *)
        echo -e "${YELLOW}无效输入，使用默认选项: DeepSeek${NC}"
        export BLACKSMITH_PROVIDER=deepseek
        ;;
esac

echo ""
echo -e "${BLUE}正在启动 BlacksmithAI...${NC}"
echo -e "${YELLOW}当前 Provider: ${BLACKSMITH_PROVIDER:-配置文件默认值}${NC}"
echo ""

# 启动应用
uv run main.py

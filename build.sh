#!/bin/bash

# PDF转图片工具 - 统一跨平台构建脚本 (使用PyInstaller)
# 支持 Windows (Git Bash/WSL), Linux, macOS

set -e  # 遇到错误立即退出

echo "=========================================="
echo "PDF转图片工具 - 跨平台构建脚本"
echo "=========================================="

# 检测操作系统
detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux";;
        Darwin*)    echo "macos";;
        CYGWIN*|MINGW*|MSYS*) echo "windows";;
        *)          echo "unknown";;
    esac
}

# 检查依赖
check_dependencies() {
    echo "正在检查依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        echo "错误: 未找到Python，请先安装Python 3.13+"
        case $OS in
            "linux") echo "Ubuntu/Debian: sudo apt install python3";;
            "macos") echo "macOS: brew install python@3.13";;
            "windows") echo "Windows: 从 python.org 下载安装";;
        esac
        exit 1
    fi
    
    # 检查uv
    if ! command -v uv &> /dev/null; then
        echo "错误: 未找到uv包管理器，请先安装uv"
        echo "安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    
    # 检查PyInstaller
    if ! uv run python -c "import PyInstaller" &> /dev/null; then
        echo "正在安装PyInstaller..."
        uv add --dev pyinstaller
    fi
    
    echo "依赖检查通过！"
}

# Windows特定的编译函数
build_windows() {
    echo "正在为Windows平台编译..."
    
    # 创建输出目录
    mkdir -p dist/windows
    
    echo "正在编译GUI版本..."
    uv run pyinstaller \
        --onefile \
        --windowed \
        --name pdf_to_image_gui_windows \
        --distpath dist/windows \
        --workpath build/windows \
        --specpath build/windows \
        gui.py
    
    echo "正在编译CLI版本..."
    uv run pyinstaller \
        --onefile \
        --console \
        --name pdf_to_image_cli_windows \
        --distpath dist/windows \
        --workpath build/windows \
        --specpath build/windows \
        main.py
    
    echo "Windows版本编译完成！"
    echo "GUI版本: dist/windows/pdf_to_image_gui_windows.exe"
    echo "CLI版本: dist/windows/pdf_to_image_cli_windows.exe"
    
    # 测试编译结果
    if [ -f "dist/windows/pdf_to_image_cli_windows.exe" ]; then
        echo "正在测试编译结果..."
        if ./dist/windows/pdf_to_image_cli_windows.exe --help > /dev/null 2>&1; then
            echo "✓ 测试成功！"
        else
            echo "⚠ 测试失败，但文件已生成"
        fi
    fi
}

# Linux特定的编译函数
build_linux() {
    echo "正在为Linux平台编译..."
    
    # 创建输出目录
    mkdir -p dist/linux
    
    echo "正在编译GUI版本..."
    uv run pyinstaller \
        --onefile \
        --windowed \
        --name pdf_to_image_gui_linux \
        --distpath dist/linux \
        --workpath build/linux \
        --specpath build/linux \
        gui.py
    
    echo "正在编译CLI版本..."
    uv run pyinstaller \
        --onefile \
        --console \
        --name pdf_to_image_cli_linux \
        --distpath dist/linux \
        --workpath build/linux \
        --specpath build/linux \
        main.py
    
    # 重命名文件以移除.exe后缀
    if [ -f "dist/linux/pdf_to_image_gui_linux.exe" ]; then
        mv "dist/linux/pdf_to_image_gui_linux.exe" "dist/linux/pdf_to_image_gui_linux"
    fi
    if [ -f "dist/linux/pdf_to_image_cli_linux.exe" ]; then
        mv "dist/linux/pdf_to_image_cli_linux.exe" "dist/linux/pdf_to_image_cli_linux"
    fi
    
    # 设置可执行权限
    chmod +x dist/linux/pdf_to_image_gui_linux
    chmod +x dist/linux/pdf_to_image_cli_linux
    
    echo "Linux版本编译完成！"
    echo "GUI版本: dist/linux/pdf_to_image_gui_linux"
    echo "CLI版本: dist/linux/pdf_to_image_cli_linux"
    
    # 测试编译结果
    echo "正在测试编译结果..."
    if ./dist/linux/pdf_to_image_cli_linux --help > /dev/null 2>&1; then
        echo "✓ 测试成功！"
    else
        echo "⚠ 测试失败，请检查编译结果"
    fi
}

# macOS特定的编译函数
build_macos() {
    echo "正在为macOS平台编译..."
    
    # 创建输出目录
    mkdir -p dist/macos
    
    echo "正在编译GUI版本..."
    uv run pyinstaller \
        --onefile \
        --windowed \
        --name "PDF转图片工具_macos" \
        --distpath dist/macos \
        --workpath build/macos \
        --specpath build/macos \
        gui.py
    
    echo "正在编译CLI版本..."
    uv run pyinstaller \
        --onefile \
        --console \
        --name pdf_to_image_cli_macos \
        --distpath dist/macos \
        --workpath build/macos \
        --specpath build/macos \
        main.py
    
    # 重命名文件以移除.exe后缀
    if [ -f "dist/macos/PDF转图片工具_macos.exe" ]; then
        mv "dist/macos/PDF转图片工具_macos.exe" "dist/macos/PDF转图片工具_macos"
    fi
    if [ -f "dist/macos/pdf_to_image_cli_macos.exe" ]; then
        mv "dist/macos/pdf_to_image_cli_macos.exe" "dist/macos/pdf_to_image_cli_macos"
    fi
    
    # 设置可执行权限
    chmod +x dist/macos/pdf_to_image_cli_macos
    if [ -f "dist/macos/PDF转图片工具_macos" ]; then
        chmod +x "dist/macos/PDF转图片工具_macos"
    fi
    
    echo "macOS版本编译完成！"
    echo "GUI版本: dist/macos/PDF转图片工具_macos"
    echo "CLI版本: dist/macos/pdf_to_image_cli_macos"
    echo "注意: 首次运行可能需要在系统偏好设置中允许运行未签名的应用"
    
    # 测试编译结果
    echo "正在测试编译结果..."
    if ./dist/macos/pdf_to_image_cli_macos --help > /dev/null 2>&1; then
        echo "✓ 测试成功！"
    else
        echo "⚠ 测试失败，请检查编译结果"
    fi
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -p, --platform 指定目标平台 (windows|linux|macos|all)"
    echo "  --clean        清理dist目录"
    echo ""
    echo "示例:"
    echo "  $0              # 为当前平台编译"
    echo "  $0 -p windows   # 仅编译Windows版本"
    echo "  $0 -p all       # 编译所有平台版本"
    echo "  $0 --clean      # 清理编译输出"
}

# 清理编译输出
clean_dist() {
    echo "正在清理dist目录..."
    rm -rf dist
    echo "清理完成！"
}

# 主函数
main() {
    local target_platform=""
    local clean_only=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -p|--platform)
                target_platform="$2"
                shift 2
                ;;
            --clean)
                clean_only=true
                shift
                ;;
            *)
                echo "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 如果只是清理，执行清理后退出
    if [ "$clean_only" = true ]; then
        clean_dist
        exit 0
    fi
    
    # 检测当前操作系统
    OS=$(detect_os)
    echo "检测到操作系统: $OS"
    
    # 如果未指定平台，使用当前平台
    if [ -z "$target_platform" ]; then
        target_platform="$OS"
    fi
    
    # 检查依赖
    check_dependencies
    
    echo "正在安装依赖..."
    uv sync
    
    echo "正在安装PyInstaller..."
    uv add --dev pyinstaller
    
    # 根据目标平台执行编译
    case $target_platform in
        windows)
            build_windows
            ;;
        linux)
            build_linux
            ;;
        macos)
            build_macos
            ;;
        all)
            echo "正在为所有平台编译..."
            build_windows
            build_linux
            build_macos
            ;;
        *)
            echo "错误: 不支持的平台 '$target_platform'"
            echo "支持的平台: windows, linux, macos, all"
            exit 1
            ;;
    esac
    
    echo ""
    echo "=========================================="
    echo "构建完成！请查看dist目录下的对应平台文件夹"
    echo "=========================================="
}

# 运行主函数
main "$@"
import argparse
import os
import sys
import io
from pathlib import Path
from typing import List, Optional
import fitz  # PyMuPDF
from PIL import Image


def pdf_to_images(
    pdf_path: str,
    output_dir: Optional[str] = None,
    output_format: str = "PNG",
    dpi: int = 200,
    page_range: Optional[tuple] = None,
    log_callback: Optional[callable] = None
) -> List[str]:
    """
    将PDF文件转换为图片
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录，默认为PDF文件同目录
        output_format: 输出格式 (PNG, JPEG, TIFF等)
        dpi: 图片分辨率，默认200
        page_range: 页面范围 (开始页, 结束页)，从1开始计数
        log_callback: 日志回调函数，用于GUI显示
    
    Returns:
        生成的图片文件路径列表
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
    
    if output_dir is None:
        output_dir = os.path.dirname(pdf_path)
    
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_name = Path(pdf_path).stem
    
    try:
        # 打开PDF文档
        pdf_document = fitz.open(pdf_path)
        
        # 计算缩放因子
        zoom = dpi / 72.0  # PyMuPDF使用72 DPI作为基准
        mat = fitz.Matrix(zoom, zoom)
        
        # 确定页面范围
        total_pages = len(pdf_document)
        if page_range:
            start_page = max(0, page_range[0] - 1)  # 转换为0索引
            end_page = min(total_pages, page_range[1])
        else:
            start_page = 0
            end_page = total_pages
        
        output_files = []
        
        for page_num in range(start_page, end_page):
            try:
                page = pdf_document[page_num]
                
                # 渲染页面为图片
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # 转换为PIL Image
                img_data = pix.tobytes("ppm")
                pil_img = Image.open(io.BytesIO(img_data))
                
                # 生成输出文件名
                actual_page_num = page_num + 1
                output_filename = f"{pdf_name}_page_{actual_page_num:03d}.{output_format.lower()}"
                output_path = os.path.join(output_dir, output_filename)
                
                # 保存图片
                pil_img.save(output_path, output_format)
                output_files.append(output_path)
                
                message = f"已保存: {output_path}"
                if log_callback:
                    log_callback(message)
                else:
                    print(message)
                    
            except Exception as e:
                error_message = f"保存页面 {page_num + 1} 失败: {str(e)}"
                if log_callback:
                    log_callback(error_message)
                else:
                    print(error_message)
        
        pdf_document.close()
        
    except Exception as e:
        raise RuntimeError(f"PDF转换失败: {str(e)}")
    
    return output_files


def multi_pdf_to_images(
    pdf_paths: List[str],
    output_dir: str,
    output_format: str = "PNG",
    dpi: int = 200,
    log_callback: Optional[callable] = None
) -> List[str]:
    """
    批量将多个PDF文件转换为图片，为每个PDF文件创建单独的文件夹
    
    Args:
        pdf_paths: PDF文件路径列表
        output_dir: 输出目录
        output_format: 输出格式 (PNG, JPEG, TIFF等)
        dpi: 图片分辨率，默认200
        log_callback: 日志回调函数，用于GUI显示
    
    Returns:
        生成的图片文件路径列表
    """
    all_output_files = []
    
    for pdf_path in pdf_paths:
        if not os.path.exists(pdf_path):
            error_msg = f"PDF文件不存在: {pdf_path}"
            if log_callback:
                log_callback(error_msg)
            else:
                print(error_msg)
            continue
            
        # 为每个PDF创建单独的子文件夹
        pdf_name = Path(pdf_path).stem
        pdf_output_dir = os.path.join(output_dir, pdf_name)
        os.makedirs(pdf_output_dir, exist_ok=True)
        
        try:
            if log_callback:
                log_callback(f"开始转换: {os.path.basename(pdf_path)}")
            else:
                print(f"开始转换: {os.path.basename(pdf_path)}")
                
            output_files = pdf_to_images(
                pdf_path,
                pdf_output_dir,
                output_format,
                dpi,
                None,  # 全部页面
                log_callback
            )
            all_output_files.extend(output_files)
            
            if log_callback:
                log_callback(f"完成转换: {os.path.basename(pdf_path)} ({len(output_files)} 个文件)")
            else:
                print(f"完成转换: {os.path.basename(pdf_path)} ({len(output_files)} 个文件)")
                
        except Exception as e:
            error_msg = f"转换失败 {os.path.basename(pdf_path)}: {str(e)}"
            if log_callback:
                log_callback(error_msg)
            else:
                print(error_msg)
    
    return all_output_files


def quality_to_dpi(quality):
    """将清晰度挡位转换为DPI值"""
    quality_map = {
        "一般": 150,
        "清晰": 200, 
        "高清": 300,
        "打印": 600
    }
    return quality_map.get(quality, 200)


def main():
    parser = argparse.ArgumentParser(description="PDF转图片工具")
    parser.add_argument("pdf_paths", nargs='+', help="PDF文件路径（支持多个文件）")
    parser.add_argument("-o", "--output", help="输出目录")
    parser.add_argument("-f", "--format", default="PNG", choices=["PNG", "JPEG", "TIFF"], help="输出图片格式")
    parser.add_argument("-q", "--quality", default="清晰", choices=["一般", "清晰", "高清", "打印"], help="图片清晰度")
    parser.add_argument("-d", "--dpi", type=int, help="自定义DPI值（会覆盖清晰度设置）")
    parser.add_argument("--pages", help="页面范围，格式: start-end 或 start (例: 1-5 或 3)，仅适用于单文件")
    
    args = parser.parse_args()
    
    # 多文件时不支持页面范围
    if len(args.pdf_paths) > 1 and args.pages:
        print("警告: 多文件模式不支持页面范围选择，将转换所有页面")
        args.pages = None
    
    # 确定DPI值
    if args.dpi:
        dpi = args.dpi
        print(f"使用自定义DPI: {dpi}")
    else:
        dpi = quality_to_dpi(args.quality)
        print(f"使用清晰度: {args.quality} ({dpi} DPI)")
    
    page_range = None
    if args.pages and len(args.pdf_paths) == 1:
        try:
            if "-" in args.pages:
                start, end = map(int, args.pages.split("-"))
                page_range = (start, end)
            else:
                page_num = int(args.pages)
                page_range = (page_num, page_num)
        except ValueError:
            print("错误: 页面范围格式不正确，应为 'start-end' 或 'start'")
            return 1
    
    try:
        if len(args.pdf_paths) == 1:
            # 单文件模式
            output_files = pdf_to_images(
                args.pdf_paths[0],
                args.output,
                args.format,
                dpi,
                page_range
            )
        else:
            # 多文件模式
            if not args.output:
                # 如果没有指定输出目录，使用第一个文件的目录
                args.output = os.path.dirname(args.pdf_paths[0])
            
            print(f"开始批量转换 {len(args.pdf_paths)} 个PDF文件...")
            output_files = multi_pdf_to_images(
                args.pdf_paths,
                args.output,
                args.format,
                dpi
            )
        
        print(f"\n转换完成! 共生成 {len(output_files)} 个图片文件")
        if len(args.pdf_paths) > 1:
            print(f"各文件已分别保存到独立文件夹中")
        return 0
        
    except (FileNotFoundError, RuntimeError) as e:
        print(f"错误: {str(e)}")
        return 1
    except Exception as e:
        print(f"未知错误: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
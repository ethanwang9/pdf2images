# PDF转图片工具 - 项目记忆文件

## 技术栈
- Python 3.13.5 + uv依赖管理
- **PyMuPDF** + Pillow + tkinterdnd2 + customtkinter
- tkinter GUI + 命令行CLI双模式
- **无需外部依赖** - 不再需要poppler工具

## 核心文件
- `main.py`: CLI模式，支持单文件和多文件转换，使用PyMuPDF进行PDF处理和图片转换
- `gui.py`: GUI模式，支持多文件选择，现代化自定义窗口界面，卡片式布局
- `run_gui.bat`: Windows GUI启动脚本
- `README.md`: 用户文档，包含完整的使用说明和功能介绍
- `CLAUDE.md`: 项目记忆文件（本文件），包含开发细节和技术实现

## 启动方式
```bash
# GUI模式（推荐）
uv run gui.py

# CLI模式 - 单文件
uv run main.py document.pdf -o output/ -f PNG -q 高清 --pages 1-5

# CLI模式 - 多文件
uv run main.py file1.pdf file2.pdf file3.pdf -o output/ -f PNG -q 打印

# CLI模式 - 自定义DPI（会覆盖清晰度设置）
uv run main.py document.pdf -o output/ -d 400
```

## 清晰度设置功能
```python
def quality_to_dpi(quality):
    quality_map = {
        "一般": 150,  # 快速预览和网页显示
        "清晰": 200,  # 默认设置，平衡质量和文件大小
        "高清": 300,  # 高质量显示，适合印刷前预览
        "打印": 600   # 最高质量，适合专业印刷
    }
    return quality_map.get(quality, 200)
```

## 输出文件组织结构

### 单文件模式
```
输出目录/
├── document_page_001.png
├── document_page_002.png
└── document_page_003.png
```

### 多文件模式
```
输出目录/
├── file1/
│   ├── file1_page_001.png
│   ├── file1_page_002.png
│   └── file1_page_003.png
├── file2/
│   ├── file2_page_001.png
│   └── file2_page_002.png
└── file3/
    ├── file3_page_001.png
    ├── file3_page_002.png
    ├── file3_page_003.png
    └── file3_page_004.png
```

## 关键实现细节

### GUI多文件支持实现
```python
# 文件列表管理
self.current_pdfs = []  # 改为文件列表

# 多文件拖拽处理
def on_drop(self, event):
    files = self.root.tk.splitlist(event.data)
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    if pdf_files:
        self.current_pdfs.extend(pdf_files)
        self.update_file_list()

# 多文件选择处理
def browse_file(self, event=None):
    file_paths = filedialog.askopenfilenames(...)
    if file_paths:
        self.current_pdfs.extend(file_paths)
        self.update_file_list()
```

### 页面范围智能控制
```python
def on_pages_mode_change(self):
    # 多文件时强制全部页面模式并禁用自定义选项
    if len(self.current_pdfs) > 1:
        self.pages_mode_var.set("all")
        # 禁用自定义页面选项
        for widget in self.pages_frame.winfo_children():
            if isinstance(widget, ctk.CTkRadioButton) and widget.cget("value") == "custom":
                widget.configure(state="disabled")
```

### 清晰度转换逻辑
```python
def do_conversion(self):
    quality = self.quality_var.get()
    dpi = self.quality_to_dpi(quality)
    
    # 日志显示格式
    self.log_message(f"格式: {output_format}, 清晰度: {quality} ({dpi} DPI)")
```

## 开发注意事项
- **使用PyMuPDF**：纯Python库，无需外部工具依赖，性能更好
- **CustomTkinter**：现代化UI组件库，支持主题和圆角设计
- **线程处理**：GUI使用线程避免界面卡死
- **完整输入验证**：页面范围边界检查，多文件模式限制
- **错误处理**：覆盖文件不存在、转换失败等情况
- **日志输出**：使用线程安全的回调机制
- **无图标设计**：移除所有装饰性emoji图标，采用纯文字界面
- **多文件支持**：GUI和CLI都完整支持多文件批量处理
- **清晰度挡位**：用户友好的质量选择，自动映射到合适的DPI值
- **状态保存**：记住用户的选择（输出目录模式、格式、清晰度等）
- **界面响应性**：所有长时间操作都在后台线程执行

## 界面组件层次
```
主窗口 (无边框，圆角)
├── 精简标题栏
│   ├── 应用标题
│   └── 关闭按钮
└── 内容区域
    ├── 左侧面板 (75%)
    │   ├── 文件选择卡片 (支持多文件，防重复)
    │   └── 转换设置卡片 (智能页面范围控制)
    └── 右侧面板 (25%)
        ├── 开始转换按钮 (100%宽度)
        └── 运行日志卡片
```
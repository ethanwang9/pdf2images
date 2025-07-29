import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
import os
from pathlib import Path
import fitz  # PyMuPDF
from main import pdf_to_images, multi_pdf_to_images
from tkinter import messagebox, filedialog
import tkinter as tk

# 设置主题和外观
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class CompactPDFToImageGUI:
    def __init__(self):
        # 创建主窗口（无边框）
        self.root = TkinterDnD.Tk()
        self.root.overrideredirect(True)  # 移除默认窗口装饰
        self.root.geometry("900x580")
        self.root.minsize(850, 530)
        self.root.configure(bg="#f5f5f5")
        
        # 窗口拖拽变量
        self.drag_data = {"x": 0, "y": 0}
        
        # 设置现代化样式
        self.setup_styling()
        self.setup_custom_frame()
        self.setup_ui()
        self.setup_drag_drop()
        
        # 当前处理的文件
        self.current_pdfs = []  # 改为文件列表
        self.total_pages = 0
        
        # 初始化界面状态
        self.on_output_mode_change()
        self.on_pages_mode_change()
        
        # 窗口居中
        self.center_window()
        
    def quality_to_dpi(self, quality):
        """将清晰度挡位转换为DPI值"""
        quality_map = {
            "一般": 150,
            "清晰": 200, 
            "高清": 300,
            "打印": 600
        }
        return quality_map.get(quality, 200)
        
    def setup_styling(self):
        """设置现代化样式"""
        self.colors = {
            'primary': '#1976D2',      # 深蓝色主题
            'success': '#388E3C',      # 深绿色
            'warning': '#F57C00',      # 深橙色
            'error': '#D32F2F',        # 深红色
            'surface': '#FFFFFF',      # 白色
            'text_primary': '#212121', # 主要文本
            'text_secondary': '#757575', # 次要文本
            'background': '#f5f5f5',   # 背景色
            'card': '#ffffff',         # 卡片色
            'border': '#e0e0e0',       # 边框色
            'title_bar': '#2c3e50',    # 标题栏色
            'title_text': '#ffffff'    # 标题文字色
        }
    
    def setup_custom_frame(self):
        """设置自定义窗口框架"""
        # 主容器框架
        self.main_frame = ctk.CTkFrame(
            self.root,
            corner_radius=12,
            fg_color=self.colors['background'],
            border_width=0
        )
        self.main_frame.pack(fill="both", expand=True)
        
        # 自定义标题栏
        self.title_bar = ctk.CTkFrame(
            self.main_frame,
            height=40,
            corner_radius=0,
            fg_color=self.colors['title_bar']
        )
        self.title_bar.pack(fill="x", padx=0, pady=(0, 0))
        self.title_bar.pack_propagate(False)
        
        # 标题栏内容
        title_content = ctk.CTkFrame(self.title_bar, fg_color="transparent")
        title_content.pack(fill="both", expand=True, padx=15, pady=8)
        
        # 应用图标和标题
        title_left = ctk.CTkFrame(title_content, fg_color="transparent")
        title_left.pack(side="left", fill="y")
        
        app_icon = ctk.CTkLabel(
            title_left,
            text="",
            font=ctk.CTkFont(size=16),
            text_color=self.colors['title_text']
        )
        app_icon.pack(side="left", padx=(0, 0))
        
        self.title_label = ctk.CTkLabel(
            title_left,
            text="PDF转图片工具",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['title_text']
        )
        self.title_label.pack(side="left")
        
        # 窗口控制按钮
        controls_frame = ctk.CTkFrame(title_content, fg_color="transparent")
        controls_frame.pack(side="right", fill="y")
        
        # 关闭按钮
        self.close_btn = ctk.CTkButton(
            controls_frame,
            text="×",
            width=30,
            height=24,
            corner_radius=4,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="transparent",
            hover_color="#e74c3c",
            text_color=self.colors['title_text'],
            command=self.close_window
        )
        self.close_btn.pack(side="left")
        
        # 绑定拖拽事件
        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.on_drag)
        title_content.bind("<Button-1>", self.start_drag)
        title_content.bind("<B1-Motion>", self.on_drag)
        self.title_label.bind("<Button-1>", self.start_drag)
        self.title_label.bind("<B1-Motion>", self.on_drag)
        app_icon.bind("<Button-1>", self.start_drag)
        app_icon.bind("<B1-Motion>", self.on_drag)
        
        # 内容区域容器
        self.content_container = ctk.CTkFrame(
            self.main_frame,
            corner_radius=0,
            fg_color=self.colors['background']
        )
        self.content_container.pack(fill="both", expand=True, padx=0, pady=0)
        
    def start_drag(self, event):
        """开始拖拽窗口"""
        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root
        
    def on_drag(self, event):
        """拖拽窗口"""
        x = self.root.winfo_x() + (event.x_root - self.drag_data["x"])
        y = self.root.winfo_y() + (event.y_root - self.drag_data["y"])
        self.root.geometry(f"+{x}+{y}")
        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root
        
    def close_window(self):
        """关闭窗口"""
        self.root.quit()
        
    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_ui(self):
        """设置紧凑的用户界面"""
        # 主容器使用网格布局
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)
        
        # 创建可滚动的主框架
        main_scrollable = ctk.CTkScrollableFrame(
            self.content_container, 
            corner_radius=0,
            fg_color=self.colors['background'],
            scrollbar_button_color=self.colors['border'],
            scrollbar_button_hover_color=self.colors['text_secondary']
        )
        main_scrollable.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        main_scrollable.grid_columnconfigure(0, weight=1)
        
        # 主要内容区域 - 左右分栏
        content_frame = ctk.CTkFrame(main_scrollable, fg_color=self.colors['background'])
        content_frame.grid(row=0, column=0, sticky="ew", pady=(0, 0))
        content_frame.grid_columnconfigure(0, weight=3)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # 左侧控制面板（卡片样式）
        left_panel = ctk.CTkFrame(
            content_frame, 
            corner_radius=0, 
            fg_color=self.colors['background']
        )
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        # 右侧日志面板（卡片样式）
        right_panel = ctk.CTkFrame(
            content_frame, 
            corner_radius=0, 
            fg_color=self.colors['background']
        )
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        self.setup_left_panel(left_panel)
        self.setup_right_panel(right_panel)
        
    def setup_left_panel(self, parent):
        """设置左侧控制面板"""
        parent.grid_columnconfigure(0, weight=1)
        
        # 文件选择卡片
        file_card = ctk.CTkFrame(
            parent, 
            corner_radius=8, 
            fg_color=self.colors['card'],
            border_width=1,
            border_color=self.colors['border']
        )
        file_card.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10))
        file_card.grid_columnconfigure(0, weight=1)
        
        # 文件选择标题栏（包含标题和清空按钮）
        title_frame = ctk.CTkFrame(file_card, fg_color=self.colors['card'])
        title_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        title_frame.grid_columnconfigure(0, weight=1)
        
        # 左侧标题
        ctk.CTkLabel(
            title_frame,
            text="选择PDF文件（支持多文件）",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        ).grid(row=0, column=0, sticky="w")
        
        # 右侧清空按钮
        clear_btn = ctk.CTkButton(
            title_frame,
            text="清空",
            command=self.clear_all,
            width=60,
            height=28,
            font=ctk.CTkFont(size=14),
            fg_color=self.colors['warning'],
            hover_color="#EF6C00"
        )
        clear_btn.grid(row=0, column=1, sticky="e")
        
        # 拖拽区域 - 更紧凑
        self.drop_frame = ctk.CTkFrame(
            file_card,
            height=80,
            fg_color="#f8f9fa",
            border_width=2,
            border_color=self.colors['primary'],
            corner_radius=8
        )
        self.drop_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
        self.drop_frame.grid_propagate(False)
        self.drop_frame.grid_columnconfigure(0, weight=1)
        
        drop_label = ctk.CTkLabel(
            self.drop_frame,
            text="拖拽PDF文件到这里或点击选择（支持多文件）",
            font=ctk.CTkFont(size=16),
            text_color=self.colors['primary']
        )
        drop_label.grid(row=0, column=0, pady=25)
        
        # 绑定点击事件到拖拽区域
        self.drop_frame.bind("<Button-1>", self.browse_file)
        drop_label.bind("<Button-1>", self.browse_file)
        
        # 文件信息显示 - 改为滚动文本框以显示多个文件
        self.file_listbox = ctk.CTkTextbox(
            file_card,
            height=80,
            corner_radius=6,
            font=ctk.CTkFont(size=14),
            fg_color="#f8f9fa",
            border_width=1,
            border_color=self.colors['border'],
            state="disabled"
        )
        self.file_listbox.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 10))
        self.file_listbox.insert("1.0", "未选择文件")
        
        # PDF信息
        self.pdf_info_var = ctk.StringVar(value="")
        self.pdf_info_label = ctk.CTkLabel(
            file_card,
            textvariable=self.pdf_info_var,
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_primary'],
            anchor="e"
        )
        self.pdf_info_label.grid(row=3, column=0, sticky="e", padx=12, pady=(0, 12))
        
        settings_card = ctk.CTkFrame(
            parent, 
            corner_radius=8, 
            fg_color=self.colors['card'],
            border_width=1,
            border_color=self.colors['border']
        )
        settings_card.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 10))
        settings_card.grid_columnconfigure((0, 1), weight=1)
        
        # 输出目录 - 两行布局
        ctk.CTkLabel(
            settings_card,
            text="输出目录:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 5))
        
        self.output_mode_var = ctk.StringVar(value="same")
        output_radio_frame = ctk.CTkFrame(settings_card, fg_color=self.colors['card'])
        output_radio_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        
        ctk.CTkRadioButton(
            output_radio_frame,
            text="源文件目录",
            variable=self.output_mode_var,
            value="same",
            command=self.on_output_mode_change,
            font=ctk.CTkFont(size=16)
        ).pack(side="left", padx=(0, 15))
        
        ctk.CTkRadioButton(
            output_radio_frame,
            text="自定义目录",
            variable=self.output_mode_var,
            value="custom",
            command=self.on_output_mode_change,
            font=ctk.CTkFont(size=16)
        ).pack(side="left")
        
        # 自定义目录输入
        self.custom_frame = ctk.CTkFrame(settings_card, fg_color=self.colors['card'])
        self.custom_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 10))
        self.custom_frame.grid_columnconfigure(0, weight=1)
        
        self.output_var = ctk.StringVar()
        self.output_entry = ctk.CTkEntry(
            self.custom_frame,
            textvariable=self.output_var,
            placeholder_text="选择输出目录...",
            state="disabled",
            height=28,
            font=ctk.CTkFont(size=16)
        )
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        self.output_browse_btn = ctk.CTkButton(
            self.custom_frame,
            text="浏览",
            command=self.browse_output_dir,
            state="disabled",
            width=30,
            height=28
        )
        self.output_browse_btn.grid(row=0, column=1)
        
        # 格式和DPI - 并排布局
        format_dpi_frame = ctk.CTkFrame(settings_card, fg_color=self.colors['card'])
        format_dpi_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 10))
        format_dpi_frame.grid_columnconfigure((0, 1), weight=1)
        
        # 输出格式
        ctk.CTkLabel(
            format_dpi_frame,
            text="格式:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.format_var = ctk.StringVar(value="PNG")
        format_combo = ctk.CTkComboBox(
            format_dpi_frame,
            variable=self.format_var,
            values=["PNG", "JPEG", "TIFF"],
            state="readonly",
            width=100,
            height=28,
            font=ctk.CTkFont(size=16)
        )
        format_combo.grid(row=1, column=0, sticky="w", padx=(0, 10))
        
        # DPI设置
        ctk.CTkLabel(
            format_dpi_frame,
            text="清晰度:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        ).grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        self.quality_var = ctk.StringVar(value="高清")
        quality_combo = ctk.CTkComboBox(
            format_dpi_frame,
            variable=self.quality_var,
            values=["一般", "清晰", "高清", "打印"],
            state="readonly",
            width=100,
            height=28,
            font=ctk.CTkFont(size=16)
        )
        quality_combo.grid(row=1, column=1, sticky="w")
        
        # 页面范围设置
        self.pages_frame = ctk.CTkFrame(settings_card, fg_color=self.colors['card'])
        self.pages_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))
        
        ctk.CTkLabel(
            self.pages_frame,
            text="页面范围:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 5))
        
        self.pages_mode_var = ctk.StringVar(value="all")
        
        ctk.CTkRadioButton(
            self.pages_frame,
            text="全部",
            variable=self.pages_mode_var,
            value="all",
            command=self.on_pages_mode_change,
            font=ctk.CTkFont(size=16)
        ).grid(row=1, column=0, sticky="w", padx=(0, 10))
        
        ctk.CTkRadioButton(
            self.pages_frame,
            text="自定义",
            variable=self.pages_mode_var,
            value="custom",
            command=self.on_pages_mode_change,
            font=ctk.CTkFont(size=16)
        ).grid(row=1, column=1, sticky="w", padx=(0, 10))
        
        # 页面范围输入 - 紧凑布局
        self.range_input_frame = ctk.CTkFrame(self.pages_frame, fg_color=self.colors['card'])
        self.range_input_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(5, 0))
        
        ctk.CTkLabel(self.range_input_frame, text="从", font=ctk.CTkFont(size=16)).pack(side="left")
        
        self.start_page_var = ctk.StringVar(value="1")
        self.start_page_entry = ctk.CTkEntry(
            self.range_input_frame,
            textvariable=self.start_page_var,
            width=60,
            height=28,
            state="disabled",
            font=ctk.CTkFont(size=16)
        )
        self.start_page_entry.pack(side="left", padx=(3, 3))
        
        ctk.CTkLabel(self.range_input_frame, text="到", font=ctk.CTkFont(size=16)).pack(side="left")
        
        self.end_page_var = ctk.StringVar(value="1")
        self.end_page_entry = ctk.CTkEntry(
            self.range_input_frame,
            textvariable=self.end_page_var,
            width=60,
            height=28,
            state="disabled",
            font=ctk.CTkFont(size=16)
        )
        self.end_page_entry.pack(side="left", padx=(3, 3))
        
        ctk.CTkLabel(self.range_input_frame, text="页", font=ctk.CTkFont(size=16)).pack(side="left")
        
    def setup_right_panel(self, parent):
        """设置右侧日志面板"""
        parent.grid_rowconfigure(1, weight=1)  # 让日志卡片占据100%高度
        parent.grid_columnconfigure(0, weight=1)
        
        # 开始转换按钮（100%宽度，无卡片）
        self.convert_btn = ctk.CTkButton(
            parent,
            text="开始转换",
            command=self.start_conversion,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=self.colors['success'],
            hover_color="#2E7D32"
        )
        self.convert_btn.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        
        # 运行日志卡片
        log_card = ctk.CTkFrame(
            parent,
            corner_radius=8,
            fg_color=self.colors['card'],
            border_width=1,
            border_color=self.colors['border']
        )
        log_card.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        log_card.grid_rowconfigure(1, weight=1)  # 让日志文本框占据100%高度
        log_card.grid_columnconfigure(0, weight=1)
        
        # 日志标题栏（包含标题和清空日志按钮）
        log_title_frame = ctk.CTkFrame(log_card, fg_color=self.colors['card'])
        log_title_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        log_title_frame.grid_columnconfigure(0, weight=1)
        
        # 左侧标题
        log_title = ctk.CTkLabel(
            log_title_frame,
            text="运行日志",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        )
        log_title.grid(row=0, column=0, sticky="w")
        
        # 右侧清空日志按钮
        clear_log_btn = ctk.CTkButton(
            log_title_frame,
            text="清空日志",
            command=self.clear_log,
            width=80,
            height=28,
            font=ctk.CTkFont(size=14),
            fg_color=self.colors['text_secondary'],
            hover_color="#616161"
        )
        clear_log_btn.grid(row=0, column=1, sticky="e")
        
        # 日志文本框（100%高度）
        self.log_text = ctk.CTkTextbox(
            log_card,
            corner_radius=6,
            font=ctk.CTkFont(size=14),
            fg_color="#f8f9fa",
            border_width=1,
            border_color=self.colors['border']
        )
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        
    def setup_drag_drop(self):
        """设置拖拽功能"""
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)
        
    def toggle_theme(self):
        """切换主题"""
        theme = self.theme_var.get()
        ctk.set_appearance_mode(theme)
        
        # 更新颜色方案
        if theme == "dark":
            self.colors.update({
                'background': '#2b2b2b',
                'card': '#3c3c3c',
                'border': '#555555',
                'title_bar': '#1a1a1a',
                'title_text': '#ffffff',
                'text_primary': '#ffffff',
                'text_secondary': '#cccccc'
            })
        else:
            self.colors.update({
                'background': '#f5f5f5',
                'card': '#ffffff',
                'border': '#e0e0e0',
                'title_bar': '#2c3e50',
                'title_text': '#ffffff',
                'text_primary': '#212121',
                'text_secondary': '#757575'
            })
        
        # 更新主要容器颜色
        self.main_frame.configure(fg_color=self.colors['background'])
        self.title_bar.configure(fg_color=self.colors['title_bar'])
        self.content_container.configure(fg_color=self.colors['background'])
        
        # 更新PDF信息标签颜色
        if hasattr(self, 'pdf_info_label'):
            self.pdf_info_label.configure(text_color=self.colors['text_primary'])
        
    def clear_log(self):
        """清空日志"""
        self.log_text.delete("1.0", "end")
        
    def on_drop(self, event):
        """处理文件拖拽事件 - 支持多文件，防止重复"""
        files = self.root.tk.splitlist(event.data)
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        
        if pdf_files:
            added_count = 0
            for pdf_file in pdf_files:
                # 检查是否已存在
                if pdf_file not in self.current_pdfs:
                    self.current_pdfs.append(pdf_file)
                    self.log_message(f"已添加: {os.path.basename(pdf_file)}")
                    added_count += 1
                else:
                    self.log_message(f"已存在，跳过: {os.path.basename(pdf_file)}")
            
            if added_count > 0:
                self.update_file_list()
        else:
            messagebox.showerror("错误", "请选择PDF文件！")
                
    def browse_file(self, event=None):
        """浏览选择PDF文件 - 支持多文件，防止重复"""
        file_paths = filedialog.askopenfilenames(
            title="选择PDF文件（支持多选）",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        if file_paths:
            added_count = 0
            for file_path in file_paths:
                # 检查是否已存在
                if file_path not in self.current_pdfs:
                    self.current_pdfs.append(file_path)
                    self.log_message(f"已添加: {os.path.basename(file_path)}")
                    added_count += 1
                else:
                    self.log_message(f"已存在，跳过: {os.path.basename(file_path)}")
            
            if added_count > 0:
                self.update_file_list()
                
    def browse_output_dir(self):
        """浏览选择输出目录"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_var.set(dir_path)
            
    def clear_all(self):
        """清空所有设置"""
        self.current_pdfs = []
        self.output_var.set("")
        self.start_page_var.set("1")
        self.end_page_var.set("1")
        self.total_pages = 0
        self.pdf_info_var.set("")
        self.output_mode_var.set("same")
        self.pages_mode_var.set("all")
        self.update_file_list()
        self.on_output_mode_change()
        self.on_pages_mode_change()
        
    def update_file_list(self):
        """更新文件列表显示"""
        self.file_listbox.configure(state="normal")
        self.file_listbox.delete("1.0", "end")
        if not self.current_pdfs:
            self.file_listbox.insert("1.0", "未选择文件")
            self.pdf_info_var.set("")
        else:
            file_list = "\n".join([f"{i+1}. {os.path.basename(pdf)}" 
                                 for i, pdf in enumerate(self.current_pdfs)])
            self.file_listbox.insert("1.0", file_list)
            
            # 计算总页数（多文件时不显示具体页数）
            if len(self.current_pdfs) == 1:
                page_count = self.get_pdf_page_count(self.current_pdfs[0])
                if page_count:
                    self.total_pages = page_count
                    self.pdf_info_var.set(f"总页数: {page_count} 页")
                    if self.pages_mode_var.get() == "all":
                        self.end_page_var.set(str(page_count))
                else:
                    self.total_pages = 0
                    self.pdf_info_var.set("无法读取页面信息")
            else:
                # 多文件模式
                self.total_pages = 0
                self.pdf_info_var.set(f"已选择 {len(self.current_pdfs)} 个PDF文件")
                # 多文件时强制为全部页面模式
                self.pages_mode_var.set("all")
                self.on_pages_mode_change()
        self.file_listbox.configure(state="disabled")
        
    def log_message(self, message):
        """添加日志消息"""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.root.update_idletasks()
        
    def log_message_safe(self, message):
        """线程安全的日志消息"""
        self.root.after(0, lambda: self.log_message(message))
        
    def on_output_mode_change(self):
        """输出目录模式变化处理"""
        if self.output_mode_var.get() == "same":
            self.output_entry.configure(state="disabled")
            self.output_browse_btn.configure(state="disabled")
            self.output_var.set("")
            # 隐藏自定义目录控件
            self.custom_frame.grid_remove()
        else:
            self.output_entry.configure(state="normal")
            self.output_browse_btn.configure(state="normal")
            # 显示自定义目录控件
            self.custom_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 10))
            
    def on_pages_mode_change(self):
        """页面范围模式变化处理"""
        # 多文件时强制全部页面模式并禁用自定义选项
        if len(self.current_pdfs) > 1:
            self.pages_mode_var.set("all")
            # 禁用自定义页面选项
            for widget in self.pages_frame.winfo_children():
                if isinstance(widget, ctk.CTkRadioButton) and widget.cget("value") == "custom":
                    widget.configure(state="disabled")
                    
        else:
            # 启用自定义页面选项
            for widget in self.pages_frame.winfo_children():
                if isinstance(widget, ctk.CTkRadioButton) and widget.cget("value") == "custom":
                    widget.configure(state="normal")
        
        if self.pages_mode_var.get() == "all":
            self.start_page_entry.configure(state="disabled")
            self.end_page_entry.configure(state="disabled")
            self.start_page_var.set("1")
            self.end_page_var.set(str(self.total_pages) if self.total_pages > 0 else "1")
            # 隐藏页面范围输入控件
            self.range_input_frame.grid_remove()
        else:
            self.start_page_entry.configure(state="normal")
            self.end_page_entry.configure(state="normal")
            # 显示页面范围输入控件
            self.range_input_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(5, 0))
            
    def get_pdf_page_count(self, pdf_path):
        """获取PDF页面数"""
        try:
            pdf_document = fitz.open(pdf_path)
            page_count = len(pdf_document)
            pdf_document.close()
            return page_count
        except Exception as e:
            self.log_message(f"读取页数失败: {str(e)}")
            return None
            
    def update_pdf_info(self, pdf_path):
        """更新PDF信息显示"""
        page_count = self.get_pdf_page_count(pdf_path)
        if page_count:
            self.total_pages = page_count
            self.pdf_info_var.set(f"总页数: {page_count} 页")
            if self.pages_mode_var.get() == "all":
                self.end_page_var.set(str(page_count))
            else:
                try:
                    start = int(self.start_page_var.get())
                    end = int(self.end_page_var.get())
                    if start > page_count:
                        self.start_page_var.set("1")
                    if end > page_count:
                        self.end_page_var.set(str(page_count))
                except ValueError:
                    self.start_page_var.set("1")
                    self.end_page_var.set(str(page_count))
        else:
            self.total_pages = 0
            self.pdf_info_var.set("无法读取页面信息")
        
    def validate_inputs(self):
        """验证输入参数"""
        if not self.current_pdfs:
            messagebox.showerror("错误", "请先选择PDF文件！")
            return False
            
        # 检查所有PDF文件是否存在
        for pdf_path in self.current_pdfs:
            if not os.path.exists(pdf_path):
                messagebox.showerror("错误", f"PDF文件不存在：{os.path.basename(pdf_path)}")
                return False
                
        # 单文件时验证页面范围
        if len(self.current_pdfs) == 1 and self.pages_mode_var.get() == "custom":
            try:
                start_page = int(self.start_page_var.get())
                end_page = int(self.end_page_var.get())
                
                if start_page < 1:
                    messagebox.showerror("错误", "起始页面不能小于1！")
                    return False
                    
                if self.total_pages > 0 and start_page > self.total_pages:
                    messagebox.showerror("错误", f"起始页面不能大于总页数({self.total_pages})！")
                    return False
                    
                if end_page < 1:
                    messagebox.showerror("错误", "结束页面不能小于1！")
                    return False
                    
                if self.total_pages > 0 and end_page > self.total_pages:
                    messagebox.showerror("错误", f"结束页面不能大于总页数({self.total_pages})！")
                    return False
                    
                if start_page > end_page:
                    messagebox.showerror("错误", "起始页面不能大于结束页面！")
                    return False
                    
            except ValueError:
                messagebox.showerror("错误", "页面范围必须是数字！")
                return False
                
        return True
        
    def start_conversion(self):
        """开始转换"""
        if not self.validate_inputs():
            return
            
        self.convert_btn.configure(state="disabled")
        
        thread = threading.Thread(target=self.do_conversion)
        thread.daemon = True
        thread.start()
        
    def do_conversion(self):
        """执行转换（在后台线程中）"""
        try:
            if self.output_mode_var.get() == "same":
                if len(self.current_pdfs) == 1:
                    output_dir = os.path.dirname(self.current_pdfs[0])
                else:
                    # 多文件时使用第一个文件的目录
                    output_dir = os.path.dirname(self.current_pdfs[0])
            else:
                output_dir = self.output_var.get() or os.path.dirname(self.current_pdfs[0])
            
            output_format = self.format_var.get()
            quality = self.quality_var.get()
            dpi = self.quality_to_dpi(quality)
            
            if len(self.current_pdfs) == 1:
                # 单文件转换
                pdf_path = self.current_pdfs[0]
                page_range = None
                if self.pages_mode_var.get() == "custom":
                    start_page = int(self.start_page_var.get())
                    end_page = int(self.end_page_var.get())
                    page_range = (start_page, end_page)
                
                self.log_message(f"开始转换: {os.path.basename(pdf_path)}")
                self.log_message(f"输出目录: {os.path.basename(output_dir)}")
                self.log_message(f"格式: {output_format}, 清晰度: {quality} ({dpi} DPI)")
                if page_range:
                    self.log_message(f"页面: {page_range[0]}-{page_range[1]}")
                else:
                    self.log_message("转换所有页面")
                    
                output_files = pdf_to_images(
                    pdf_path,
                    output_dir,
                    output_format,
                    dpi,
                    page_range,
                    self.log_message_safe
                )
            else:
                # 多文件转换
                self.log_message(f"开始批量转换 {len(self.current_pdfs)} 个PDF文件")
                self.log_message(f"输出目录: {os.path.basename(output_dir)}")
                self.log_message(f"格式: {output_format}, 清晰度: {quality} ({dpi} DPI)")
                self.log_message("模式: 全部页面（多文件模式）")
                
                output_files = multi_pdf_to_images(
                    self.current_pdfs,
                    output_dir,
                    output_format,
                    dpi,
                    self.log_message_safe
                )
            
            self.root.after(0, lambda: self.conversion_complete(output_files))
            
        except Exception as e:
            self.root.after(0, lambda: self.conversion_failed(str(e)))
            
    def conversion_complete(self, output_files):
        """转换完成回调"""
        self.convert_btn.configure(state="normal")
        
        self.log_message(f"完成！生成 {len(output_files)} 个文件")
        
        messagebox.showinfo("成功", f"转换完成！\n共生成 {len(output_files)} 个图片文件")
        
    def conversion_failed(self, error_msg):
        """转换失败回调"""
        self.convert_btn.configure(state="normal")
        
        self.log_message(f"失败: {error_msg}")
        messagebox.showerror("错误", f"转换失败：\n{error_msg}")
        
    def run(self):
        """运行GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    app = CompactPDFToImageGUI()
    app.run()
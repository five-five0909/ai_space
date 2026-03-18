import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests
import webbrowser
from PIL import Image, ImageTk
import io
import re
import os
from threading import Thread
from urllib.parse import urlparse

class DouyinAPIViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("抖音链接信息解析工具")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # 设置字体，确保中文显示正常
        self.font_config = ('SimHei', 10)
        
        # 创建主框架，添加最小尺寸限制
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # 输入区域
        self.input_frame = ttk.LabelFrame(self.main_frame, text="输入抖音链接", padding="10")
        self.input_frame.pack(fill=tk.X, pady=5, expand=True)
        
        self.url_var = tk.StringVar()
        # 绑定输入事件，自动提取链接
        self.url_var.trace_add("write", self.auto_extract_url)
        
        self.url_entry = ttk.Entry(self.input_frame, textvariable=self.url_var, width=80, font=self.font_config)
        self.url_entry.pack(padx=5, fill=tk.BOTH, expand=True)

        self.parse_button = ttk.Button(self.input_frame, text="解析链接", command=self.parse_url)
        self.parse_button.pack(pady=5, fill=tk.X, expand=True)

        # 显示提取状态的标签
        self.status_label = ttk.Label(self.input_frame, text="", font=('SimHei', 9))
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # 结果显示区域
        self.result_frame = ttk.LabelFrame(self.main_frame, text="解析结果", padding="10")
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建标签页
        self.tab_control = ttk.Notebook(self.result_frame)
        
        # 基本信息标签页
        self.basic_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.basic_tab, text="基本信息")
        
        # 媒体预览标签页
        self.media_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.media_tab, text="媒体预览")
        
        # 原始数据标签页
        self.raw_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.raw_tab, text="原始数据")
        
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # 基本信息内容
        self.info_text = scrolledtext.ScrolledText(self.basic_tab, wrap=tk.WORD, font=self.font_config)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.config(state=tk.DISABLED)
        
        # 媒体预览内容
        self.media_frame = ttk.Frame(self.media_tab)
        self.media_frame.pack(fill=tk.BOTH, expand=True)
        
        # 封面预览
        self.cover_label = ttk.Label(self.media_frame, text="封面预览:")
        self.cover_label.pack(anchor=tk.W, pady=5)

        # 调整 Canvas 不设置固定大小，使用布局参数适配
        self.cover_canvas = tk.Canvas(self.media_frame, bg="lightgray")
        self.cover_canvas.pack(pady=5, fill=tk.BOTH, expand=True)

        # 按钮区域 - 第二行（下载功能）
        self.button_frame2 = ttk.Frame(self.media_frame)
        self.button_frame2.pack(pady=5, fill=tk.X, expand=True)
        
        self.download_video_btn = ttk.Button(self.button_frame2, text="下载视频", command=self.download_video)
        self.download_video_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.download_music_btn = ttk.Button(self.button_frame2, text="下载音乐", command=self.download_music)
        self.download_music_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 批量下载按钮区域
        self.button_frame3 = ttk.Frame(self.media_frame)
        self.button_frame3.pack(pady=5, fill=tk.X, expand=True)

        self.select_csv_btn = ttk.Button(self.button_frame3, text="选择CSV文件", command=self.select_csv_file)
        self.select_csv_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.batch_download_btn = ttk.Button(self.button_frame3, text="批量下载视频", command=self.batch_download)
        self.batch_download_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.batch_download_btn.config(state=tk.DISABLED)
        
        # 下载进度条
        self.progress_frame = ttk.Frame(self.media_frame)
        self.progress_frame.pack(fill=tk.X, pady=5, padx=10, expand=True)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, expand=True)
        
        self.progress_label = ttk.Label(self.progress_frame, text="准备就绪", font=self.font_config)
        self.progress_label.pack(anchor=tk.W)
        
        # 原始数据内容
        self.raw_text = scrolledtext.ScrolledText(self.raw_tab, wrap=tk.WORD, font=('Consolas', 10))
        self.raw_text.pack(fill=tk.BOTH, expand=True)
        self.raw_text.config(state=tk.DISABLED)
        
        # 存储解析结果
        self.parsed_data = None
        # 用于避免重复触发的标志
        self.is_processing = False
        # 下载线程
        self.download_thread = None
        # 存储批量下载的CSV数据
        self.csv_data = []
        self.csv_file_path = ""
    
    def auto_extract_url(self, *args):
        """自动提取链接"""
        if self.is_processing:
            return
            
        self.is_processing = True
        try:
            input_text = self.url_var.get()
            # 定义抖音链接的正则表达式模式
            pattern = r'https?://[^\s]*douyin\.com[^\s]*'
            matches = re.findall(pattern, input_text)
            
            if matches:
                # 取第一个匹配到的链接
                extracted_url = matches[0]
                # 去除链接中可能存在的多余字符
                extracted_url = re.sub(r'[^\w\-\./:]+$', '', extracted_url)
                
                # 如果提取的链接与当前输入不同，则更新输入框
                if extracted_url != input_text:
                    self.url_var.set(extracted_url)
                    self.status_label.config(text="已自动提取链接", foreground="green")
            else:
                self.status_label.config(text="未检测到抖音链接", foreground="orange")
        except Exception as e:
            self.status_label.config(text=f"提取错误: {str(e)}", foreground="red")
        finally:
            self.is_processing = False
    
    def parse_url(self):
        """解析抖音链接"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("警告", "请输入抖音链接")
            return
        
        # 再次验证链接格式
        if not re.match(r'https?://[^\s]*douyin\.com[^\s]*', url):
            messagebox.showwarning("警告", "请输入有效的抖音链接")
            return
        
        # 更新状态
        self.status_label.config(text="正在解析...", foreground="blue")
        self.root.update()
        
        api_url = "https://api.pearktrue.cn/api/video/douyin/"
        params = {"url": url}
        
        try:
            # 发送请求
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()  # 检查请求是否成功
            
            # 解析JSON
            result = response.json()
            
            # 保存原始数据
            self.raw_text.config(state=tk.NORMAL)
            self.raw_text.delete(1.0, tk.END)
            self.raw_text.insert(tk.END, str(result))
            self.raw_text.config(state=tk.DISABLED)
            
            # 检查解析是否成功
            if result.get("code") == 200:
                self.parsed_data = result.get("data", {})
                self.display_basic_info()
                self.display_cover_image()
                self.status_label.config(text="解析成功", foreground="green")
                
                # 启用下载按钮
                if self.parsed_data.get('url'):
                    self.download_video_btn.config(state=tk.NORMAL)
                if self.parsed_data.get('music_url'):
                    self.download_music_btn.config(state=tk.NORMAL)
            else:
                self.status_label.config(text="解析失败", foreground="red")
                messagebox.showerror("错误", f"解析失败: {result.get('msg', '未知错误')}")
                
        except requests.exceptions.RequestException as e:
            self.status_label.config(text="网络请求失败", foreground="red")
            messagebox.showerror("请求错误", f"网络请求失败: {str(e)}")
        except Exception as e:
            self.status_label.config(text="数据解析失败", foreground="red")
            messagebox.showerror("解析错误", f"数据解析失败: {str(e)}")
    
    def display_basic_info(self):
        """显示基本信息"""
        if not self.parsed_data:
            return
        
        info = []
        info.append("=" * 50)
        info.append("基本信息".center(50))
        info.append("=" * 50)
        info.append(f"账号作者: {self.parsed_data.get('author', '未知')}")
        info.append(f"账号ID: {self.parsed_data.get('author_id', '未知')}")
        info.append(f"视频标题: {self.parsed_data.get('title', '未知')}")
        
        # 计算视频时长（毫秒转换为秒）
        duration_ms = self.parsed_data.get('video_duration', 0)
        duration_sec = duration_ms / 1000
        info.append(f"视频时长: {duration_sec:.2f} 秒")
        
        info.append("-" * 50)
        info.append("链接信息".center(50))
        info.append("-" * 50)
        info.append(f"视频封面: {self.parsed_data.get('cover', '未知')}")
        info.append(f"无水印视频: {self.parsed_data.get('url', '未知')}")
        info.append(f"音乐链接: {self.parsed_data.get('music_url', '未知')}")
        info.append(f"作者头像: {self.parsed_data.get('avatar', '未知')}")
        info.append("=" * 50)
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        for line in info:
            if line.startswith("=") or line.startswith("-"):
                self.info_text.insert(tk.END, line + "\n", ("separator",))
            elif line.endswith("信息"):
                self.info_text.insert(tk.END, line + "\n", ("title",))
            else:
                self.info_text.insert(tk.END, line + "\n")
        self.info_text.tag_config("separator", foreground="gray")
        self.info_text.tag_config("title", foreground="blue", font=('SimHei', 12, 'bold'))
        self.info_text.config(state=tk.DISABLED)
    
    def display_cover_image(self):
        """显示封面图片"""
        if not self.parsed_data:
            return

        cover_url = self.parsed_data.get('cover', '')
        if not cover_url:
            self.cover_canvas.delete("all")
            self.cover_canvas.config(width=200, height=200)
            self.cover_canvas.create_text(100, 100, text="无封面图片", font=self.font_config)
            return

        try:
            # 下载封面图片
            response = requests.get(cover_url, timeout=10)
            image_data = response.content

            # 打开并调整图片大小，进一步压缩图片
            image = Image.open(io.BytesIO(image_data))
            image.thumbnail((200, 200))  # 最大程度压缩图片到 200x200

            # 强制图片同比例缩小，设置 Canvas 尺寸为图片尺寸但不超过最大尺寸
            canvas_width = min(image.width, 200)
            canvas_height = min(image.height, 200)
            self.cover_canvas.config(width=canvas_width, height=canvas_height)
            
            # 在Canvas上居中显示图片
            self.cover_image = ImageTk.PhotoImage(image)
            self.cover_canvas.delete("all")
            # 确保图片在 Canvas 区域居中
            x = canvas_width // 2
            y = canvas_height // 2
            self.cover_canvas.create_image(x, y, image=self.cover_image)

        except Exception as e:
            self.cover_canvas.delete("all")
            self.cover_canvas.config(width=200, height=200)
            self.cover_canvas.create_text(100, 100, text=f"无法加载图片\n{str(e)}", font=self.font_config)
    
    def open_video(self):
        pass

    def open_music(self):
        pass

    def download_video(self):
        """下载视频"""
        if not self.parsed_data or 'url' not in self.parsed_data:
            messagebox.showinfo("提示", "没有可下载的视频链接，请先解析")
            return
        
        video_url = self.parsed_data['url']
        default_filename = self.generate_filename(video_url, "mp4")
        
        # 打开文件对话框
        save_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 文件", "*.mp4"), ("所有文件", "*.*")],
            initialfile=default_filename
        )
        
        if save_path:
            self.download_thread = Thread(target=self._download_file, args=(video_url, save_path, "视频"))
            self.download_thread.daemon = True
            self.download_thread.start()
    
    def download_music(self):
        """下载音乐"""
        if not self.parsed_data or 'music_url' not in self.parsed_data:
            messagebox.showinfo("提示", "没有可下载的音乐链接，请先解析")
            return
        
        music_url = self.parsed_data['music_url']
        default_filename = self.generate_filename(music_url, "mp3")
        
        # 打开文件对话框
        save_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 文件", "*.mp3"), ("所有文件", "*.*")],
            initialfile=default_filename
        )
        
        if save_path:
            self.download_thread = Thread(target=self._download_file, args=(music_url, save_path, "音乐"))
            self.download_thread.daemon = True
            self.download_thread.start()
    
    def generate_filename(self, url, default_ext):
        """生成默认文件名"""
        try:
            # 尝试从URL中提取文件名
            path = urlparse(url).path
            filename = os.path.basename(path)
            
            # 如果提取的文件名有效
            if filename and len(filename) > 3 and '.' in filename:
                return filename
            
            # 否则使用标题或时间戳
            title = self.parsed_data.get('title', '').replace(' ', '_')
            if title:
                return f"{title[:50]}.{default_ext}"
            
            # 如果没有标题，则使用时间戳
            import datetime
            now = datetime.datetime.now()
            return f"douyin_{now.strftime('%Y%m%d_%H%M%S')}.{default_ext}"
            
        except Exception:
            return f"douyin_download.{default_ext}"
    
    def _download_file(self, url, save_path, file_type):
        """实际下载文件的方法（在后台线程中运行）"""
        try:
            # 更新UI状态
            self.root.after(0, lambda: self.progress_label.config(text=f"准备下载{file_type}..."))
            self.root.after(0, lambda: self.progress_var.set(0))
            self.root.after(0, lambda: self.download_video_btn.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.download_music_btn.config(state=tk.DISABLED))
            
            # 发送HEAD请求获取文件大小
            response_head = requests.head(url)
            total_size = int(response_head.headers.get('content-length', 0))
            
            # 开始下载
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # 写入文件
            with open(save_path, 'wb') as f:
                bytes_downloaded = 0
                chunk_size = 1024 * 1024  # 1MB
                
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:  # 过滤掉保持活动的空块
                        f.write(chunk)
                        bytes_downloaded += len(chunk)
                        
                        # 更新进度条
                        progress = min(100, bytes_downloaded * 100 / total_size)
                        self.root.after(0, lambda p=progress: self.progress_var.set(p))
                        self.root.after(0, lambda s=bytes_downloaded, t=total_size: 
                            self.progress_label.config(text=f"已下载: {self.format_size(s)}/{self.format_size(t)}"))
            
            # 下载完成
            self.root.after(0, lambda: self.progress_label.config(text=f"{file_type}下载完成"))
            self.root.after(0, lambda: messagebox.showinfo("成功", f"{file_type}下载完成\n保存路径: {save_path}"))
            
        except Exception as e:
            self.root.after(0, lambda: self.progress_label.config(text=f"{file_type}下载失败"))
            self.root.after(0, lambda: messagebox.showerror("下载错误", f"{file_type}下载失败: {str(e)}"))
        finally:
            # 恢复UI状态
            self.root.after(0, lambda: self.download_video_btn.config(state=tk.NORMAL if self.parsed_data.get('url') else tk.DISABLED))
            self.root.after(0, lambda: self.download_music_btn.config(state=tk.NORMAL if self.parsed_data.get('music_url') else tk.DISABLED))
    
    def format_size(self, size_bytes):
        """格式化文件大小显示"""
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0

        while size_bytes >= 1024 and unit_index < len(units) - 1:
            size_bytes /= 1024
            unit_index += 1

        return f"{size_bytes:.2f} {units[unit_index]}"

    def select_csv_file(self):
        """选择CSV文件"""
        self.csv_file_path = filedialog.askopenfilename(
            title="选择CSV文件",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if self.csv_file_path:
            try:
                # 读取CSV文件
                import csv
                self.csv_data = []

                # 尝试多种编码格式读取CSV文件
                encodings = ['utf-8', 'gbk', 'gb2312']
                csv_content = None

                for encoding in encodings:
                    try:
                        with open(self.csv_file_path, 'r', encoding=encoding) as f:
                            csv_content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue

                if csv_content is None:
                    raise Exception("无法解码CSV文件")

                # 使用StringIO来模拟文件对象
                import io
                csv_file = io.StringIO(csv_content)
                reader = csv.reader(csv_file)

                for row in reader:
                    if len(row) >= 3:  # 确保至少有3列
                        # 清理文件名，移除非法字符
                        title = re.sub(r'[<>:"/\\|?*]', '_', row[1])
                        self.csv_data.append({
                            'id': row[0],
                            'title': title,
                            'url': row[2]
                        })

                if self.csv_data:
                    self.status_label.config(text=f"已加载 {len(self.csv_data)} 个视频链接", foreground="green")
                    self.batch_download_btn.config(state=tk.NORMAL)
                else:
                    self.status_label.config(text="CSV文件为空或格式错误", foreground="red")
                    messagebox.showwarning("警告", "CSV文件为空或格式错误")

            except Exception as e:
                self.status_label.config(text="读取CSV文件失败", foreground="red")
                messagebox.showerror("错误", f"读取CSV文件失败: {str(e)}")

    def batch_download(self):
        """批量下载视频"""
        if not self.csv_data:
            messagebox.showinfo("提示", "请先选择CSV文件")
            return

        # 选择保存目录
        save_dir = filedialog.askdirectory(title="选择保存目录")
        if not save_dir:
            return

        # 在新线程中执行批量下载
        self.batch_thread = Thread(target=self._batch_download_worker, args=(save_dir,))
        self.batch_thread.daemon = True
        self.batch_thread.start()

    def _batch_download_worker(self, save_dir):
        """批量下载工作线程"""
        successful = 0
        failed = 0

        total_videos = len(self.csv_data)

        for i, video_info in enumerate(self.csv_data, 1):
            try:
                # 更新进度
                self.root.after(0, lambda: self.progress_label.config(
                    text=f"正在下载 {i}/{total_videos}: {video_info['title'][:30]}..."
                ))
                self.root.after(0, lambda: self.progress_var.set((i - 1) * 100 / total_videos))

                # 解析视频链接
                api_url = "https://api.pearktrue.cn/api/video/douyin/"
                params = {"url": video_info['url']}

                response = requests.get(api_url, params=params, timeout=10)
                response.raise_for_status()
                result = response.json()

                if result.get("code") == 200:
                    video_url = result.get("data", {}).get('url')
                    if video_url:
                        # 生成文件名
                        filename = f"{video_info['id']}-{video_info['title']}.mp4"
                        # 清理文件名中的非法字符
                        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                        save_path = os.path.join(save_dir, filename)

                        # 下载视频
                        self._download_single_file(video_url, save_path)
                        successful += 1
                    else:
                        failed += 1
                else:
                    failed += 1

            except Exception as e:
                print(f"下载失败 {video_info['title']}: {str(e)}")
                failed += 1

        # 下载完成
        self.root.after(0, lambda: self.progress_var.set(100))
        self.root.after(0, lambda: self.progress_label.config(text="批量下载完成"))
        self.root.after(0, lambda: messagebox.showinfo(
            "完成",
            f"批量下载完成！\n成功: {successful} 个\n失败: {failed} 个\n总计: {total_videos} 个"
        ))

    def _download_single_file(self, url, save_path):
        """下载单个文件"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

        except Exception as e:
            raise Exception(f"下载文件失败: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DouyinAPIViewer(root)
    root.mainloop()
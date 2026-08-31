import sys
import os
import subprocess
import urllib.request
import importlib.util
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

WIDTH = 96
HEIGHT = 68
BYTES_PER_ROW = WIDTH // 8
TOTAL_BYTES = BYTES_PER_ROW * HEIGHT
APP_TITLE = "RobotixInnoBot Logo Converter PRO"

def pillow_installed():
    return importlib.util.find_spec("PIL") is not None

def internet_available():
    urls = [
        "https://pypi.org",
        "https://www.google.com",
        "https://github.com"
    ]
    for url in urls:
        try:
            urllib.request.urlopen(url, timeout=4)
            return True
        except Exception:
            pass
    return False

def install_pillow():
    try:
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "Pillow"
        ])
        return True
    except Exception:
        return False

class InternetWindow:
    def __init__(self):
        self.ready = False
        self.root = tk.Tk()
        self.root.title("اتصال به اینترنت")
        self.root.geometry("520x360")
        self.root.resizable(False, False)
        self.root.configure(bg="#07111f")
        self.build_ui()
        self.check_connection()

    def build_ui(self):
        tk.Label(
            self.root,
            text="🌐",
            font=("Arial", 48),
            bg="#07111f",
            fg="#4de1ff"
        ).pack(pady=(25, 5))

        tk.Label(
            self.root,
            text="بررسی اتصال اینترنت",
            font=("Tahoma", 20, "bold"),
            bg="#07111f",
            fg="white"
        ).pack(pady=5)

        self.message = tk.Label(
            self.root,
            text="در حال بررسی اتصال اینترنت...",
            font=("Tahoma", 11),
            bg="#07111f",
            fg="#a7b6c8",
            wraplength=430,
            justify="center"
        )
        self.message.pack(pady=15)

        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=380,
            mode="indeterminate"
        )
        self.progress.pack(pady=10)

        self.retry_button = ttk.Button(
            self.root,
            text="🔄 تلاش مجدد",
            command=self.check_connection
        )
        self.retry_button.pack(pady=10)

        ttk.Button(
            self.root,
            text="✕ خروج",
            command=self.close
        ).pack(pady=5)

    def check_connection(self):
        self.retry_button.config(state="disabled")
        self.message.config(text="در حال بررسی اتصال اینترنت...")
        self.progress.start(10)
        self.root.after(100, self.perform_check)

    def perform_check(self):
        connected = internet_available()
        self.progress.stop()

        if not connected:
            self.message.config(
                text=(
                    "❌ اتصال اینترنت برقرار نیست.\n\n"
                    "لطفاً کامپیوتر را به اینترنت متصل کنید.\n"
                    "سپس روی «تلاش مجدد» کلیک کنید."
                ),
                fg="#ff8f8f"
            )
            self.retry_button.config(state="normal")
            return

        self.message.config(
            text="✓ اتصال اینترنت برقرار است.",
            fg="#6fffb0"
        )
        self.root.update_idletasks()
        self.root.after(700, self.prepare_libraries)

    def prepare_libraries(self):
        self.retry_button.config(state="disabled")

        if pillow_installed():
            self.message.config(
                text=(
                    "✓ اینترنت متصل است.\n\n"
                    "✓ کتابخانه Pillow از قبل نصب شده است.\n\n"
                    "در حال ورود به برنامه..."
                ),
                fg="#6fffb0"
            )
            self.root.update_idletasks()
            self.root.after(1200, self.finish)
            return

        self.message.config(
            text=(
                "✓ اینترنت متصل است.\n\n"
                "کتابخانه Pillow روی سیستم نصب نیست.\n"
                "در حال دانلود و نصب خودکار..."
            ),
            fg="#4de1ff"
        )

        self.progress.config(mode="indeterminate")
        self.progress.start(10)
        self.root.update_idletasks()

        success = install_pillow()
        self.progress.stop()

        if not success:
            self.message.config(
                text=(
                    "❌ نصب Pillow انجام نشد.\n\n"
                    "لطفاً اتصال اینترنت را بررسی کنید "
                    "و دوباره تلاش کنید."
                ),
                fg="#ff8f8f"
            )
            self.retry_button.config(state="normal")
            return

        self.message.config(
            text=(
                "✓ Pillow با موفقیت نصب شد.\n\n"
                "✓ همه چیز آماده است.\n\n"
                "در حال ورود به محیط تبدیل..."
            ),
            fg="#6fffb0"
        )

        self.root.update_idletasks()
        self.root.after(1200, self.finish)

    def finish(self):
        self.ready = True
        self.root.destroy()

    def close(self):
        self.ready = False
        self.root.destroy()

    def run(self):
        self.root.mainloop()
        return self.ready

setup = InternetWindow()

if not setup.run():
    sys.exit()

try:
    from PIL import Image, ImageOps, ImageEnhance, ImageTk
except ImportError:
    messagebox.showerror(
        "خطا",
        "کتابخانه Pillow قابل بارگذاری نیست."
    )
    sys.exit()

selected_file = None
processed_image = None
generated_data = []

def prepare_image(filename):
    img = Image.open(filename)

    if "A" in img.getbands():
        background = Image.new("RGB", img.size, "white")
        background.paste(
            img,
            (0, 0),
            img.getchannel("A")
        )
        img = background
    else:
        img = img.convert("RGB")

    img = ImageOps.contain(
        img,
        (WIDTH, HEIGHT),
        Image.Resampling.LANCZOS
    )

    canvas = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        "white"
    )

    x = (WIDTH - img.width) // 2
    y = (HEIGHT - img.height) // 2

    canvas.paste(img, (x, y))
    img = canvas

    img = ImageOps.grayscale(img)

    img = ImageEnhance.Contrast(img).enhance(1.4)

    return img

def threshold_image(img, threshold):
    return img.point(
        lambda p: 255 if p >= threshold else 0
    )

def image_to_bytes(img):
    pixels = img.load()
    data = []

    for y in range(HEIGHT):
        for byte_x in range(BYTES_PER_ROW):
            value = 0

            for bit in range(8):
                x = byte_x * 8 + bit
                pixel = pixels[x, y]

                if pixel < 128:
                    value |= 1 << bit

            data.append(value)

    return data

def create_header(data, logo_name):
    text = ""

    text += "/*\n"
    text += "    RobotixInnoBot Logo\n"
    text += "    Generated automatically\n"
    text += "    Resolution: 96x68\n"
    text += "    Format: 1-bit bitmap\n"
    text += f"    Size: {len(data)} bytes\n"
    text += "*/\n\n"

    text += (
        "static unsigned char "
        f"{logo_name}[] = {{\n"
    )

    for i in range(0, len(data), 12):
        chunk = data[i:i + 12]

        text += "    "
        text += ", ".join(
            f"0x{x:02X}"
            for x in chunk
        )

        if i + 12 < len(data):
            text += ","

        text += "\n"

    text += "};\n"

    return text

def valid_cpp_name(name):
    if not name:
        return False

    if not (name[0].isalpha() or name[0] == "_"):
        return False

    for char in name:
        if not (char.isalnum() or char == "_"):
            return False

    return True

def update_preview(img):
    preview_width = 500
    preview_height = 350

    scale_x = preview_width / WIDTH
    scale_y = preview_height / HEIGHT
    scale = min(scale_x, scale_y)

    new_width = int(WIDTH * scale)
    new_height = int(HEIGHT * scale)

    preview = img.resize(
        (new_width, new_height),
        Image.Resampling.NEAREST
    )

    preview_tk = ImageTk.PhotoImage(preview)

    preview_label.config(
        image=preview_tk,
        text=""
    )

    preview_label.image = preview_tk

def update_threshold(value):
    global processed_image

    threshold = int(float(value))

    threshold_value_label.config(
        text=f"Threshold: {threshold}"
    )

    if not selected_file:
        return

    try:
        img = prepare_image(selected_file)
        img = threshold_image(img, threshold)
        processed_image = img
        update_preview(img)
    except Exception as e:
        status_label.config(text=f"خطا: {e}")

def choose_file():
    global selected_file
    global processed_image

    filename = filedialog.askopenfilename(
        title="انتخاب عکس",
        filetypes=[
            (
                "Image Files",
                "*.png *.jpg *.jpeg *.bmp *.gif *.webp"
            ),
            ("PNG", "*.png"),
            ("JPG", "*.jpg *.jpeg"),
            ("BMP", "*.bmp"),
            ("GIF", "*.gif"),
            ("WEBP", "*.webp"),
            ("All Files", "*.*")
        ]
    )

    if not filename:
        return

    selected_file = filename

    filename_label.config(
        text=os.path.basename(filename)
    )

    try:
        original = Image.open(filename)

        img = prepare_image(filename)

        img = threshold_image(
            img,
            threshold_scale.get()
        )

        processed_image = img

        update_preview(img)

        info_label.config(
            text=(
                f"اندازه اصلی: "
                f"{original.width} × {original.height}"
                f"    |    "
                f"خروجی: {WIDTH} × {HEIGHT}"
                f"    |    "
                f"داده: {TOTAL_BYTES} bytes"
            )
        )

        status_label.config(
            text="✓ عکس با موفقیت آماده شد."
        )

    except Exception as e:
        messagebox.showerror("خطا", str(e))

def convert():
    global processed_image
    global generated_data

    if not selected_file:
        messagebox.showwarning(
            "عکس انتخاب نشده",
            "ابتدا یک عکس انتخاب کنید."
        )
        return

    try:
        logo_name = name_entry.get().strip()

        if not logo_name:
            logo_name = "LogoRobotix"

        if not valid_cpp_name(logo_name):
            messagebox.showerror(
                "نام نامعتبر",
                "نام آرایه C++ فقط باید "
                "شامل حروف، اعداد و _ باشد."
            )
            return

        img = prepare_image(selected_file)

        threshold = threshold_scale.get()

        img = threshold_image(
            img,
            threshold
        )

        processed_image = img

        data = image_to_bytes(img)
        generated_data = data

        if len(data) != TOTAL_BYTES:
            raise Exception(
                f"خطا: باید {TOTAL_BYTES} بایت باشد "
                f"ولی {len(data)} بایت تولید شد."
            )

        output = filedialog.asksaveasfilename(
            title="ذخیره Logo.h",
            defaultextension=".h",
            initialfile="Logo.h",
            filetypes=[
                ("C Header", "*.h"),
                ("All Files", "*.*")
            ]
        )

        if not output:
            return

        content = create_header(
            data,
            logo_name
        )

        with open(
            output,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(content)

        update_preview(img)

        status_label.config(
            text=(
                "✓ تبدیل با موفقیت انجام شد\n"
                f"فایل: {output}\n"
                f"حجم داده: {len(data)} bytes"
            )
        )

        messagebox.showinfo(
            "موفق",
            "Logo.h با موفقیت ساخته شد!\n\n"
            f"{output}\n\n"
            f"Resolution: {WIDTH} × {HEIGHT}\n"
            f"Data: {len(data)} bytes"
        )

    except Exception as e:
        messagebox.showerror("خطا", str(e))

def copy_hex():
    if not generated_data:
        messagebox.showwarning(
            "کدی وجود ندارد",
            "ابتدا تصویر را تبدیل کنید."
        )
        return

    text = ", ".join(
        f"0x{x:02X}"
        for x in generated_data
    )

    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()

    messagebox.showinfo(
        "کپی شد",
        "کد HEX با موفقیت کپی شد."
    )

def save_preview():
    if processed_image is None:
        messagebox.showwarning(
            "Preview موجود نیست",
            "ابتدا یک عکس انتخاب کنید."
        )
        return

    filename = filedialog.asksaveasfilename(
        title="ذخیره Preview",
        defaultextension=".png",
        initialfile="Logo_preview.png",
        filetypes=[
            ("PNG", "*.png")
        ]
    )

    if not filename:
        return

    preview = processed_image.resize(
        (WIDTH * 6, HEIGHT * 6),
        Image.Resampling.NEAREST
    )

    preview.save(filename)

    messagebox.showinfo(
        "ذخیره شد",
        "Preview با موفقیت ذخیره شد."
    )

root = tk.Tk()

root.title(APP_TITLE)
root.geometry("1050x720")
root.minsize(900, 650)
root.configure(bg="#07111f")

style = ttk.Style()

try:
    style.theme_use("clam")
except:
    pass

style.configure(
    "TButton",
    font=("Tahoma", 10, "bold"),
    padding=9
)

style.configure(
    "Horizontal.TProgressbar",
    thickness=10
)

header = tk.Frame(
    root,
    bg="#0c192b",
    height=85
)

header.pack(fill="x")
header.pack_propagate(False)

tk.Label(
    header,
    text="🤖 RobotixInnoBot",
    font=("Tahoma", 22, "bold"),
    bg="#0c192b",
    fg="#4de1ff"
).pack(
    side="right",
    padx=30
)

tk.Label(
    header,
    text="Logo Converter PRO",
    font=("Tahoma", 12),
    bg="#0c192b",
    fg="#a7b6c8"
).pack(
    side="right"
)

main = tk.Frame(
    root,
    bg="#07111f"
)

main.pack(
    fill="both",
    expand=True,
    padx=25,
    pady=20
)

left = tk.Frame(
    main,
    bg="#0c192b",
    highlightbackground="#203a56",
    highlightthickness=1,
    width=350
)

left.pack(
    side="left",
    fill="y",
    padx=(0, 15)
)

left.pack_propagate(False)

tk.Label(
    left,
    text="تنظیمات تبدیل",
    font=("Tahoma", 17, "bold"),
    bg="#0c192b",
    fg="white"
).pack(
    pady=(25, 20)
)

tk.Label(
    left,
    text="نام آرایه C++",
    font=("Tahoma", 10, "bold"),
    bg="#0c192b",
    fg="#a7b6c8"
).pack(
    anchor="e",
    padx=25
)

name_entry = tk.Entry(
    left,
    font=("Consolas", 11),
    bg="#07111f",
    fg="white",
    insertbackground="white",
    relief="flat"
)

name_entry.insert(0, "LogoRobotix")

name_entry.pack(
    fill="x",
    padx=25,
    pady=(7, 20),
    ipady=9
)

ttk.Button(
    left,
    text="📁 انتخاب عکس",
    command=choose_file
).pack(
    fill="x",
    padx=25,
    pady=5
)

filename_label = tk.Label(
    left,
    text="هنوز عکسی انتخاب نشده",
    font=("Tahoma", 9),
    bg="#0c192b",
    fg="#a7b6c8",
    wraplength=290
)

filename_label.pack(
    pady=(5, 15)
)

tk.Label(
    left,
    text="Threshold",
    font=("Tahoma", 10, "bold"),
    bg="#0c192b",
    fg="#a7b6c8"
).pack(
    anchor="e",
    padx=25
)

threshold_value_label = tk.Label(
    left,
    text="Threshold: 128",
    font=("Consolas", 11, "bold"),
    bg="#0c192b",
    fg="#4de1ff"
)

threshold_value_label.pack(pady=5)

threshold_scale = tk.Scale(
    left,
    from_=0,
    to=255,
    orient="horizontal",
    length=280,
    resolution=1,
    bg="#0c192b",
    fg="white",
    troughcolor="#07111f",
    highlightthickness=0,
    activebackground="#4de1ff",
    command=update_threshold
)

threshold_scale.set(128)

threshold_scale.pack(
    padx=25,
    pady=(0, 20)
)

ttk.Button(
    left,
    text="⚡ تبدیل به Logo.h",
    command=convert
).pack(
    fill="x",
    padx=25,
    pady=5
)

tools = tk.Frame(
    left,
    bg="#0c192b"
)

tools.pack(
    fill="x",
    padx=25,
    pady=10
)

ttk.Button(
    tools,
    text="📋 کپی HEX",
    command=copy_hex
).pack(
    side="left",
    fill="x",
    expand=True,
    padx=(0, 5)
)

ttk.Button(
    tools,
    text="💾 Preview",
    command=save_preview
).pack(
    side="left",
    fill="x",
    expand=True,
    padx=(5, 0)
)

right = tk.Frame(
    main,
    bg="#0c192b",
    highlightbackground="#203a56",
    highlightthickness=1
)

right.pack(
    side="right",
    fill="both",
    expand=True
)

tk.Label(
    right,
    text="پیش‌نمایش",
    font=("Tahoma", 17, "bold"),
    bg="#0c192b",
    fg="white"
).pack(
    pady=(22, 5)
)

tk.Label(
    right,
    text="96 × 68  |  1-bit  |  816 bytes",
    font=("Consolas", 10),
    bg="#0c192b",
    fg="#4de1ff"
).pack(
    pady=(0, 15)
)

preview_container = tk.Frame(
    right,
    bg="white",
    highlightbackground="#203a56",
    highlightthickness=2
)

preview_container.pack(
    padx=30,
    pady=10,
    fill="both",
    expand=True
)

preview_label = tk.Label(
    preview_container,
    text="PREVIEW\n\n96 × 68",
    font=("Tahoma", 15, "bold"),
    bg="white",
    fg="#333333"
)

preview_label.pack(expand=True)

info_label = tk.Label(
    right,
    text=(
        "اندازه اصلی: ---    |    "
        "خروجی: 96 × 68    |    "
        "داده: 816 bytes"
    ),
    font=("Tahoma", 9),
    bg="#0c192b",
    fg="#a7b6c8"
)

info_label.pack(pady=10)

status_label = tk.Label(
    root,
    text="✓ آماده...",
    font=("Tahoma", 10),
    bg="#07111f",
    fg="#4de1ff"
)

status_label.pack(pady=(0, 12))

root.mainloop()

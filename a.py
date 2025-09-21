import tkinter as tk
import uiautomator2 as u2
import subprocess
import os
from tkinter import messagebox, scrolledtext
import time
from pathlib import Path
from PIL import Image, ImageTk
import threading
import queue
import sys




# ---------------- پنجره اصلی ----------------
root = tk.Tk()
root.title("فرم نمونه PAGE")
root.geometry("900x600")
root.configure(bg="white")

# مسیر کامل adb
adb_path = r"C:\android\sdk\platform-tools\adb.exe"

# اتصال به دستگاه (ممکن است کمی طول بکشد)
d = u2.connect()

def reconnect():
    global PACKAGE_NAME, ACTIVITY_NAME, d

    try:
        # 1. دوباره اتصال به دستگاه
        d = u2.connect()  # reconnect
        log_step("دستگاه دوباره متصل شد")

        # 2. دوباره گرفتن لیست پکیج‌ها
        result = subprocess.run([adb_path, "shell", "pm", "list", "packages"], capture_output=True, text=True)
        packages = [p.replace("package:", "") for p in result.stdout.splitlines()]

        # کلیدواژه‌های اپ‌های پرداختی
        payment_keywords = ["behpardakht", "dey", "pasargad", "saman", "moneytech",
                            "refah", "pardakhtnovin", "tech.pay", "sadad"]

        target_packages = [p for p in packages if any(k in p.lower() for k in payment_keywords)]
        if not target_packages:
            log_step("هیچ اپ پرداختی پیدا نشد", success=False)
            PACKAGE_NAME = None
            ACTIVITY_NAME = None
        else:
            PACKAGE_NAME = target_packages[0]
            ACTIVITY_NAME = get_main_activity(PACKAGE_NAME)
            log_step(f"پکیج هدف: {PACKAGE_NAME}, Activity: {ACTIVITY_NAME}")

        # 3. اجرای اپ روی دستگاه
        if PACKAGE_NAME and ACTIVITY_NAME:
            d.app_stop(PACKAGE_NAME)
            time.sleep(0.5)
            d.app_start(PACKAGE_NAME)
            log_step("اجرای مجدد برنامه روی دستگاه")
        else:
            log_step("اجرای مجدد برنامه ممکن نیست، Package یا Activity یافت نشد", success=False)

    except Exception as e:
        log_step("restart_app_and_reload_packages", success=False, details=str(e))


# ایجاد فولدر log در کنار فایل پایتون (لاگ‌های تستی)
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)

# پوشه‌ی جدا برای logcat
logs_dir = "logcats"
os.makedirs(logs_dir, exist_ok=True)






# گرفتن لیست اپ‌های نصب شده
result = subprocess.run([adb_path, "shell", "pm", "list", "packages"], capture_output=True, text=True)
packages = result.stdout.splitlines()
packages = [p.replace("package:", "") for p in packages]

# کلیدواژه‌های اپ‌های پرداختی
payment_keywords = ["behpardakht", "dey", "pasargad", "saman", "moneytech", "payment", "refah", "pardakhtnovin", "tech.pay", "sadad"]

# پیدا کردن اولین اپ پرداختی
target_packages = [p for p in packages if any(k in p.lower() for k in payment_keywords)]
if not target_packages:
    messagebox.showinfo("هیچ اپ پرداختی پیدا نشد!")
    PACKAGE_NAME = None
else:
    PACKAGE_NAME = target_packages[0]
    d.app_start(PACKAGE_NAME)


def get_main_activity(package_name):
    try:
        result = subprocess.run(
            [adb_path, "shell", "cmd", "package", "resolve-activity", "--brief", package_name],
            capture_output=True, text=True
        )
        output = result.stdout.strip().splitlines()
        if len(output) >= 2:
            # خط دوم معمولاً activity اصلی
            activity = output[1].strip()
            return activity
        else:
            return None
    except Exception as e:
        log_step("get_main_activity", success=False, details=str(e))
        return None

ACTIVITY_NAME = get_main_activity(PACKAGE_NAME)

def runapp():
    subprocess.run([
    adb_path, "shell", "am", "start",
    "-n", f"{PACKAGE_NAME}/{ACTIVITY_NAME}",
    "-S"  # force clear task
    ]) 











# نام فایل لاگ با تاریخ و ساعت (برای لاگ‌مرحله‌ای)
if PACKAGE_NAME:
    log_file = os.path.join(log_dir, PACKAGE_NAME + time.strftime("_%Y%m%d_%H%M%S") + ".txt")
else:
    log_file = os.path.join(log_dir, "device_test_" + time.strftime("_%Y%m%d_%H%M%S") + ".txt")













# ---------------- تصویر صفحه ----------------
# فریم تصویر (راست)
screenlbl = tk.LabelFrame(root, text="صفحه دستگاه", padx=10, pady=10, bd=2, relief="groove", bg="white")
screenlbl.pack(side="right", padx=10, pady=10, fill="y")
image_label = tk.Label(screenlbl)
image_label.pack()

def screenshot():
    """گرفتن اسکرین‌شات و نمایش روی فرم"""
    out_dir = Path("D:/")
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = out_dir / "screen.png"
    try:
        d.screenshot(str(filename))
        img = Image.open(filename)
        img = img.resize((300, 480), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.image = photo
        root.update_idletasks()
    except Exception as e:
        return

def auto_screenshot():
    """اجرای خودکار اسکرین‌شات"""
    screenshot()
    root.after(500, auto_screenshot)  # هر 500 میلی‌ثانیه

# شروع اسکرین‌شات خودکار
auto_screenshot()


runapp()










# ---------------- تابع لاگ نرم افزار ----------------
def log_step(step_name, success=True, details=""):
    status = "✅ موفق" if success else "❌ ناموفق"
    message = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {step_name}: {status}. {details}"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")


# ---------------- مانیتور لاگ (logcat) ----------------
log_process = None
log_thread = None
log_stop_event = threading.Event()
log_queue = queue.Queue()

# کلیدواژه فیلتر لاگ (پیش‌فرض package name + خطاها)
log_keywords = []
#if PACKAGE_NAME:
 #   log_keywords.append(PACKAGE_NAME)
log_keywords.extend(["ERROR", "Exception", "Failed"])

def _logcat_worker(logfile_path, stop_event, q, keywords):
    """کرنل که subprocess adb logcat را اجرا می‌کند و خطوط فیلترشده را ذخیره و به queue می‌دهد"""
    cmd = [adb_path, "logcat", "-v", "time"]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
    except FileNotFoundError as e:
        tk.messagebox.showerror("ADB Error", f"adb پیدا نشد: {adb_path}\n{e}")
        return

    with open(logfile_path, "w", encoding="utf-8") as f:
        while not stop_event.is_set():
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            # فیلتر کردن: اگر keywords تعریف شده، فقط خطوط شامل یکی از آنها را نگه دار
            if keywords:
                matched = any(k in line for k in keywords)
                if not matched:
                    continue
            f.write(line)
            f.flush()
            q.put(line)
        # cleanup
        try:
            proc.terminate()
        except Exception:
            pass

def start_log_monitoring():
    global log_thread, log_stop_event
    if log_thread and log_thread.is_alive():
        messagebox.showinfo("Log", "لاگ‌گیری در حال اجراست.")
        return

    # ساخت نام فایل لاگ نسبی داخل پوشه logs
    log_file_path = os.path.join(logs_dir, time.strftime("logcat_%Y%m%d_%H%M%S.txt"))
    log_stop_event.clear()
    log_thread = threading.Thread(target=_logcat_worker, args=(log_file_path, log_stop_event, log_queue, log_keywords), daemon=True)
    log_thread.start()
    log_step("شروع مانیتورینگ لاگ", details=f"فایل: {log_file_path}")
    # نمایش اطلاع در ui
    status_var.set(f"Log: recording -> {os.path.basename(log_file_path)}")

def stop_log_monitoring():
    global log_stop_event
    log_stop_event.set()
    log_step("توقف مانیتورینگ لاگ")
    status_var.set("Log: stopped")

# تابعی که صف لاگ را در UI نمایش می‌دهد
def poll_log_queue():
    try:
        while True:
            line = log_queue.get_nowait()
            # درج در ترِک متن
            log_text.configure(state="normal")
            log_text.insert(tk.END, line)
            # محدود کردن طول متن به خطوط آخر (مثلاً 1000 خط)
            max_lines = 1000
            if int(log_text.index('end-1c').split('.')[0]) > max_lines:
                log_text.delete('1.0', f'{int(log_text.index("end-1c").split(".")[0]) - max_lines}.0')
            log_text.see(tk.END)
            log_text.configure(state="disabled")
    except queue.Empty:
        pass
    root.after(200, poll_log_queue)












#کلیک ایمن برای اینکه اگر دکمه ای در صفحه نبود پیام بدهد
def safe_click(selector, name):
    """کلیک ایمن روی دکمه با لاگ‌گیری در صورت نبودن یا خطا"""
    try:
        if selector.exists:
            selector.click()
            log_step(f"کلیک روی {name}")
            return True
        else:
            log_step(f"❌ دکمه {name} در این نسخه موجود نیست", success=False)
            return False
    except Exception as e:
        log_step(f"❌ خطا در کلیک {name}", success=False, details=str(e))
        return False













# ---------------- توابع دکمه‌ها ----------------
def report_last():
    try:
        if not safe_click(d(text="تنظیمات"), "تنظیمات"): return
        time.sleep(0.5)

        if not safe_click(d(text="گزارش ها"), "گزارش‌ها"): return
        time.sleep(0.5)

        subprocess.run([adb_path, "shell", "input", "text", "1111"])
        log_step("رمز 1111 وارد شد")  # فقط ثبت رمز
        time.sleep(0.5)

        if not d(textContains="آخرین تراکنش").exists:
            log_step("یا رمز اشتباه وارد شده یا گزینه آخرین تراکنش در منو نیست / عملیات متوقف شد", success=False)
            runapp()
            return

        safe_click(d(textContains="آخرین تراکنش"), "آخرین تراکنش")
        time.sleep(0.5)

        if d(textContains="چاپ").exists:
            safe_click(d(textContains="چاپ"), "چاپ")
            time.sleep(1)

        runapp()
    except Exception as e:
        log_step("report_last", success=False, details=str(e))


def report_daily():
    try:
        if not safe_click(d(text="تنظیمات"), "تنظیمات"): return
        time.sleep(0.5)

        if not safe_click(d(text="گزارش ها"), "گزارش ها"): return
        time.sleep(1)

        subprocess.run([adb_path, "shell", "input", "text", "1111"])
        log_step("رمز 1111 وارد شد")  # فقط ثبت رمز
        time.sleep(1)

        if not d(textContains="روزانه").exists:
            log_step("یا رمز اشتباه وارد شده یا  گزینه روزانه در منو نیست / عملیات متوقف شد", success=False)
            runapp()
            return

        if safe_click(d(textContains="روزانه"), "روزانه"):
            if safe_click(d(textContains="چاپ کامل"), "چاپ کامل"):
                log_step("عملیات چاپ روزانه انجام شد")
        runapp()
    except Exception as e:
        log_step("report_daily", success=False, details=str(e))


def report_general():
    try:
        if not safe_click(d(text="تنظیمات"), "تنظیمات"): return
        time.sleep(0.5)

        if not safe_click(d(text="گزارش ها"), "گزارش ها"): return
        time.sleep(0.5)

        subprocess.run([adb_path, "shell", "input", "text", "1111"])
        log_step("رمز 1111 وارد شد")  # فقط ثبت رمز
        time.sleep(1)

        if not d(text="گزارش سرجمع").exists:
            log_step("یا رمز اشتباه وارد شده یا  گزینه گزارش سرجمع در منو نیست / عملیات متوقف شد", success=False)
            runapp()
            return

        if safe_click(d(text="گزارش سرجمع"), "گزارش سرجمع"):
            time.sleep(0.5)
            safe_click(d(text="تایید"), "تایید")
            time.sleep(0.5)
            safe_click(d(text="چاپ سرجمع"), "چاپ سرجمع")
            log_step("عملیات چاپ سرجمع انجام شد")
            time.sleep(0.5)
        runapp()
    except Exception as e:
        log_step("report_general", success=False, details=str(e))


def configuration_show():
    try:
        if not safe_click(d(text="تنظیمات"), "تنظیمات"): return
        time.sleep(1)

        if not safe_click(d(text="مدیریت دستگاه"), "مدیریت دستگاه"): return
        time.sleep(0.5)

        subprocess.run([adb_path, "shell", "input", "text", "1111"])
        log_step("رمز 1111 وارد شد")  # فقط ثبت رمز
        time.sleep(1)

        if not d(text="مشخصات پیکربندی").exists:
            log_step("یا رمز اشتباه وارد شده یا گزینه پیکربندی در منو نیست / عملیات متوقف شد", success=False)
            runapp()
            return

        if safe_click(d(text="مشخصات پیکربندی"), "مشخصات پیکربندی"):
            if d(text="چاپ پیکربندی").exists:
                safe_click(d(text="چاپ پیکربندی"), "چاپ پیکربندی")
                safe_click(d(textContains="بله"), "تأیید چاپ (بله)")
                log_step("عملیات چاپ پیکربندی انجام شد")
        runapp()
    except Exception as e:
        log_step("configuration_show", success=False, details=str(e))


def configuration_receive():
    try:
        if not safe_click(d(text="تنظیمات"), "تنظیمات"): return
        time.sleep(0.5)

        if not safe_click(d(text="پشتیبانی"), "پشتیبانی"): return
        time.sleep(0.5)

        result = subprocess.run([adb_path, "shell", "date +%H%M"], capture_output=True, text=True)
        time_str = result.stdout.strip()
        subprocess.run([adb_path, "shell", "input", "text", time_str[::-1]])
        log_step("رمز زمان وارد شد")  # ثبت رمز یا زمان
        time.sleep(1)

        if d(textContains="دریافت پیکربندی").exists:
            safe_click(d(textContains="دریافت پیکربندی"), "دریافت پیکربندی")
            log_step("عملیات دریافت پیکربندی انجام شد")
        elif d(textContains="راه اندازی اولیه").exists:
            safe_click(d(textContains="راه اندازی اولیه"), "راه اندازی اولیه")
            log_step("عملیات راه اندازی اولیه انجام شد")
        else:
            log_step("یا رمز اشتباه وارد شده یا  گزینه دریافت پیکربندی در منو نیست / عملیات متوقف شد", success=False)
        time.sleep(5)
        runapp()
    except Exception as e:
        log_step("configuration_receive", success=False, details=str(e))


def printkvc():
    try:
        if not safe_click(d(text="تنظیمات"), "تنظیمات"): return
        time.sleep(0.5)

        if not safe_click(d(text="پشتیبانی"), "پشتیبانی"): return
        time.sleep(0.5)

        # وارد کردن رمز/زمان
        result = subprocess.run([adb_path, "shell", "date +%H%M"], capture_output=True, text=True)
        time_str = result.stdout.strip()
        subprocess.run([adb_path, "shell", "input", "text", time_str[::-1]])
        log_step("رمز/زمان وارد شد", success=True)

        time.sleep(1)

        # بررسی گزینه بعدی جدا از رمز
        if not d(text="چاپ KCV").exists:
            log_step("یا رمز اشتباه وارد شده یا این  گزینه  در منو نیست / عملیات متوقف شد", success=False)
            runapp()
            return

        safe_click(d(text="چاپ KCV"), "چاپ KCV")
        log_step("عملیات چاپ KCV انجام شد", success=True)
        time.sleep(0.5)
        runapp()

    except Exception as e:
        log_step("printkvc", success=False, details=str(e))









# ---------------- UI بخش لاگ ----------------
left_panel = tk.Frame(root, bg="white")
left_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)

controls_frame = tk.LabelFrame(left_panel, text="گزارشات و پیکربندی", padx=10, pady=10, bd=2, relief="groove", bg="white")
controls_frame.pack(fill="x", padx=5, pady=5)

# دکمه‌های قدیمی (report/config) را داخل controls_frame قرار می‌دهیم
report_frame = tk.LabelFrame(controls_frame, text="گزارشات", padx=6, pady=6, bg="white")
report_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nw")
config_frame = tk.LabelFrame(controls_frame, text="پیکربندی", padx=6, pady=6, bg="white")
config_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nw")
setting_frame = tk.LabelFrame(controls_frame, text="تنظیمات", padx=6, pady=6, bg="white")
setting_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nw")


# دکمه‌ها 
tk.Button(report_frame, text="آخرین تراکنش", width=18, command=lambda: threading.Thread(target=report_last, daemon=True).start()).pack(pady=3)
tk.Button(report_frame, text="گزارش روزانه", width=18, command=lambda: threading.Thread(target=report_daily, daemon=True).start()).pack(pady=3)
tk.Button(report_frame, text="گزارش سرجمع", width=18, command=lambda: threading.Thread(target=report_general, daemon=True).start()).pack(pady=3)

tk.Button(config_frame, text="چاپ پیکربندی", width=18, command=lambda: threading.Thread(target=configuration_show, daemon=True).start()).pack(pady=3)
tk.Button(config_frame, text="دریافت پیکربندی", width=18, command=lambda: threading.Thread(target=configuration_receive, daemon=True).start()).pack(pady=3)
tk.Button(config_frame, text="KCV چاپ", width=18, command=lambda: threading.Thread(target=printkvc, daemon=True).start()).pack(pady=3)

tk.Button(setting_frame, text="اجرای مجدد برنامه", width=18, command=lambda: threading.Thread(target=runapp, daemon=True).start()).pack(pady=3)
tk.Button(setting_frame, text="بررسی مجدد اتصال", width=18, command=lambda: threading.Thread(target=reconnect, daemon=True).start()).pack(pady=3)

# Frame برای کنترل لاگ
log_frame = tk.LabelFrame(left_panel, text="Logcat Monitor", padx=6, pady=6, bg="white")
log_frame.pack(fill="both", expand=True, padx=5, pady=5)

btn_start_log = tk.Button(log_frame, text="شروع مانیتورینگ لاگ", bg="#28a745", fg="white", command=start_log_monitoring)
btn_start_log.pack(side="top", pady=4, anchor="w")

btn_stop_log = tk.Button(log_frame, text="توقف مانیتورینگ لاگ", bg="#dc3545", fg="white", command=stop_log_monitoring)
btn_stop_log.pack(side="top", pady=4, anchor="w")





# Text ویجت برای نمایش لاگ زنده
log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.NONE, height=12)
log_text.pack(fill="both", expand=True, pady=4)
log_text.configure(state="disabled")






# وضعیت لاگ
status_var = tk.StringVar(value="Log: stopped")
status_label = tk.Label(log_frame, textvariable=status_var, bg="white")
status_label.pack(anchor="w")






# شروع poling برای بروزرسانی لاگ در UI
root.after(200, poll_log_queue)





# ---------------- اجرای پنجره ----------------
root.mainloop()

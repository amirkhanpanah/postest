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

adb_path = r"C:\android\sdk\platform-tools\adb.exe"

d = u2.connect()  # یا d = u2.connect_usb() برای USB




d(text="موجودی").click()
time.sleep(0.5)
subprocess.run([adb_path, "shell", "input", "text", "1461"])

import tkinter as tk
from tkinter import Image, messagebox, Label, Scale
from detector import detect_image, detect_video, detect_webcam
import webbrowser
import subprocess
import PIL
from PIL import ImageTk, Image
def create_main_window():
    root = tk.Tk()
    root.title("Motor & Car Detector")
    root.geometry("350x450")
    root.resizable(False, False)

    Label(root, text="Motor & Car Detector", font=("Helvetica", 20)).pack(pady=2)

    panel = Label(root)
    panel.pack()

    # Slider chỉnh confidence
    #Label(root, text="Confidence Threshold (%)").pack()
    #conf_slider = Scale(root, from_=10, to=90, orient="horizontal")
    #conf_slider.set(40)
    #conf_slider.pack(pady=5)
    # Tải hình bằng PIL
    image = Image.open("logo.png")
    image = image.resize((100, 100))  # Tuỳ chỉnh kích thước
    photo = ImageTk.PhotoImage(image)

# Thêm Label hiển thị ảnh
    img_label = tk.Label(root, image=photo)
    img_label.image = photo  # Giữ tham chiếu tránh bị garbage collected
    img_label.pack(pady=5)
    # Các nút chức năng
    btn_img = tk.Button(root, text="Nhận diện ẢNH",
                        width=25,
                        command=lambda: detect_image(root))
    btn_img.pack(pady=10)

    btn_vid = tk.Button(root, text="Nhận diện VIDEO",
                        width=25,
                        command=lambda: detect_video(root))
    btn_vid.pack(pady=10)

    btn_webcam = tk.Button(root, text="Nhận diện WEBCAM",
                           width=25,
                           command=lambda: detect_webcam( root))
    btn_webcam.pack(pady=10)

    btn_log = tk.Button(root, text="Mở trang QUẢN LÝ LOG",
                        width=25,
                        command=open_log_dashboard)
    btn_log.pack(pady=10)

    btn_exit = tk.Button(root, text="Thoát",
                         width=25,
                         command=lambda: exttit_app(root))
    btn_exit.pack(pady=10)

    return root

def open_log_dashboard():
    # Chạy Flask nếu chưa chạy, sau đó mở localhost:5000
    try:
        subprocess.Popen(["python", "manage.py"])
        webbrowser.open("http://127.0.0.1:5000")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể mở dashboard:\n{e}")

def exttit_app(root):
    if messagebox.askokcancel("Thoát", "Bạn có chắc muốn thoát?"):
        root.destroy()

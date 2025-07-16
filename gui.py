import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO
import os
import threading

# Load model
model = YOLO("model/best (2).pt")

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Motor & Car Detector")
root.geometry("280x240")
root.resizable(False, False)

# Hiển thị ảnh kết quả
panel = tk.Label(root)
panel.pack()

def get_next_filename(filename_base, extension):
    """Tìm tên file tiếp theo không bị trùng."""
    n = 1
    while True:
        filename = f"{filename_base}_{n}{extension}"
        if not os.path.exists(filename):
            return filename
        n += 1

def detect_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if file_path:
        # Load ảnh
        img = cv2.imread(file_path)

        # Detect
        results = model.predict(source=img, conf=0.4, verbose=False)
        annotated = results[0].plot()

        # Hiển thị ảnh (chuyển BGR -> RGB)
        annotated = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(annotated)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        panel.config(image=img_tk)
        panel.image = img_tk

        # Lưu file
        output_filename = get_next_filename("out_put/output_image", ".jpg")
        cv2.imwrite(output_filename, results[0].plot())
        messagebox.showinfo("Info", f"Saved {output_filename}")

def detect_video():
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov")])
    if file_path:
        # Tạo cửa sổ pop-up mới
        video_window = tk.Toplevel(root)
        video_window.title("Video Detection")

        # Panel hiển thị video trong cửa sổ pop-up
        video_panel = tk.Label(video_window)
        video_panel.pack()

        cap = cv2.VideoCapture(file_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Khởi tạo VideoWriter với tên file không trùng
        output_filename = get_next_filename("out_put/output_video", ".mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

        is_running = True  # Thêm biến is_running
        def update_video():
            nonlocal is_running
            ret, frame = cap.read()
            if not is_running or not ret:
                cap.release()
                out.release()
                cv2.destroyAllWindows()
                messagebox.showinfo("Info", f"Saved {output_filename}")
                video_window.destroy()  # Đóng cửa sổ pop-up khi video kết thúc
                return

            frame = cv2.resize(frame, (640, 360))

            results = model.predict(source=frame, conf=0.7, verbose=False)
            annotated = results[0].plot()
            out.write(annotated)

            # Hiển thị frame
            annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(annotated_rgb)
            img_tk = ImageTk.PhotoImage(image=img_pil)
            video_panel.config(image=img_tk)
            video_panel.image = img_tk

            video_window.after(30, update_video)  # Cập nhật mỗi 30ms

        def stop_video():
            nonlocal is_running
            is_running = False

        # Nút dừng trong cửa sổ pop-up
        stop_button = tk.Button(video_window, text="Dừng", command=stop_video)
        stop_button.pack()

        update_video()  # Bắt đầu cập nhật video

def detect_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Lỗi", "Không thể mở webcam")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect
        results = model.predict(source=frame, conf=0.7, verbose=False)
        annotated = results[0].plot()

        # Hiển thị frame
        annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(annotated_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        panel.config(image=img_tk)
        panel.image = img_tk

        root.update()

        # Thoát nếu nhấn phím 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def exttit_app():
    if messagebox.askokcancel("Thoát", "Bạn có chắc muốn thoát?"):
         root.destroy()

# Nút bấm
btn_img = tk.Button(root, text="Nhận diện ẢNH", command=detect_image)
btn_img.pack(pady=10)

btn_vid = tk.Button(root, text="Nhận diện VIDEO", command=detect_video)
btn_vid.pack(pady=10)

btn_webcam = tk.Button(root, text="Nhận diện WEBCAM", command=detect_webcam)
btn_webcam.pack(pady=10)

btn_exit = tk.Button(root, text="Thoát", command=exttit_app)
btn_exit.pack(pady=10)
root.mainloop()

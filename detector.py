import cv2
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox, Toplevel, Label
from ultralytics import YOLO
from utils import get_next_filename
import json
import csv
import sqlite3
import time
from datetime import datetime
from utils import get_timestamp_filename
import threading
# Load YOLO model
model = YOLO("model/best yolov8n(100epoc).pt")  

# Lưu log DB
def insert_log(input_file, output_file, num_motor, num_car):
    conn = sqlite3.connect("detect_logs.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS detection_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_file TEXT,
            output_file TEXT,
            timestamp TEXT,
            num_motor INT,
            num_car INT
        )
    """)
    c.execute("""
        INSERT INTO detection_logs (input_file, output_file, timestamp, num_motor, num_car)
        VALUES (?, ?, ?, ?, ?)
    """, (input_file, output_file, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), num_motor, num_car))
    conn.commit()
    conn.close()

# Lưu JSON & CSV log chi tiết
def save_detection_log(results, input_file, output_file):
    log_data = []
    for box in results[0].boxes:
        item = {
            "label": results[0].names[int(box.cls)],
            "confidence": float(box.conf),
            "bbox": box.xyxy.tolist()[0]
        }
        log_data.append(item)

    json_name = output_file.replace(".jpg", ".json").replace(".mp4", ".json")
    with open(json_name, "w") as f:
        json.dump(log_data, f, indent=4)

    csv_name = output_file.replace(".jpg", ".csv").replace(".mp4", ".csv")
    with open(csv_name, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["label", "confidence", "x1", "y1", "x2", "y2"])
        writer.writeheader()
        for item in log_data:
            bbox = item["bbox"]
            writer.writerow({
                "label": item["label"],
                "confidence": item["confidence"],
                "x1": bbox[0],
                "y1": bbox[1],
                "x2": bbox[2],
                "y2": bbox[3]
            })

# Nhận diện ẢNH
def detect_image(root):
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if file_path:
        img = cv2.imread(file_path)

        start_time = time.time()
        results = model.predict(source=img, verbose=False)
        elapsed = time.time() - start_time

        labels = [results[0].names[int(box.cls)] for box in results[0].boxes]
        num_motor = labels.count("motorbike") + labels.count("bike")
        num_car = labels.count("car")

        annotated = results[0].plot()
        cv2.putText(annotated, f"Motorbike: {num_motor} Car: {num_car}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.putText(annotated, f"Time: {elapsed:.2f}s",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

        output_filename = get_timestamp_filename("out_put/output_image", ".jpg")
        cv2.imwrite(output_filename, annotated)

        save_detection_log(results, file_path, output_filename)
        insert_log(file_path, output_filename, num_motor, num_car)

        image_window = Toplevel(root)
        image_window.title("Image Detection Result")
        annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(annotated_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        img_label = Label(image_window, image=img_tk)
        img_label.image = img_tk
        img_label.pack()

        messagebox.showinfo("Info", f"Saved {output_filename} + log")

# Nhận diện VIDEO
def detect_video(root):
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov")])
    if not file_path:
        return

    video_window = Toplevel(root)
    video_window.title("Video Detection")

    video_panel = Label(video_window)
    video_panel.pack()

    cap = cv2.VideoCapture(file_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    output_filename = get_timestamp_filename("out_put/output_video", ".mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

    is_running = True
    last_time = time.time()
    total_motor = 0
    total_car = 0

    def update_video():
        nonlocal is_running, last_time, total_motor, total_car
        ret, frame = cap.read()
        if not is_running or not ret:
            cap.release()
            out.release()
            messagebox.showinfo("Info", f"Saved {output_filename}")
            insert_log(file_path, output_filename, total_motor, total_car)
            video_window.destroy()
            return
        frame = cv2.resize(frame, (640, 360))
        current_time = time.time()
        fps_calc = 1 / (current_time - last_time)
        last_time = current_time

        results = model.predict(source=frame, verbose=False)
        labels = [results[0].names[int(box.cls)] for box in results[0].boxes]
        num_motor = labels.count("motorbike") + labels.count("bike")
        num_car = labels.count("car")

        total_motor += num_motor
        total_car += num_car

        annotated = results[0].plot()
        cv2.putText(annotated, f"Motorbike: {num_motor} Car: {num_car}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.putText(annotated, f"FPS: {fps_calc:.2f}",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

        out.write(annotated)

        annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(annotated_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        video_panel.config(image=img_tk)
        video_panel.image = img_tk

        video_window.after(30, update_video)

    def stop_video():
        nonlocal is_running
        is_running = False

    stop_btn = tk.Button(video_window, text="Dừng", command=stop_video)
    stop_btn.pack()

    update_video()

# Nhận diện WEBCAM
import threading

def detect_webcam(root):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        messagebox.showerror("Error", "Không thể mở webcam")
        return

    webcam_window = Toplevel(root)
    webcam_window.title("Webcam Detection")

    video_panel = Label(webcam_window)
    video_panel.pack()

    last_time = time.time()
    is_running = True

    def video_loop():
        nonlocal last_time, is_running
        while is_running:
            ret, frame = cap.read()
            if not ret:
                break

            current_time = time.time()
            fps_calc = 1 / (current_time - last_time)
            last_time = current_time

            results = model.predict(source=frame, verbose=False)
            labels = [results[0].names[int(box.cls)] for box in results[0].boxes]
            num_motor = labels.count("motorbike") + labels.count("motor")
            num_car = labels.count("car")

            annotated = results[0].plot()
            cv2.putText(annotated, f"Motorbike: {num_motor} Car: {num_car}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.putText(annotated, f"FPS: {fps_calc:.2f}",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

            annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(annotated_rgb)
            img_tk = ImageTk.PhotoImage(image=img_pil)

            def update_gui():
                video_panel.config(image=img_tk)
                video_panel.image = img_tk

            webcam_window.after(0, update_gui)

        cap.release()
        output_filename = get_timestamp_filename("out_put/output_webcam", ".jpg")
        cv2.imwrite(output_filename, annotated)
        insert_log("webcam", output_filename, num_motor, num_car)
        messagebox.showinfo("Info", f"Saved last frame {output_filename}")
        webcam_window.destroy()

    def stop_webcam():
        nonlocal is_running
        is_running = False

    stop_btn = tk.Button(webcam_window, text="Dừng", command=stop_webcam)
    stop_btn.pack(pady=5)

    # Chạy thread
    threading.Thread(target=video_loop, daemon=True).start()



    # Gắn phím Esc dừng webcam
    root.bind("<Escape>", lambda e: stop_webcam())

    update_webcam()

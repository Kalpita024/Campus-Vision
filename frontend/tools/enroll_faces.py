"""
tools/enroll_faces.py

Tkinter tool to register a student's face with the webcam.

Run from the frontend/ folder:
    python -m tools.enroll_faces

Steps in the window:
  1. Enter Student ID, Name, Class
  2. Start Camera
  3. Capture Faces (auto-saves ~40 photos - move your head slightly)
  4. Train Model (do this after enrolling one or more students)

Requires: pip install opencv-contrib-python pillow
(Tkinter ships with Python on Windows/macOS. On Ubuntu: sudo apt install python3-tk)
"""

import re
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

# allow running as a plain script too:  python tools/enroll_faces.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2
from PIL import Image, ImageTk

from services import attendance_api
from services.face_recognition import FACES_DIR, detect_faces, preprocess_face, train_model

TARGET_SAMPLES = 40
SAVE_EVERY_N_FRAMES = 4
PREVIEW_SIZE = (640, 480)


class EnrollApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Enroll Student Faces")
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.cap = None
        self.capturing = False
        self.saved = 0
        self.frame_count = 0
        self.student_dir = None
        self.photo = None  # keep reference so Tk doesn't garbage-collect the image

        self._build_ui()

    # ---------------------------------- UI ---------------------------------- #
    def _build_ui(self):
        form = ttk.Frame(self.root, padding=10)
        form.grid(row=0, column=0, sticky="ns")

        self.var_id = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_class = tk.StringVar()

        for r, (label, var) in enumerate(
            [("Student ID", self.var_id), ("Name", self.var_name), ("Class", self.var_class)]
        ):
            ttk.Label(form, text=label).grid(row=r, column=0, sticky="w", pady=4)
            ttk.Entry(form, textvariable=var, width=22).grid(row=r, column=1, pady=4)

        self.btn_camera = ttk.Button(form, text="Start Camera", command=self.toggle_camera)
        self.btn_camera.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(14, 4))

        self.btn_capture = ttk.Button(
            form, text="Capture Faces", command=self.start_capture, state="disabled"
        )
        self.btn_capture.grid(row=4, column=0, columnspan=2, sticky="ew", pady=4)

        ttk.Button(form, text="Train Model", command=self.train).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=4
        )

        self.progress = ttk.Progressbar(form, maximum=TARGET_SAMPLES)
        self.progress.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(14, 4))

        self.status = tk.StringVar(value="Fill in the details and start the camera.")
        ttk.Label(form, textvariable=self.status, wraplength=230, foreground="#555").grid(
            row=7, column=0, columnspan=2, sticky="w", pady=4
        )

        self.video = ttk.Label(self.root)
        self.video.grid(row=0, column=1, padx=10, pady=10)

    # -------------------------------- Camera -------------------------------- #
    def toggle_camera(self):
        if self.cap is None:
            backend = cv2.CAP_DSHOW if sys.platform.startswith("win") else 0
            self.cap = cv2.VideoCapture(0, backend)
            if not self.cap.isOpened():
                self.cap = None
                messagebox.showerror("Camera", "Could not open the webcam.")
                return
            self.btn_camera.config(text="Stop Camera")
            self.btn_capture.config(state="normal")
            self.update_frame()
        else:
            self.stop_camera()

    def stop_camera(self):
        self.capturing = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.video.config(image="")
        self.btn_camera.config(text="Start Camera")
        self.btn_capture.config(state="disabled")

    def update_frame(self):
        if self.cap is None:
            return
        ok, frame = self.cap.read()
        if ok:
            frame = cv2.flip(frame, 1)  # mirror view
            faces = detect_faces(frame)
            display = frame.copy()
            for (x, y, w, h) in faces:
                cv2.rectangle(display, (x, y), (x + w, y + h), (0, 200, 0), 2)

            if self.capturing and faces:
                self.frame_count += 1
                if self.frame_count % SAVE_EVERY_N_FRAMES == 0:
                    largest = max(faces, key=lambda b: b[2] * b[3])
                    face_img = preprocess_face(frame, largest)
                    self.saved += 1
                    cv2.imwrite(str(self.student_dir / f"{self.saved:04d}.jpg"), face_img)
                    self.progress["value"] = self.saved
                    self.status.set(f"Captured {self.saved}/{TARGET_SAMPLES}")
                    if self.saved >= TARGET_SAMPLES:
                        self.finish_capture()

            rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb).resize(PREVIEW_SIZE)
            self.photo = ImageTk.PhotoImage(img)
            self.video.config(image=self.photo)

        self.root.after(15, self.update_frame)

    # ------------------------------- Capturing ------------------------------ #
    def _validate(self):
        sid, name, cls = (v.get().strip() for v in (self.var_id, self.var_name, self.var_class))
        if not (sid and name and cls):
            messagebox.showwarning("Missing info", "Please fill Student ID, Name and Class.")
            return None
        if not re.fullmatch(r"[A-Za-z0-9_-]+", sid):
            messagebox.showwarning("Invalid ID", "Student ID can only use letters, numbers, - and _.")
            return None
        return sid, name, cls

    def start_capture(self):
        info = self._validate()
        if not info:
            return
        sid, _, _ = info
        self.student_dir = FACES_DIR / sid
        self.student_dir.mkdir(parents=True, exist_ok=True)
        # start fresh if re-enrolling the same student
        for old in self.student_dir.glob("*.jpg"):
            old.unlink()
        self.saved = 0
        self.frame_count = 0
        self.progress["value"] = 0
        self.capturing = True
        self.btn_capture.config(state="disabled")
        self.status.set("Capturing... look at the camera and turn your head slightly.")

    def finish_capture(self):
        self.capturing = False
        sid, name, cls = self._validate()
        attendance_api.add_student(sid, name, cls)
        self.btn_capture.config(state="normal")
        self.status.set(f"Saved {self.saved} photos for {name}. Enroll another or click Train Model.")
        messagebox.showinfo("Done", f"{name} enrolled. Click 'Train Model' when finished enrolling.")

    # -------------------------------- Training ------------------------------ #
    def train(self):
        try:
            students, images = train_model()
        except Exception as e:
            messagebox.showerror("Training failed", str(e))
            return
        self.status.set(f"Model trained: {students} students, {images} images.")
        messagebox.showinfo("Trained", f"Model trained on {students} students ({images} images).")

    def on_close(self):
        self.stop_camera()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    EnrollApp(root)
    root.mainloop()
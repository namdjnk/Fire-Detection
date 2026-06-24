import argparse
import time
import sys
import queue
import threading
from collections import deque
from pathlib import Path
from datetime import datetime

import cv2
import numpy as np
import torch
import torch.nn as nn
import requests


# =========================================================
# TELEGRAM — NON-BLOCKING (Queue + Worker Thread)
# =========================================================

TOKEN = "8785726507:AAEfOwRJ7tDqNyy2o3Cshou4BrKPw391pKw"
CHAT_ID = "8343039436"

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# Queue chứa các task gửi — main loop chỉ put vào, không chờ
_tg_queue = queue.Queue(maxsize=20)


def _telegram_worker():
    """Worker chạy ngầm, xử lý queue gửi Telegram."""
    while True:
        task = _tg_queue.get()
        if task is None:
            break  # shutdown signal
        try:
            kind = task.get("kind")
            if kind == "message":
                requests.post(
                    f"{BASE_URL}/sendMessage",
                    data={"chat_id": CHAT_ID, "text": task["text"]},
                    timeout=8
                )
            elif kind == "photo":
                with open(task["path"], "rb") as f:
                    requests.post(
                        f"{BASE_URL}/sendPhoto",
                        data={"chat_id": CHAT_ID, "caption": task["caption"]},
                        files={"photo": f},
                        timeout=15
                    )
        except requests.exceptions.Timeout:
            print("[Telegram] Timeout — bỏ qua, không đơ hệ thống")
        except Exception as e:
            print(f"[Telegram] Lỗi: {e}")
        finally:
            _tg_queue.task_done()


# Khởi động worker thread 1 lần duy nhất
_worker_thread = threading.Thread(
    target=_telegram_worker,
    daemon=True,   # tự tắt khi chương trình thoát
    name="TelegramWorker"
)
_worker_thread.start()


def send_telegram_message(text):
    """Đưa vào queue — KHÔNG block vòng lặp chính."""
    try:
        _tg_queue.put_nowait({"kind": "message", "text": text})
    except queue.Full:
        print("[Telegram] Queue đầy — bỏ qua message")


def send_telegram_photo(photo_path, caption="ALERT"):
    """Đưa vào queue — KHÔNG block vòng lặp chính."""
    try:
        _tg_queue.put_nowait({"kind": "photo", "path": photo_path, "caption": caption})
    except queue.Full:
        print("[Telegram] Queue đầy — bỏ qua photo")


# =========================================================
# FALL MODEL
# =========================================================

class TemporalAttention(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.attn = nn.Linear(hidden_dim, 1)

    def forward(self, lstm_out):
        scores  = self.attn(lstm_out).squeeze(-1)
        weights = torch.softmax(scores, dim=1)
        return (lstm_out * weights.unsqueeze(-1)).sum(dim=1)


class FallLSTM(nn.Module):
    def __init__(self, input_size=102, hidden=128, n_layers=2, dropout=0.3):
        super().__init__()

        self.lstm = nn.LSTM(
            input_size,
            hidden,
            num_layers    = n_layers,
            batch_first   = True,
            dropout       = dropout if n_layers > 1 else 0.0,
            bidirectional = True,
        )

        self.attention = TemporalAttention(hidden * 2)

        self.head = nn.Sequential(
            nn.LayerNorm(hidden * 2),
            nn.Dropout(dropout),
            nn.Linear(hidden * 2, 64),
            nn.GELU(),
            nn.Dropout(dropout * 0.5),
            nn.Linear(64, 2),
        )

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        context     = self.attention(lstm_out)
        return self.head(context)


# =========================================================
# PIPELINE
# =========================================================

class SafetyPipeline:

    def __init__(
        self,
        fire_model_path,
        lstm_model_path,
        device,
        seq_len=20,
        conf_fire=0.45
    ):

        from ultralytics import YOLO

        self.device = device
        self.seq_len = seq_len
        self.conf_fire = conf_fire

        print("=" * 60)
        print("LOADING MODELS...")
        print("=" * 60)

        # FIRE MODEL
        print("Loading fire model...")
        self.fire_model = YOLO(fire_model_path)

        # POSE MODEL
        print("Loading pose model...")
        self.pose_model = YOLO("yolov8n-pose.pt")

        # LSTM
        print("Loading LSTM...")
        self.lstm = FallLSTM().to(device)

        state = torch.load(
            lstm_model_path,
            map_location=device
        )

        self.lstm.load_state_dict(state)
        self.lstm.eval()

        print("READY!")

        # buffers
        self.kp_buffer = deque(maxlen=seq_len)

        # fall confirm
        self.fall_counter = 0
        self.FALL_CONFIRM = 12   # tăng từ 5 → 12 để giảm báo nhầm khi demo

        self.cooldown_timer = 0
        self.COOLDOWN = 30

        # stats
        self.frame_count = 0

        # anti spam telegram
        self.last_fire_alert = 0
        self.last_fall_alert = 0

        self.ALERT_INTERVAL = 10


    # =====================================================
    # KEYPOINTS
    # =====================================================

    def get_keypoints(self, frame):

        results = self.pose_model(
            frame,
            imgsz=640,
            conf=0.3,
            device=self.device,
            verbose=False
        )

        r = results[0]

        if r.keypoints is not None and len(r.keypoints.xyn) > 0:

            boxes = r.boxes.xyxy.cpu().numpy()

            areas = (
                (boxes[:, 2] - boxes[:, 0]) *
                (boxes[:, 3] - boxes[:, 1])
            )

            best = int(np.argmax(areas))

            xy   = r.keypoints.xyn[best].cpu().numpy()   # (17, 2)
            conf = r.keypoints.conf[best].cpu().numpy()  # (17,)
            kp   = np.concatenate([xy, conf[:, None]], axis=1)  # (17, 3)

            annotated = r.plot()

        else:
            kp        = np.zeros((17, 3), dtype=np.float32)
            annotated = frame.copy()

        return kp.flatten().astype(np.float32), annotated  # 51 features


    # =====================================================
    # FIRE DETECT
    # =====================================================

    def detect_fire(self, frame):

        results = self.fire_model(
            frame,
            imgsz=640,
            conf=self.conf_fire,
            device=self.device,
            verbose=False
        )

        r = results[0]

        detections = []

        if r.boxes is not None:

            for box in r.boxes:

                cls_id = int(box.cls[0])

                conf = float(box.conf[0])

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                label = r.names[cls_id]

                detections.append(
                    (
                        label,
                        conf,
                        x1,
                        y1,
                        x2,
                        y2
                    )
                )

        return detections


    # =====================================================
    # FALL DETECT
    # =====================================================

    def detect_fall(self):

        if len(self.kp_buffer) < self.seq_len:
            return False, 0.0

        kps_51 = np.stack(list(self.kp_buffer))       # (T, 51)

        # Tính velocity (delta giữa các frame) — feature quan trọng nhất
        vel      = np.zeros_like(kps_51)              # (T, 51)
        vel[1:]  = kps_51[1:] - kps_51[:-1]
        seq_102  = np.concatenate([kps_51, vel], axis=1)  # (T, 102)

        tensor = torch.tensor(seq_102).unsqueeze(0).to(self.device)

        with torch.no_grad():

            logits = self.lstm(tensor)

            prob = torch.softmax(
                logits,
                dim=1
            )[0, 1].item()

        is_fall = prob > 0.5

        return is_fall, prob


    # =====================================================
    # FALL STATE
    # =====================================================

    def update_fall_state(self, is_fall_raw):

        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
            return False

        if is_fall_raw:
            self.fall_counter += 1
        else:
            self.fall_counter = max(
                0,
                self.fall_counter - 1
            )

        if self.fall_counter >= self.FALL_CONFIRM:

            self.fall_counter = 0

            self.cooldown_timer = self.COOLDOWN

            return True

        return False


    # =====================================================
    # OVERLAY
    # =====================================================

    def draw_overlay(
        self,
        frame,
        fire_dets,
        fall_confirmed,
        fall_prob,
        fps
    ):

        h, w = frame.shape[:2]

        overlay = frame.copy()

        # TOP BAR
        cv2.rectangle(
            overlay,
            (0, 0),
            (w, 40),
            (20, 20, 20),
            -1
        )

        cv2.putText(
            overlay,
            f"FPS: {fps:.1f}",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # FIRE
        for label, conf, x1, y1, x2, y2 in fire_dets:

            cv2.rectangle(
                overlay,
                (x1, y1),
                (x2, y2),
                (0, 0, 255),
                3
            )

            cv2.putText(
                overlay,
                f"{label} {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

        # ALERTS
        if fire_dets:

            cv2.rectangle(
                overlay,
                (0, 50),
                (w, 110),
                (0, 0, 180),
                -1
            )

            cv2.putText(
                overlay,
                "FIRE DETECTED!",
                (w // 2 - 150, 90),
                cv2.FONT_HERSHEY_DUPLEX,
                1.2,
                (255, 255, 255),
                3
            )

        if fall_confirmed:

            cv2.rectangle(
                overlay,
                (0, 120),
                (w, 180),
                (0, 150, 0),
                -1
            )

            cv2.putText(
                overlay,
                "FALL DETECTED!",
                (w // 2 - 150, 160),
                cv2.FONT_HERSHEY_DUPLEX,
                1.2,
                (255, 255, 255),
                3
            )

        # FALL BAR
        bar_w = int(w * fall_prob)

        cv2.rectangle(
            overlay,
            (0, h - 20),
            (bar_w, h),
            (0, 255, 0),
            -1
        )

        cv2.putText(
            overlay,
            f"Fall prob: {fall_prob:.2f}",
            (10, h - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        frame[:] = cv2.addWeighted(
            overlay,
            0.85,
            frame,
            0.15,
            0
        )

        return frame


    # =====================================================
    # PROCESS
    # =====================================================

    def process(self, frame):

        self.frame_count += 1

        # FIRE
        fire_dets = self.detect_fire(frame)

        # POSE
        kp, annotated = self.get_keypoints(frame)

        self.kp_buffer.append(kp)

        # FALL
        is_fall_raw, fall_prob = self.detect_fall()

        fall_confirmed = self.update_fall_state(
            is_fall_raw
        )

        return (
            annotated,
            fire_dets,
            fall_confirmed,
            fall_prob
        )


# =========================================================
# MAIN
# =========================================================

def main(args):

    # DEVICE
    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device

    print(f"DEVICE: {device}")

    # CHECK MODELS
    for path in [
        args.fire_model,
        args.lstm_model
    ]:

        if not Path(path).exists():

            print(f"MODEL NOT FOUND: {path}")

            sys.exit(1)

    # SOURCE
    source = (
        int(args.source)
        if args.source.isdigit()
        else args.source
    )

    cap = cv2.VideoCapture(source)

    if not cap.isOpened():

        print("Cannot open source")

        sys.exit(1)

    # PIPELINE
    pipeline = SafetyPipeline(
        fire_model_path=args.fire_model,
        lstm_model_path=args.lstm_model,
        device=device,
        seq_len=args.seq_len,
        conf_fire=args.conf_fire
    )

    # FPS
    t_prev = time.time()

    fps = 0.0

    print("RUNNING...")

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        # FPS
        t_now = time.time()

        fps = (
            0.9 * fps +
            0.1 * (
                1.0 / max(t_now - t_prev, 1e-6)
            )
        )

        t_prev = t_now

        # PROCESS
        (
            annotated,
            fire_dets,
            fall_confirmed,
            fall_prob
        ) = pipeline.process(frame)

        # OVERLAY
        annotated = pipeline.draw_overlay(
            annotated,
            fire_dets,
            fall_confirmed,
            fall_prob,
            fps
        )

        # =================================================
        # FIRE ALERT
        # =================================================

        if fire_dets:

            if (
                time.time() -
                pipeline.last_fire_alert
            ) > pipeline.ALERT_INTERVAL:

                print("FIRE DETECTED!")

                cv2.imwrite(
                    "fire_alert.jpg",
                    annotated
                )

                send_telegram_message(
                    "🔥 FIRE DETECTED!"
                )

                send_telegram_photo(
                    "fire_alert.jpg",
                    caption="🔥 FIRE DETECTED!"
                )

                pipeline.last_fire_alert = time.time()

        # =================================================
        # FALL ALERT
        # =================================================

        if fall_confirmed:

            if (
                time.time() -
                pipeline.last_fall_alert
            ) > pipeline.ALERT_INTERVAL:

                print("FALL DETECTED!")

                cv2.imwrite(
                    "fall_alert.jpg",
                    annotated
                )

                send_telegram_message(
                    "🚨 FALL DETECTED!"
                )

                send_telegram_photo(
                    "fall_alert.jpg",
                    caption="🚨 FALL DETECTED!"
                )

                pipeline.last_fall_alert = time.time()

        # SHOW
        cv2.imshow(
            "AI Safety Monitor",
            annotated
        )

        key = cv2.waitKey(1) & 0xFF

        # QUIT
        if key == ord("q"):
            break

        # SCREENSHOT
        elif key == ord("s"):

            ts = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            fn = f"screenshot_{ts}.jpg"

            cv2.imwrite(fn, annotated)

            print(f"Saved: {fn}")

    # CLEANUP
    cap.release()

    cv2.destroyAllWindows()


# =========================================================
# ARGS
# =========================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--source",
        default="0"
    )

    parser.add_argument(
        "--fire_model",
        default="fire_best.pt"
    )

    parser.add_argument(
        "--lstm_model",
        default="fall_lstm_best.pt"
    )

    parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cuda", "cpu"]
    )

    parser.add_argument(
        "--seq_len",
        type=int,
        default=30   # tăng từ 20 → 30 để khớp model mới
    )

    parser.add_argument(
        "--conf_fire",
        type=float,
        default=0.45
    )

    args = parser.parse_args()

    main(args)
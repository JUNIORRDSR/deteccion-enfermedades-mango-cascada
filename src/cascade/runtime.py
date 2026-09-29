"""Cascade M1 -> crops -> M2, copied from the legacy CLI with only outputs and timers changed.

Source (read-only legacy; never imported or run from here):
  legacy_corpus Mango-vision/src/inference/infer_cascade.py (SRC-009663, ART-041)
  legacy git commit e7e59d1bce74a7ae12674f5b6068068681e691ce, file clean at that commit
  (blob 4f4cbdf0a51a5b9c9611e2fae082e8aea053d649)
  SHA256 7d672aa40603f61e53afe752fc99779c885af8e1588a4ab6cbb68277bf6a957b
  COLORS_BY_CLASS from Mango-vision/src/utils/config.py (SRC-009669), same commit,
  SHA256 63bef8f337cf7c224e61cc5f420373092d0ddb325539521ab70ee68e4fd9c394

Copied: draw_box verbatim, the body of process_frame and the single-image branch of main.
Changed, only for outputs and timers:
- cv2.imread(path) is split into a file read and cv2.imdecode(IMREAD_COLOR), the same BGR
  decode, so reading and decoding are separate timed stages.
- process_frame is split into three timed stages: the full M1 call; crops + M2 calls; drawing.
  The source drew each box right after classifying it, so a later overlapping crop could
  contain the label drawn for an earlier box; here every crop comes from the undrawn frame.
- cv2.imwrite / cv2.imshow are replaced by cv2.imencode('.jpg') in memory: nothing is written.
- predict calls pass the frozen protocol explicitly: imgsz (M1 640, M2 224), device,
  half=False (FP32) and save=False. The source left the M1 imgsz to the checkpoint default.
- The Ultralytics .speed of every call is returned so it can be recorded as internal time.
Not copied: argparse, the webcam/video loop, draw_fps, the window, the src.utils.config import.

Scientific imports stay at module level as in the source; import this module only after
src.evaluation.provenance.verify_environment.

Channel order: the source passes OpenCV BGR arrays straight to YOLO.predict and does NOT
convert BGR to RGB. That is kept (Ultralytics' own file loader also reads BGR).
M2 runs on every M1 box above the M1 threshold whatever its class, as in the source.
"""

from pathlib import Path

import cv2
import numpy as np

CHANNEL_ORDER = 'BGR'  # recorded in every benchmark run

# BGR para OpenCV (no RGB). Copied from src/utils/config.py.
COLORS_BY_CLASS = {
    "Saludable": (0, 200, 0),
    "Antracnosis": (0, 0, 255),
    "Cancro_bacteriano": (0, 255, 255),
    "Costras": (0, 140, 255),
    "Podredumbre_Extremo_tallo": (200, 0, 200),
}


def draw_box(frame, xyxy, label: str, color: tuple[int, int, int]) -> None:
    x1, y1, x2, y2 = [int(v) for v in xyxy]
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)
    cv2.putText(frame, label, (x1 + 2, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)


def read_file(path: Path) -> bytes:
    return Path(path).read_bytes()


def decode(data: bytes):
    """Same result as cv2.imread: a BGR uint8 array."""
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError('image bytes could not be decoded')
    return frame


def detect(frame, detector, conf: float, imgsz: int, device: str):
    """The full M1 call."""
    return detector.predict(frame, conf=conf, imgsz=imgsz, device=device, half=False,
                            save=False, verbose=False)[0]


def classify_crops(frame, det_results, classifier, conf_cls: float, imgsz: int,
                   device: str) -> list[dict]:
    """Crops + M2 calls; labels as the source builds them, drawn later by annotate()."""
    boxes = det_results.boxes
    if boxes is None or len(boxes) == 0:
        return []
    items = []
    for i in range(len(boxes)):
        xyxy = boxes.xyxy[i].cpu().numpy()
        x1, y1, x2, y2 = [max(0, int(v)) for v in xyxy]
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            continue
        cls_result = classifier.predict(crop, imgsz=imgsz, device=device, half=False,
                                        save=False, verbose=False)[0]
        probs = cls_result.probs
        top1 = int(probs.top1)
        conf = float(probs.top1conf)
        cls_name = cls_result.names[top1]
        if conf < conf_cls:
            label_cls = f"Desconocido: {conf * 100:.0f}%"
            color = (128, 128, 128)
        else:
            label_cls = f"{cls_name}: {conf * 100:.0f}%"
            color = COLORS_BY_CLASS.get(cls_name, (255, 255, 255))
        items.append({'xyxy': (x1, y1, x2, y2), 'label': label_cls, 'color': color,
                      'speed': dict(cls_result.speed)})
    return items


def annotate(frame, items: list[dict]):
    for item in items:
        draw_box(frame, item['xyxy'], item['label'], item['color'])
    return frame


def encode(frame) -> bytes:
    ok, buffer = cv2.imencode('.jpg', frame)
    if not ok:
        raise ValueError('JPEG encoding failed')
    return buffer.tobytes()


def describe(det_results, items: list[dict]) -> dict:
    """Counts and Ultralytics internal times (ms), outside every wall timer.

    M2 internal times are summed over that pass's M2 calls, 0 when there were none.
    """
    internal = {f'm1.{key}': float(value) for key, value in det_results.speed.items()}
    for key in ('preprocess', 'inference', 'postprocess'):
        internal[f'm2.{key}'] = float(sum(item['speed'][key] for item in items))
    boxes = det_results.boxes
    return {'n_predicted_fruits': 0 if boxes is None else len(boxes),
            'n_m2_calls': len(items), 'internal_ms': internal}

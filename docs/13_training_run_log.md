# Training Run Log

Started on 2026-07-05.

## Why This File Exists

This project has several training pipelines. This log records what is being trained, why the command was chosen, how it was run, and what result it produced. The aim is to make progress auditable instead of mysterious.

## Run 1 - YOLO11n Obstacle Detector, Full GPU Training

### Purpose

The previous YOLO output looked wrong because it came from a one-epoch CPU smoke model with a forced confidence threshold of `0.001`. That proved the pipeline was wired, but it did not produce a useful detector.

This run is meant to move from "pipeline proof" to a real first obstacle detector for facade features.

### Dataset

Source:

- CMP Facade Database converted from XML annotations.

Training classes:

- `balcony`
- `blind`

Current converted counts:

- Train images: `516`
- Validation images: `90`
- Balcony boxes: `1872`
- Blind boxes: `4425`

### Hardware Check

WSL can see the GPU:

- GPU: NVIDIA GeForce RTX 3050 6GB Laptop GPU
- Torch CUDA: available

### Why Copy Data Into WSL

Ultralytics warned that the OneDrive-mounted `/mnt/c/...` dataset is slow for image training. To avoid training stalls and reduce compatibility issues, the dataset is copied to:

```text
/home/mohit/facade_uav_training/cmp_yolo_obstacles
```

The training output will be written locally first, then key results will be copied back into the project.

### Planned Command

```bash
~/.local/bin/yolo train \
  model=yolo11n.pt \
  data=/home/mohit/facade_uav_training/cmp_yolo_obstacles/data.yaml \
  epochs=50 \
  imgsz=640 \
  batch=8 \
  device=0 \
  workers=2 \
  patience=15 \
  project=/home/mohit/facade_uav_training/runs \
  name=yolo_obstacles_full \
  exist_ok=True \
  plots=True
```

### Expected Interpretation

This still will not be a final flight model. It is the first serious trained detector. It should be judged by validation mAP and visual overlays at normal confidence, not by whether it merely creates boxes.

### Result

Live notes:

- Dataset copy completed successfully.
- Local WSL dataset path: `/home/mohit/facade_uav_training/cmp_yolo_obstacles`
- Files in local dataset folder: `1216`
- Training launched on CUDA device `0`.
- Early epochs are stable with about `2.4 GB / 6 GB` GPU memory used.
- GPU temperature observed around `67 C`.
- By epoch `7`, validation mAP was still very low, so the detector is not useful yet. The run is being allowed to continue because there are no memory, corruption, or thermal problems.

Final outcome:

- Training stopped early at epoch `46`.
- Best epoch: `31`.
- Best validation summary after final validation:
  - Precision: `0.512`
  - Recall: `0.00719`
  - mAP50: `0.00285`
  - mAP50-95: `0.000607`
- Normal inference confidence `0.25` on `cmp_b0013.jpg`: `0` detections.
- Lower confidence `0.05` on `cmp_b0013.jpg`: `0` detections.

Artifacts copied into the project:

```text
models/yolo_obstacles_full/
models/yolo_obstacles_full/weights/best.pt
models/yolo_obstacles_full/weights/last.pt
models/yolo_obstacles_full/results.csv
models/yolo_obstacles_full/results.png
models/yolo_obstacles_full/val_batch0_labels.jpg
models/yolo_obstacles_full/val_batch0_pred.jpg
```

Interpretation:

This run was technically successful but scientifically poor. The dataset loads, training runs on GPU, losses decrease, and validation executes. However, the detector does not produce usable boxes at normal confidence. The validation batch images show that labels are present but predictions are nearly absent. This means the next step should be diagnostic training, not simply claiming the YOLO model works.

## Run 2 - YOLO Obstacle Diagnostic Overfit

### Purpose

Before spending more time on full training, test whether YOLO can overfit a tiny subset of the CMP obstacle labels. If it cannot overfit a small subset, then the issue is likely label format, class definition, or preprocessing. If it can overfit, then the full model likely needs better data balance, higher resolution, or different hyperparameters.

### Planned Method

Create a small local dataset using object-containing samples only, then train YOLO11n for a short focused run where train and validation point at the same tiny set. This is not a production model. It is a sanity check.

### Result

Completed.

Final outcome:

- Dataset size: `32` images with objects.
- Train and validation used the same images intentionally.
- Epochs: `100`.
- Final validation summary:
  - Precision: `0.114`
  - Recall: `0.138`
  - mAP50: `0.0574`
  - mAP50-95: `0.0188`
- Normal inference confidence `0.25` on one overfit image: `0` detections.
- Lower confidence `0.05` on one overfit image: `208` weak detections.

Artifacts copied into the project:

```text
models/yolo_obstacles_overfit32/
models/yolo_obstacles_overfit32/weights/best.pt
models/yolo_obstacles_overfit32/results.csv
models/yolo_obstacles_overfit32/results.png
models/yolo_obstacles_overfit32/val_batch0_pred.jpg
outputs/yolo_obstacles_overfit32_conf025/
outputs/yolo_obstacles_overfit32_conf005/
```

Interpretation:

This diagnostic did not pass. A detector should be able to strongly overfit 32 labeled images when train and validation are identical. Instead, it only learned weak low-confidence patterns. This means the current CMP `balcony`/`blind` bounding-box formulation is not enough for reliable obstacle avoidance.

## Decision After YOLO Runs

Stop blind YOLO training for now.

Why:

- Full GPU training produced a technically valid but poor model.
- Tiny-set overfit also remained poor.
- More epochs on the same labels are unlikely to fix the core issue.

What this means for the project:

- Do not use the current YOLO model for safety-critical obstacle avoidance.
- Keep YOLO artifacts because they prove the training pipeline and show the limitation.
- Use SegFormer/OpenCV clean-skip mapping as the trusted near-term perception route.

Next better training path:

1. Create obstacle masks from CMP labels and train segmentation-style obstacle detection.
2. Add real facade obstacle classes beyond CMP: AC units, pipes, ropes, ledges, maintenance platforms, open windows, people.
3. Try tiled/higher-resolution detection only after labels are reviewed and cleaned.
4. Fuse obstacle masks with the cleaning-zone grid instead of relying only on weak bounding boxes.

Visual evaluation board:

```text
outputs/progress_evaluation/yolo_training_evaluation_board.png
```

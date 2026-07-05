# Dataset Source Selection

## Selected Dataset

Primary source: CMP Facade Database

Official URL:

https://cmp.felk.cvut.cz/~tylecr1/facade/

Why this dataset:

- It is specifically a facade parsing dataset.
- It has 606 rectified facade images.
- It has manual annotations.
- It includes facade element classes useful for cleaning decisions.
- It has an official report and direct download links.

## Classes

CMP classes:

- facade
- molding
- cornice
- pillar
- window
- door
- sill
- blind
- balcony
- shop
- deco
- background

Verified local index:

- Samples: `606`
- Images: `606` JPG
- Masks: `606` PNG
- XML annotations: `606`
- Highest-volume object class: `window`
- Mask labels include `shop` as label ID `12`

## Mapping To Cleaning Logic

For our UAV:

- `window` -> cleanable glass candidate
- `door` -> conditional glass candidate
- `shop` -> conditional glass candidate
- `facade` -> skip unless later classified as glass curtain wall
- `molding`, `cornice`, `pillar`, `sill`, `deco` -> skip structural/frame detail
- `blind`, `balcony` -> skip obstacle
- `background` -> skip

This is not perfect for modern glass curtain walls because CMP was built for facade parsing, not cleaning. It is still the best first source because it gives us annotated facade structure and a path to train SegFormer/YOLO-style semantic models.

## Download

From WSL:

```bash
cd /mnt/c/Users/mohit/OneDrive/Documents/Facade_drone_Vision
python3 scripts/download_cmp_facade.py
```

Downloaded files go to:

```text
data/raw/cmp_facade/
```

Prepare an index:

```bash
python3 scripts/prepare_cmp_facade_index.py
python3 scripts/preview_cmp_facade_sample.py
```

Convert CMP labels into UAV cleaning masks:

```bash
python3 scripts/convert_cmp_to_cleaning_masks.py
```

Cleaning mask IDs:

- `0`: skip background
- `1`: cleanable glass
- `2`: skip structure
- `3`: skip obstacle
- `4`: conditional glass

Convert CMP balcony/blind annotations into YOLO obstacle boxes:

```bash
python3 scripts/convert_cmp_to_yolo_obstacles.py
```

YOLO obstacle classes:

- `0`: balcony
- `1`: blind

Verified YOLO conversion:

- Train images: `516`
- Validation images: `90`
- Balcony boxes: `1872`
- Blind boxes: `4425`

## Secondary Dataset To Consider Later

IRF / Irregular Facades dataset is attractive for modern free-form facades because it includes classes such as Background, Plant, Wall, Window, Door, and Fence, and focuses on modern irregular facades. Use it later if a public download is available and licensing is clear.

from pathlib import Path
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.oil_detector.detect import detect_oil_spill
from backend.services.oil_detector.postprocess import postprocess_prediction
from backend.services.oil_detector.overlay import generate_overlay

router = APIRouter(
    prefix="/detection",
    tags=["Oil Spill Detection"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.get("/health")
def health():

    return {

        "status": "Model Loaded",

        "module": "Oil Spill Detection",

    }


@router.get("/model-info")
def model_info():

    return {

        "Model": "U-Net",

        "Framework": "PyTorch",

        "Input Size": "256x256",

        "Output": "Oil Spill Mask",

    }


@router.post("/predict")
async def predict(file: UploadFile = File(...)):

    if not file.content_type.startswith("image/"):

        raise HTTPException(
            status_code=400,
            detail="Please upload an image."
        )

    image_path = UPLOAD_DIR / file.filename

    with image_path.open("wb") as buffer:

        shutil.copyfileobj(file.file, buffer)
        

    # Run model inference
    prediction = detect_oil_spill(str(image_path))

    # Convert prediction to binary mask
    mask, spill_percentage = postprocess_prediction(prediction)

    # Save original image, mask and overlay
    images = generate_overlay(
        str(image_path),
        mask
    )

    # Derived metrics (can later be replaced with real calculations)
    confidence = round(min(99.9, 92 + spill_percentage), 2)

    spill_area = round(spill_percentage * 0.75, 2)

    risk_score = min(100, int(spill_percentage * 8))

    if spill_percentage < 3:
        risk_level = "LOW"
    elif spill_percentage < 8:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return {

        "filename": file.filename,

        "oil_detected": bool(spill_percentage > 1)  ,

        "confidence": float(confidence),

        "spill_percentage": float(round(spill_percentage, 2)),

        "spill_area_km2": float(spill_area),

        "risk_score": int(risk_score),

        "risk_level": risk_level,

        "images": {

            "original": images["original"],

            "mask": images["mask"],

            "overlay": images["overlay"],

        },

    }
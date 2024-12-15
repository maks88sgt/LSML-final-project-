from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import os
import torch
from timm import create_model
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI(
    title="Image Similarity API",
    description="""
    API for getting simalar ECCO products based on following models: ResNet, EfficientNet и MobileNet.
    """,
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_DIR = "saved_models"
DATA_PATH = "./cleaned_data.csv"

try:
    product_data = pd.read_csv(DATA_PATH)
    product_data.set_index("objectID", inplace=True)
    print("Product data loaded successfully.")
except FileNotFoundError:
    raise RuntimeError(f"Data file {DATA_PATH} not found. Please ensure the file exists.")

def load_saved_model(model_name):
    model_path = os.path.join(MODEL_DIR, f"{model_name}_model.pth")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file {model_path} not found.")

    checkpoint = torch.load(model_path)

    model = create_model(model_name, pretrained=False, num_classes=0)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    object_ids = checkpoint["object_ids"]
    feature_matrix = checkpoint["feature_matrix"]

    return model, object_ids, feature_matrix

models = {}
for model_name in ["resnet50", "efficientnet_b0", "mobilenetv2_100"]:
    models[model_name] = load_saved_model(model_name)

def get_similar_items_by_image(feature_matrix, object_ids, input_object_id, top_n=5):
    try:
        input_object_id = int(input_object_id)
    except ValueError:
        raise ValueError(f"Invalid object ID format: {input_object_id}")

    if input_object_id not in object_ids:
        print(f"Requested object_id {input_object_id} not found in object_ids.")
        raise ValueError(f"Object ID {input_object_id} not found.")

    input_index = object_ids.index(input_object_id)

    similarity_matrix = cosine_similarity(feature_matrix)

    similar_items = list(enumerate(similarity_matrix[input_index]))
    similar_items = sorted(similar_items, key=lambda x: x[1], reverse=True)

    return [
        {
            "product": product_data.loc[object_ids[idx]].reset_index().iloc[0].to_dict(),
            "similarity": float(round(score, 3))
        }
        for idx, score in similar_items[1:top_n + 1]
    ]


class RecommendationRequest(BaseModel):
    object_id: str
    model_name: str = Query(
        "resnet50",
        description="Model to use (resnet50, efficientnet_b0, mobilenetv2_100)."
    )

@app.post(
    "/recommend",
    summary="Get list of similar products",
    description="Return list of similar products for provided objectID."
)
def recommend(data: RecommendationRequest):
    model_name = data.model_name
    input_object_id = data.object_id

    if model_name not in models:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found.")

    model, object_ids, feature_matrix = models[model_name]

    try:
        recommendations = get_similar_items_by_image(feature_matrix, object_ids, input_object_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
         base_product = product_data.loc[int(input_object_id)].reset_index().iloc[0].to_dict()
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Base product with ID {input_object_id} not found.")

    

    response = {
    "base_product": base_product,
    "recommendations": recommendations
}

# Приведение JSON-ответа к корректному формату
    response = jsonable_encoder(response)

# Проверка и замена некорректных значений
    def sanitize_json(data):
        if isinstance(data, dict):
            return {key: sanitize_json(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [sanitize_json(item) for item in data]
        elif isinstance(data, float) and not np.isfinite(data):  # NaN, Infinity
            return 0.0
        return data

    response = sanitize_json(response)
    return response

@app.get(
    "/products",
    summary="Get list of products",
    description="Return list of products."
)
def get_products(page: int = Query(1, ge=1, description="Page number"),
                 page_size: int = Query(10, ge=1, le=100, description="Products per page")):
    # Рассчёт индексов для текущей страницы
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    if start_idx >= len(product_data):
        raise HTTPException(status_code=404, detail="Page out of range.")

    products = product_data.iloc[start_idx:end_idx].reset_index().to_dict(orient="records")

    return {
        "page": page,
        "page_size": page_size,
        "total_products": len(product_data),
        "products": products
    }


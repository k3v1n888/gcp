# backend/routers/debug.py
from fastapi import APIRouter, Request
from sklearn.utils.validation import check_is_fitted

router = APIRouter()

@router.get("/api/debug/model_status")
def get_model_status(request: Request):
    predictor = request.app.state.predictor
    if not predictor or not predictor.model:
        return {"status": "Model not loaded."}

    model_details = {"model_type": str(type(predictor.model))}
    try:
        vectorizer = predictor.model.named_steps['tfidfvectorizer']
        check_is_fitted(vectorizer)
        model_details["vectorizer_status"] = "Fitted"
    except Exception as e:
        model_details["vectorizer_status"] = "NOT FITTED"
        model_details["error"] = str(e)

    return model_details

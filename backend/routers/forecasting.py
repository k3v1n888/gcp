from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/api/forecasting/24_hour")
def get_24_hour_forecast(request: Request):
    forecaster = request.app.state.forecaster
    prediction = forecaster.predict_next_24_hours()
    return prediction

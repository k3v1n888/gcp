from fastapi import APIRouter, Request
router = APIRouter()

@router.get("/api/graph/storyline/{threat_id}")
def get_storyline(request: Request, threat_id: int):
    graph_service = request.app.state.graph_service
    storyline = graph_service.get_attack_storyline(threat_id)
    return {"storyline": storyline}
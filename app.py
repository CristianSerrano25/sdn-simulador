from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import asyncio
import json
import threading
import time
from main import NetworkSimulator
from network import TrafficType

app = FastAPI(title="SDN Attack Simulator")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global simulation state
simulation_state = {
    "running": False,
    "progress": 0,
    "duration": 0,
    "stats": {
        "total_packets": 0,
        "blocked_hosts": 0,
        "active_hosts": 0,
        "attack_packets": 0,
        "normal_packets": 0,
        "attacks_detected": 0
    },
    "events": []
}

simulator = None
sim_thread = None

class SimulationRequest(BaseModel):
    duration: int = 10

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main HTML interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/simulate")
async def start_simulation(sim_request: SimulationRequest):
    """Start a new simulation"""
    global simulator, sim_thread, simulation_state
    
    if simulation_state["running"]:
        return {"status": "error", "message": "Simulation already running"}
    
    # Reset state
    simulation_state["running"] = True
    simulation_state["progress"] = 0
    simulation_state["duration"] = sim_request.duration
    simulation_state["stats"] = {
        "total_packets": 0,
        "blocked_hosts": 0,
        "active_hosts": 0,
        "attack_packets": 0,
        "normal_packets": 0,
        "attacks_detected": 0
    }
    simulation_state["events"] = []
    
    # Create new simulator
    simulator = NetworkSimulator()
    
    # Run simulation in background thread
    def run_sim():
        global simulation_state
        try:
            simulator.run_simulation(duration=sim_request.duration)
            simulation_state["running"] = False
            
            # Update final stats
            update_stats()
        except Exception as e:
            simulation_state["running"] = False
            simulation_state["events"].append({
                "timestamp": time.time(),
                "type": "error",
                "message": f"Error: {str(e)}"
            })
    
    sim_thread = threading.Thread(target=run_sim, daemon=True)
    sim_thread.start()
    
    return {
        "status": "success",
        "message": f"Simulation started for {sim_request.duration} seconds"
    }

@app.get("/api/status")
async def get_status():
    """Get current simulation status"""
    update_stats()
    return simulation_state

def update_stats():
    """Update statistics from the simulator"""
    global simulator, simulation_state
    
    if simulator is None:
        return
    
    controller = simulator.controller
    
    # Count traffic types
    attack_count = sum(1 for _, ttype in controller.traffic_history if ttype == TrafficType.ATTACK)
    normal_count = len(controller.traffic_history) - attack_count
    
    simulation_state["stats"] = {
        "total_packets": len(controller.traffic_history),
        "blocked_hosts": len(controller.blocked_hosts),
        "active_hosts": len(controller.hosts) - len(controller.blocked_hosts),
        "attack_packets": attack_count,
        "normal_packets": normal_count,
        "attacks_detected": len(controller.blocked_hosts)
    }

@app.get("/api/stream")
async def stream_updates(request: Request):
    """Server-Sent Events endpoint for real-time updates"""
    
    async def event_generator():
        global simulation_state
        
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                break
            
            # Update stats
            update_stats()
            
            # Send current state
            data = json.dumps(simulation_state)
            yield f"data: {data}\n\n"
            
            # Update every 500ms
            await asyncio.sleep(0.5)
            
            # Stop streaming if simulation is not running
            if not simulation_state["running"] and simulation_state["progress"] == 0:
                break
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

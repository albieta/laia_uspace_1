from fastapi import APIRouter
from backend.models import DronesTracking, Drone, FlightPlan
from backend.drone_tracking import verify_coordinates
from laiagenlib.Domain.Shared.Utils.logger import _logger
from laiagenlib.Domain.LaiaBaseModel.ModelRepository import ModelRepository
from laiagenlib.Application.LaiaBaseModel import ReadLaiaBaseModel, CreateLaiaBaseModel, DeleteLaiaBaseModel, SearchLaiaBaseModel, UpdateLaiaBaseModel

def ExtraRoutes(repository: ModelRepository=None):
    router = APIRouter(tags=["Extra Routes"])

    @router.get("/drone_tracking_alert/{droneTrackingId}", openapi_extra={'x-description': 'Given a Drone tracking object with basic telemetry data, it verifies that the coordinates of a given timestamp are correct, if not, it sets an alarm to the drone system.'})
    async def get_drone_tracking_alert_droneTrackingId(droneTrackingId: str):
        drone_tracking_data = await ReadLaiaBaseModel.read_laia_base_model(droneTrackingId, DronesTracking, ["admin"], repository)

        if not drone_tracking_data:
            raise HTTPException(status_code=404, detail="Drone tracking data not found")

        coordinates = drone_tracking_data["coordinates"]["geometry"]["coordinates"]
        timestamp = drone_tracking_data["timestamp"]
        flightplanId = drone_tracking_data["flightplanId"]
        droneId = drone_tracking_data["droneId"]

        flight_plan = await ReadLaiaBaseModel.read_laia_base_model(flightplanId, FlightPlan, ["admin"], repository)

        if not flight_plan:
            raise HTTPException(status_code=404, detail="Flight plan not found")

        is_correct = verify_coordinates(coordinates, timestamp, flight_plan)

        if not is_correct:
            alert_message = "ALERT - drone deviated from its flighplan route"
            severity = 10
        else:
            alert_message = "NO ALERTS"
            severity = 0
        await UpdateLaiaBaseModel.update_laia_base_model(droneId, {"alerts": {"alert_message":alert_message, "severity": severity, "drone_id": droneId}}, Drone, ["admin"], repository)

        return {"message": "Drone tracking alert checked successfully", "alert_message":alert_message, "severity": severity, "drone_id": droneId}

    @router.get("/drone_tracking_alert_from_drone/{droneId}", openapi_extra={'x-description': 'Given a Drone id, check the its last tracking data available with basic telemetry data, it verifies that the coordinates of a given timestamp are correct, if not, it sets an alarm to the drone system.'})
    async def get_drone_tracking_alert_from_drone_droneId(droneId: str):
        drone_tracking_data = await SearchLaiaBaseModel.search_laia_base_model(0, 1, {"droneId": droneId}, {"timestamp": -1}, DronesTracking, ["admin"], repository)
        
        if not drone_tracking_data:
            raise HTTPException(status_code=404, detail="No tracking data found for the drone")

        return await get_drone_tracking_alert_droneTrackingId(drone_tracking_data['items'][0]['id'])

    return router
                    
""" 
**************************************************************************
Instructions to develop new routes
**************************************************************************

- Import models from the models file with: 
from .models import modelName1, modelName2

- To operate with the crud operations on the models here are examples of the usage:
await CreateLaiaBaseModel.create_laia_base_model(dict(element), modelName1, user_roles, repository)
await UpdateLaiaBaseModel.update_laia_base_model(element_id, values, modelName1, user_roles, repository)
await ReadLaiaBaseModel.read_laia_base_model(element_id, modelName1, user_roles, repository)
await DeleteLaiaBaseModel.delete_laia_base_model(element_id, modelName1, user_roles, repository)
await SearchLaiaBaseModel.search_laia_base_model(skip, limit, filters, orders, modelName1, user_roles, repository)
"""

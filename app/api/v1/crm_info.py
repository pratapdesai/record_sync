from fastapi import APIRouter, HTTPException
from app.crms.registry import crm_registry

router = APIRouter()


@router.get("/available", tags=["CRM"])
async def list_available_crms():
    # crms = []
    # for name, cls in crm_registry.items():
    #     crms.append({
    #         "name": name,
    #         "schema": cls.config_schema()
    #     })
    # return {"supported_crms": crms}
    return {"supported_crms": list(crm_registry.keys())}


@router.get("/{crm_name}/schema", tags=["CRM"])
async def get_crm_schema(crm_name: str):
    crm_cls = crm_registry.get(crm_name.lower())
    if not crm_cls:
        raise HTTPException(status_code=404, detail=f"CRM '{crm_name}' not found")
    return {
        "crm": crm_name,
        "schema": crm_cls.config_schema()
    }

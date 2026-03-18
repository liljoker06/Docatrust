from fastapi import APIRouter

from controllers.generation import run_script

router = APIRouter(prefix="/generate", tags=["generation"])


@router.post("/devis")
def generate_devis():
    return run_script("generate_devis.py")


@router.post("/devis-erronees")
def generate_devis_erronees():
    return run_script("generate_devis_erronees.py")


@router.post("/factures")
def generate_factures():
    return run_script("generate_factures.py")


@router.post("/factures-erronees")
def generate_factures_erronees():
    return run_script("generate_factures_erronees.py")


@router.post("/rib")
def generate_rib():
    return run_script("generate_rib.py")


@router.post("/rib-erronees")
def generate_rib_erronees():
    return run_script("generate_rib_erronees.py")


@router.post("/siret")
def generate_siret():
    return run_script("generate_siret.py")


@router.post("/siret-erronees")
def generate_siret_erronees():
    return run_script("generate_siret_erronees.py")


@router.post("/urssaf")
def generate_urssaf():
    return run_script("generate_urssaf.py")


@router.post("/urssaf-erronees")
def generate_urssaf_erronees():
    return run_script("generate_urssaf_erronees.py")


@router.post("/kbis")
def generate_kbis():
    return run_script("generate_kbis.py")


@router.post("/kbis-erronees")
def generate_kbis_erronees():
    return run_script("generate_kbis_erronees.py")


@router.post("/scans")
def generate_scans():
    return run_script("generate_scans.py")


@router.post("/manifest")
def generate_manifest():
    return run_script("generate_manifest.py")

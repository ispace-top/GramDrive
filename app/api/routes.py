from fastapi import APIRouter

from .files import router as files_router
from .settings import router as settings_router
from .sse import router as sse_router
from .upload import router as upload_router
from .auth import router as auth_router
from .tags import router as tags_router
from .stats import router as stats_router
from .downloads import router as downloads_router
from .thumbnail import router as thumbnail_router

router = APIRouter()

router.include_router(upload_router)
router.include_router(files_router)
router.include_router(sse_router)
router.include_router(settings_router)
router.include_router(auth_router)
router.include_router(tags_router)
router.include_router(stats_router)
router.include_router(downloads_router)
router.include_router(thumbnail_router)

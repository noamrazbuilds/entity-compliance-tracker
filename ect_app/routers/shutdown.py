import logging
import os
import signal
import threading

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["system"])


def _delayed_shutdown(delay: float = 0.5) -> None:
    """Send SIGTERM to the process group after a short delay.

    The delay allows the HTTP response to be returned before the
    process begins shutting down. The startup script's trap handler
    catches the signal and cleans up all child processes.
    """
    import time

    time.sleep(delay)
    logger.info("Sending SIGTERM to process group %d", os.getpgrp())
    try:
        os.killpg(os.getpgrp(), signal.SIGTERM)
    except ProcessLookupError:
        pass
    except OSError:
        # Fallback: kill just this process
        os.kill(os.getpid(), signal.SIGTERM)


@router.post("/api/v1/shutdown")
def shutdown() -> dict[str, str]:
    """Initiate graceful shutdown of all services.

    Returns a response immediately, then sends SIGTERM to the process group
    after a short delay so the startup script's trap handler can clean up.
    """
    thread = threading.Thread(target=_delayed_shutdown, daemon=True)
    thread.start()
    logger.info("Shutdown requested — terminating in ~0.5s")
    return {"status": "shutting_down", "message": "Services are shutting down."}

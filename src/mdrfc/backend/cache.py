import logging
from datetime import datetime

from mdrfc.backend.document import RFCDocumentSummary


logger = logging.getLogger(__name__)


class MdrfcCache:
    """
    Cache manager for the MDRFC server.
    """

    def __init__(
        self
    ) -> None:
        return
    
    async def setup(
        self
    ) -> None:
        """
        Initialize and warm up the MDRFC cache.
        """
        logger.info("setting up cache...")

        await self._setup_rfcs()

        logger.info("cache setup complete")

    async def _setup_rfcs(
        self,
    ) -> None:
        """
        Populate the cache's `rfcs`.
        """
        logger.debug("populating `rfcs`...")

        rfcs: list[RFCDocumentSummary] = [
            RFCDocumentSummary(
                rfc_id=-1,
                author_id="kline",
                created_at=datetime.now(),
                summary="Hello, world!"
            )
        ]

        self.rfcs = rfcs
        logger.debug("done populating `rfcs`")

    async def get_rfcs(
        self,
    ) -> list[RFCDocumentSummary] | None:
        """
        Get the cache's list of RFCs, or None if it does not exist.
        """
        if self.rfcs:
            return self.rfcs
        
        return None
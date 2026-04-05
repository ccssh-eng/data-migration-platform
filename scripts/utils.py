import logging
import time


def retry(func, max_attempts=3, delay=5):
    logger = logging.getLogger()
    for attempt in range(1, max_attempts + 1):
        try:
            return func()
        except Exception as e:
            logger.error(f"Tentative {attempt} a échoué: {e}")
            if attempt < max_attempts:
                logger.info(f"Réessayer dans {delay}s...")
                time.sleep(delay)
            else:
                logger.critical(
                    "Les tentatives maximales ont été réalisées.Pipeline a échoué."
                )
                raise

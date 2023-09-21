import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import aiohttp
import asyncio
import json
import time
import requests

message_body = {
  "hours": 0,
  "minutes": 0,
  "seconds": 10,
  "url": "http://127.0.0.1/"
}


async def async_stress_test():
    logger.setLevel(logging.INFO)
    async with aiohttp.ClientSession() as session:
        url_requests = []
        for i in range(2):
            url_to_invoke = "http://localhost/timer/"
            url_requests.append(create_task(session,url_to_invoke))

        start_time = time.perf_counter()
        all_responses = await asyncio.gather(*url_requests)
        end_time = time.perf_counter() - start_time

    logger.error(f"Some request passed: {True in all_responses}")
    logger.error(f"Sending 1000 requests took {end_time} seconds")


async def create_task(session,url):
    try:
        async with session.post(url,json=message_body) as response:
            if response.status == 200:
                return True
            return False
    except Exception as err:
        logger.error(f"Error while Creating task: {err}")

def sync_stress_test():
# Sends 500 sync http requests to the system
    start_time = time.perf_counter()
    for i in range(500):
        response = requests.post("http://localhost/timer/",json=message_body)
        if response.status_code != 200:
            logger.error("Failed http")
    end_timer = time.perf_counter() - start_time
    logger.info(f"Finished processing in {end_timer} seconds")


if __name__ == "__main__":
## Async Stress Test
# asyncio.run(async_stress_test())

## Sync Stress Test




from redis import Redis
from rq import Queue

# Connect to Valkey/Redis running on localhost:6379
redis_connection = Redis(
    host="localhost",
    port=6379
)

# Create a Queue instance using the Redis connection
# This queue follows FIFO — first job in, first job out
queue = Queue(connection=redis_connection)



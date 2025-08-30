import os
from celery import Celery
from kombu import Queue

# Get Redis URL from environment variable, with a default for local development
REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')

# Define the task queues
task_queues = (
    Queue('default', routing_key='task.default'),
    Queue('shell', routing_key='task.shell'),
    Queue('git', routing_key='task.git'),
    Queue('llm', routing_key='task.llm'),
    Queue('qa', routing_key='task.qa'),
    Queue('tests', routing_key='task.tests'),
    Queue('repo', routing_key='task.repo'),
)

# Define the task routes. For now, all tasks are routed to the same function.
# This can be changed later to have specific functions for each task type.
task_routes = {
    'tasks.execute_command': {
        'queue': 'default'
    },
}

# Create the Celery app instance
celery_app = Celery(
    'tasks',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['tasks']
)

# Update celery configuration
celery_app.conf.update(
    task_queues=task_queues,
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='task.default',
)

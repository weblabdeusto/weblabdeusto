from celery import Celery

celery_app = Celery("celery_tasks", broker="redis://localhost:6379",
                    backend="redis://localhost:6379")
import celery


def create_worker_from(WorkerClass, celery_config='celery_tasks.celery_config'):

    assert issubclass(WorkerClass, celery.Task)
    app = celery.Celery()
    app.config_from_object(celery_config)
    app.conf.update(task_default_queue=WorkerClass.name)  # update worker queue
    worker_task = app.register_task(WorkerClass())

    return app, worker_task

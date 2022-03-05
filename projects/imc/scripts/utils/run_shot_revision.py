from restapi.connectors import celery

obj = celery.get_instance()


# parameters as in projects/imc/backend/apis/videos.py:1028
item_id = "3605621f-44ea-47ea-b134-b3d2170c4849"  # item uuid
shots = "......"
reviser = (
    "6037b2bb-28a3-411c-a9bc-a59d1a226668"  # uuid of the user who submitted the request
)
revision = {"shots": shots, "exitRevision": True, "reviser": reviser}
args = [revision, item_id]
task_id = obj.celery_app.send_task("shot_revision", args=args, countdown=10)
print("Task submitted: %s" % task_id)

from imc.tasks.imc_tasks import shot_revision
from restapi.connectors import get_debug_instance
from restapi.connectors.celery import CeleryExt

obj = get_debug_instance(CeleryExt)


# parameters as in projects/imc/backend/apis/videos.py:1028
item_id = "3605621f-44ea-47ea-b134-b3d2170c4849"  # item uuid
shots = "......"
reviser = (
    "6037b2bb-28a3-411c-a9bc-a59d1a226668"  # uuid of the user who submitted the request
)
revision = {"shots": shots, "exitRevision": True, "reviser": reviser}
args = [revision, item_id]
task_id = shot_revision.apply_async(args=args, countdown=10)
print("Task submitted: %s" % task_id)

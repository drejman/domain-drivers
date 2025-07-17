from schedule.allocation.capability_scheduling import AllocatableResourceId
from schedule.resource import DeviceId, EmployeeId

ResourceId = DeviceId | EmployeeId


def to_allocatable_resource_id(resource_id: ResourceId) -> AllocatableResourceId:
    return AllocatableResourceId(resource_id.id)

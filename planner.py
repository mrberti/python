#%%
import asyncio
import json
from datetime import datetime
from typing import Optional, List, Sequence

import httpx
from pydantic import BaseModel, Field, ConfigDict
import pandas as pd

base_url = "https://graph.microsoft.com"
token = "YOUR-ACCESS-TOKEN"

class PlannerPlan(BaseModel):
    etag: str = Field(alias="@odata.etag")
    id: str
    title: str

class Group(BaseModel):
    id: str
    displayName: str
    description: str

class User(BaseModel):
    id: str
    displayName: Optional[str]

class Task(BaseModel):
    model_config = ConfigDict(
        json_encoders={
            datetime: (lambda x: x.astimezone().isoformat())
        }
    )

    etag: Optional[str] = Field(None, alias="@odata.etag")
    id: Optional[str] = None
    planId: Optional[str] = None
    title: Optional[str] = None
    bucketId: Optional[str] = None

    activeChecklistItemCount: Optional[int] = None
    appliedCategories: Optional[dict] = None
    assigneePriority: Optional[str] = None
    assignments: Optional[dict] = None
    checklistItemCount: Optional[int] = None
    completedBy: Optional[dict] = None
    completedDateTime: Optional[datetime] = None
    conversationThreadId: Optional[str] = None
    createdBy: Optional[dict] = None
    createdDateTime: Optional[datetime] = None
    dueDateTime: Optional[datetime] = None
    hasDescription: Optional[bool] = None
    orderHint: Optional[str] = None
    percentComplete: Optional[int] = None
    previewType: Optional[str] = None
    priority: Optional[int] = None
    referenceCount: Optional[int] = None
    startDateTime: Optional[datetime] = None

    @classmethod
    def read_only_fields(cls):
        return {
            "activeChecklistItemCount",
            "assigneePriority",
            "assignments",
            "checklistItemCount",
            "completedBy",
            "completedDateTime",
            "createdBy",
            "createdDateTime",
            "hasDescription",
            "orderHint",
            "previewType",
            "referenceCount",
        }

class Planner:
    def __init__(self, plan_id: str) -> None:
        self.plan_id = plan_id
        self.headers = {
            "Authorization": f"Bearer {token}",
        }
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers=self.headers,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        await self.client.aclose()

    async def get_plan(self) -> PlannerPlan:
        endpoint = f"/v1.0/planner/plans/{self.plan_id}"
        resp = await self.client.get(endpoint)
        data = resp.json()
        print(data)
        model = PlannerPlan.model_validate(data)
        return model

    async def get_groups(self) -> List[Group]:
        endpoint = f"/v1.0/groups"
        select = Group.model_fields.keys()
        params = {"$select": ",".join(select)}
        resp = await self.client.get(endpoint, params=params)
        data = resp.json()
        self.groups = [Group.model_validate(x) for x in data["value"]]
        return self.groups

    async def get_members(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None
    ) -> List[User]:
        if id is None and name is None:
            raise Exception("Either id or name must be given")
        if id is None:
            id = str(name)
        endpoint = f"/v1.0/groups/{id}/members"
        endpoint = f"/v1.0/users"
        # select = Group.model_fields.keys()
        # params = {"$select": ",".join(select)}
        resp = await self.client.get(endpoint)
        data = resp.json()
        users = [User.model_validate(x) for x in data["value"]]
        return users

    async def get_task(self, task_id: str) -> Task:
        endpoint = f"/v1.0/planner/tasks/{task_id}"
        resp = await self.client.get(endpoint)
        data: dict = resp.json()
        task = Task.model_validate(data)
        return task

    async def get_tasks(self) -> List[Task]:
        endpoint = f"/v1.0/planner/plans/{self.plan_id}/tasks"
        resp = await self.client.get(endpoint)
        resp.raise_for_status()
        data: dict = resp.json()["value"]
        tasks = [Task.model_validate(x) for x in data]
        return tasks

    async def get_task_details(self, task_id: str) -> Optional[str]:
        endpoint = f"/v1.0/planner/tasks/{task_id}/details"
        resp = await self.client.get(endpoint)
        data = resp.json()
        return data

    async def get_tasks_details(self, tasks: Sequence[Task]) -> List[dict]:
        futures = [self.get_task_details(x.id) for x in tasks]
        data = await asyncio.gather(*futures)
        return data

    async def get_buckets(self) -> List[dict]:
        endpoint = f"/v1.0/planner/plans/{self.plan_id}/buckets"
        resp = await self.client.get(endpoint)
        data = resp.json()["value"]
        return data

    async def update_task(self, task: Task) -> None:
        task_id = task.id
        etag = task.etag
        if not task_id or not etag:
            raise ValueError("id and etag must be set")
        endpoint = f"/v1.0/planner/tasks/{task_id}"
        payload = json.loads(task.model_dump_json(
            exclude=Task.read_only_fields(),
            exclude_unset=True
        ))
        headers = {
            "If-Match": task.etag,
        }
        resp = await self.client.patch(
            endpoint,
            json=payload,
            headers=headers
        )
        if not resp.is_success:
            print(resp.json()["error"]["message"])
        resp.raise_for_status()

    async def create_task(self, task: Task):
        endpoint = "/v1.0/planner/tasks"
        if not task.planId:
            task.planId = self.plan_id
        payload = task.model_dump(exclude_defaults=True, exclude_unset=True)
        resp = await self.client.post(
            endpoint,
            json=payload,
        )
        data = resp.json()
        return Task.model_validate(data)

async def get_tasks(plan_id: str):
    async with Planner(plan_id=plan_id) as planner:
        # print(await planner.get_plan())
        coros = [
            planner.get_plan(),
            planner.get_tasks(),
            planner.get_buckets()
        ]
        results = await asyncio.gather(*coros)
        plan = results[0]
        tasks = results[1]
        buckets = results[2]
        details = await planner.get_tasks_details(tasks)
    df_tasks = pd.DataFrame([x.model_dump() for x in tasks])
    df_tasks.insert(0, "planId", plan.id)
    df_tasks.insert(1, "planTitle", plan.title)
    df_details = pd.DataFrame(details)
    df_buckets = pd.DataFrame(buckets)
    df_buckets = df_buckets.rename(columns={"id": "bucketId", "name": "bucketName"})
    df_tasks = df_tasks.merge(df_details[["id", "description"]], on="id", how="left")
    df_tasks = df_tasks.merge(df_buckets[["bucketId", "bucketName"]], on="bucketId", how="left")
    df_tasks = df_tasks.set_index("id")
    print(df_tasks)
    print(plan)
    return df_tasks

async def main():
    plan_ids = [
        "mRqiHYxJVE-afU9PwFT-_5gAFDWE",
        "p4KjA-IqYkeqHLR6y6lOsJgABh-g"
    ]
    coros = [get_tasks(x) for x in plan_ids]
    results = await asyncio.gather(*coros)
    df_tasks = pd.concat(results)
    return df_tasks

async def main2():
    async with Planner(plan_id="mRqiHYxJVE-afU9PwFT-_5gAFDWE") as planner:
        tasks = await planner.get_tasks()
        for task in tasks:
            print(task)
        update_task = Task.model_copy(tasks[0])
        update_task.title = "asd"
        update_task.priority = 1
        update_task.percentComplete = 0
        update_task.dueDateTime = datetime(2023, 10, 10, 10, 12)

        await planner.update_task(update_task)
        x = await planner.get_task(task_id=update_task.id)
        print(x)
        # new_task = Task(title="My New Task")
        # x = await planner.create_task(task=new_task)
        # print(x)

#%%
asyncio.run(main2())

from typing import Any, List
from asyncio import coroutine, gather


class ParallelTaskProcessorService:
    def __init__(self, parallel_tasks_enabled: bool = False, max_parallel_tasks: int = 10, return_exceptions: bool = True) -> None:
        self.parallel_tasks_enabled = parallel_tasks_enabled
        self.max_parallel_tasks = max_parallel_tasks
        self.return_exceptions = return_exceptions
        self.parallel_tasks = []
    
    
    async def process_available_tasks(self) -> List[Any]:
        if len(self.parallel_tasks) > 0:
            results = await gather(*self.parallel_tasks, return_exceptions=self.return_exceptions)
            self.parallel_tasks = []
            return results
    
    
    async def process_task(self, task: coroutine) -> List[Any] | None:
        if self.parallel_tasks_enabled:
            self.parallel_tasks.append(task)
            if len(self.parallel_tasks) >= self.max_parallel_tasks:
                results = []
                try:
                    results = await gather(*self.parallel_tasks, return_exceptions=self.return_exceptions)
                    self.parallel_tasks = []
                    return results
                except Exception as e:
                    self.parallel_tasks = []
                    raise e
        else:
            result = await task
            return result
    
    
    process_pending_tasks = process_available_tasks
            
        
    
    
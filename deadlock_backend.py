class DeadlockBackend:
    def __init__(self):
        self.process_names = []
        self.resource_names = []
        self.process_count = 0
        self.resource_count = 0
        self.allocation = []
        self.max_need = []
        self.available = []
        self.terminated = []

    def setup(self, process_names, resource_names, allocation, max_need, available):
        self.process_names = process_names
        self.resource_names = resource_names
        self.process_count = len(process_names)
        self.resource_count = len(resource_names)
        self.allocation = [row[:] for row in allocation]
        self.max_need = [row[:] for row in max_need]
        self.available = available[:]
        self.terminated = [False] * self.process_count

    def get_need(self):
        return [[self.max_need[i][j] - self.allocation[i][j] for j in range(self.resource_count)] for i in range(self.process_count)]

    def detect_deadlock(self):
        n, m = self.process_count, self.resource_count
        allocation = self.allocation
        max_need = self.max_need
        available = self.available
        need = self.get_need()
        work = available[:]
        finish = [self.terminated[i] or all(allocation[i][j] == 0 and need[i][j] == 0 for j in range(m)) for i in range(n)]
        safe_seq = []
        while True:
            did_allocate = False
            for i in range(n):
                if not finish[i] and all(need[i][j] <= work[j] for j in range(m)):
                    for j in range(m):
                        work[j] += allocation[i][j]
                    finish[i] = True
                    safe_seq.append(i)
                    did_allocate = True
            if not did_allocate:
                break
        deadlocked = [i for i, done in enumerate(finish) if not done]
        return (deadlocked if deadlocked else None), safe_seq

    def kill_process(self, pname):
        idx = self.process_names.index(pname)
        for j in range(self.resource_count):
            self.available[j] += self.allocation[idx][j]
            self.allocation[idx][j] = 0
            self.max_need[idx][j] = 0
        self.terminated[idx] = True
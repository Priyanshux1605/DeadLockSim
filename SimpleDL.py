class DeadlockDetector:
    def __init__(self, num_processes, num_resources, available, allocation, request):
        self.num_processes = num_processes
        self.num_resources = num_resources
        self.available = list(available)
        self.allocation = [list(row) for row in allocation]
        self.request = [list(row) for row in request]

    def is_safe(self, temp_available, temp_allocation, temp_request, temp_finish):
        n = self.num_processes
        m = self.num_resources
        work = list(temp_available)

        while True:
            found = False
            for i in range(n):
                if not temp_finish[i]:
                    can_grant = True
                    for j in range(m):
                        if temp_request[i][j] > work[j]:
                            can_grant = False
                            break
                    if can_grant:
                        for j in range(m):
                            work[j] += temp_allocation[i][j]
                        temp_finish[i] = True
                        found = True
            if not found:
                break
        return all(temp_finish)

    def detect_deadlock(self):
        n = self.num_processes
        m = self.num_resources
        finish = [False] * n
        temp_available = list(self.available)
        temp_allocation = [list(row) for row in self.allocation]
        temp_request = [list(row) for row in self.request]

        safe_sequence = []

        while True:
            found_safe_process = False
            for i in range(n):
                if not finish[i]:
                    can_grant = True
                    for j in range(m):
                        if temp_request[i][j] > temp_available[j]:
                            can_grant = False
                            break
                    if can_grant:
                        for j in range(m):
                            temp_available[j] += temp_allocation[i][j]
                        safe_sequence.append(i)
                        finish[i] = True
                        temp_allocation[i] = [0] * m  # Mark as "finished"
                        temp_request[i] = [0] * m     # Mark as "finished"
                        found_safe_process = True

            if not found_safe_process:
                break

        deadlocked_processes = [i for i, finished in enumerate(finish) if not finished]
        return deadlocked_processes, safe_sequence

    def can_grant_request(self, process_id, request):
        for i in range(self.num_resources):
            if request[i] > self.available[i]:
                return False
        return True

    def grant_request(self, process_id, request):
        for i in range(self.num_resources):
            self.available[i] -= request[i]
            self.allocation[process_id][i] += request[i]
            self.request[process_id][i] -= request[i]

    def release_resources(self, process_id, release):
        for i in range(self.num_resources):
            self.available[i] += release[i]
            self.allocation[process_id][i] -= release[i]

    def terminate_process(self, process_id):
        released_resources = self.allocation[process_id]
        self.release_resources(process_id, released_resources)
        self.allocation[process_id] = [0] * self.num_resources
        self.request[process_id] = [0] * self.num_resources

    def get_system_state(self):
        return {
            "available": list(self.available),
            "allocation": [list(row) for row in self.allocation],
            "request": [list(row) for row in self.request],
        }

if __name__ == '__main__':
    # Example Usage
    num_processes = 3
    num_resources = 3
    available = [3, 3, 2]
    allocation = [[0, 1, 0], [2, 0, 0], [3, 0, 2]]
    request = [[7, 5, 3], [0, 2, 0], [0, 0, 2]]

    detector = DeadlockDetector(num_processes, num_resources, available, allocation, request)
    deadlocked, safe_sequence = detector.detect_deadlock()

    print("Initial System State:")
    print("Available:", detector.available)
    print("Allocation:", detector.allocation)
    print("Request:", detector.request)

    if deadlocked:
        print("Deadlocked Processes:", deadlocked)
    else:
        print("No deadlock detected. Safe sequence:", safe_sequence)

import networkx as nx
import matplotlib.pyplot as plt

class DeadlockBackend:
    def __init__(self):
        # Your original __init__ method
        self.process_names = []
        self.resource_names = []
        self.process_count = 0
        self.resource_count = 0
        self.allocation = []
        self.max_need = []
        self.available = []
        self.terminated = []
        # Added to store deadlock detection results for the graph
        self.deadlocked_indices = []

    def setup(self, process_names, resource_names, allocation, max_need, available):
        # Your original setup method
        self.process_names = process_names
        self.resource_names = resource_names
        self.process_count = len(process_names)
        self.resource_count = len(resource_names)
        self.allocation = [row[:] for row in allocation]
        self.max_need = [row[:] for row in max_need]
        self.available = available[:]
        self.terminated = [False] * self.process_count
        self.deadlocked_indices = []

    def get_need(self):
        # Your original get_need method
        return [[self.max_need[i][j] - self.allocation[i][j] for j in range(self.resource_count)] for i in range(self.process_count)]

    def detect_deadlock(self):
        # Your original detect_deadlock method
        n, m = self.process_count, self.resource_count
        allocation = self.allocation
        need = self.get_need()
        work = self.available[:]
        finish = [self.terminated[i] for i in range(n)]
        
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
        self.deadlocked_indices = deadlocked # Store result for graphing
        return (deadlocked if deadlocked else None), safe_seq

    def kill_process(self, pname):
        # Your original kill_process method
        idx = self.process_names.index(pname)
        for j in range(self.resource_count):
            self.available[j] += self.allocation[idx][j]
            self.allocation[idx][j] = 0
            self.max_need[idx][j] = 0
        self.terminated[idx] = True

    # --- NEW APPENDED METHODS ---

    def auto_recover(self):
        """
        NEW: Automatically recovers from deadlock by killing a process.
        Heuristic: Kills the deadlocked process holding the most total resources.
        """
        if not self.deadlocked_indices:
            return None # No deadlock to recover from

        # Calculate total resources held by each deadlocked process
        resources_held = {}
        for p_idx in self.deadlocked_indices:
            total_res = sum(self.allocation[p_idx])
            resources_held[p_idx] = total_res
        
        # Find the process index holding the most resources
        if not resources_held: # Should not happen unless all hold 0
            idx_to_kill = self.deadlocked_indices[0]
        else:
            idx_to_kill = max(resources_held, key=resources_held.get)

        process_to_kill_name = self.process_names[idx_to_kill]
        self.kill_process(process_to_kill_name)
        return process_to_kill_name

    def generate_rag_image(self, filename="rag_graph.png"):
        """
        NEW: Generates and saves a Resource Allocation Graph image.
        """
        g = nx.DiGraph()
        need = self.get_need()

        # Add nodes
        for i, name in enumerate(self.process_names):
            if self.terminated[i]: continue
            is_deadlocked = i in self.deadlocked_indices
            g.add_node(name, type='process', color='red' if is_deadlocked else 'skyblue')
        for name in self.resource_names:
            g.add_node(name, type='resource', color='lightgreen')

        # Add edges based on Allocation (R -> P) and Request (P -> R)
        for p_idx, p_name in enumerate(self.process_names):
            if self.terminated[p_idx]: continue
            for r_idx, r_name in enumerate(self.resource_names):
                # Allocation edge
                if self.allocation[p_idx][r_idx] > 0:
                    g.add_edge(r_name, p_name)
                # Request edge
                if need[p_idx][r_idx] > 0:
                    g.add_edge(p_name, r_name)

        # Styling and Drawing
        pos = nx.spring_layout(g, seed=42, k=0.9)
        plt.figure(figsize=(10, 8))
        
        process_nodes = [n for n, d in g.nodes(data=True) if d['type'] == 'process']
        resource_nodes = [n for n, d in g.nodes(data=True) if d['type'] == 'resource']
        process_colors = [d['color'] for n, d in g.nodes(data=True) if d['type'] == 'process']
        
        nx.draw_networkx_nodes(g, pos, nodelist=process_nodes, node_shape='o', node_size=2500, node_color=process_colors)
        nx.draw_networkx_nodes(g, pos, nodelist=resource_nodes, node_shape='s', node_size=2500, node_color='lightgreen')
        
        nx.draw_networkx_labels(g, pos, font_size=10, font_weight='bold')
        nx.draw_networkx_edges(g, pos, arrows=True, arrowstyle='->', arrowsize=20, edge_color='gray')
        
        plt.title("Resource Allocation Graph (RAG)", fontsize=16)
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.1)
        plt.close()
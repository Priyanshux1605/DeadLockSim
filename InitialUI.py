import tkinter as tk
from tkinter import messagebox, ttk
from deadlock_backend import DeadlockBackend

class DeadlockSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dead by Deadlock: Simulator")
        self.backend = DeadlockBackend()
        self.init_gui()

    def init_gui(self):
        self.clear_frame()
        tk.Label(self.root, text="Deadlock Simulator", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(self.root, text="Enter number of processes:").pack()
        self.process_entry = tk.Entry(self.root)
        self.process_entry.pack()
        tk.Label(self.root, text="Enter number of resource types:").pack()
        self.resource_entry = tk.Entry(self.root)
        self.resource_entry.pack()
        tk.Button(self.root, text="Next", command=self.get_names).pack(pady=10)

    def get_names(self):
        try:
            process_count = int(self.process_entry.get())
            resource_count = int(self.resource_entry.get())
            assert process_count > 0 and resource_count > 0
        except:
            messagebox.showerror("Error", "Please enter valid positive integers.")
            return
        self.process_count = process_count
        self.resource_count = resource_count
        self.clear_frame()

        tk.Label(self.root, text="Enter process names:").pack()
        self.process_name_entries = []
        for i in range(process_count):
            e = tk.Entry(self.root)
            e.pack()
            e.insert(0, f"P{i}")
            self.process_name_entries.append(e)
        tk.Label(self.root, text="Enter resource names:").pack()
        self.resource_name_entries = []
        for i in range(resource_count):
            e = tk.Entry(self.root)
            e.pack()
            e.insert(0, f"R{i}")
            self.resource_name_entries.append(e)
        tk.Button(self.root, text="Next", command=self.get_matrices).pack(pady=10)

    def get_matrices(self):
        process_names = [e.get() for e in self.process_name_entries]
        resource_names = [e.get() for e in self.resource_name_entries]
        self.process_names = process_names
        self.resource_names = resource_names
        self.clear_frame()
        tk.Label(self.root, text="Enter Allocation Matrix: (resources allocated to each process)").pack()
        self.allocation_entries = []
        self.allocation_frame = tk.Frame(self.root)
        self.allocation_frame.pack()
        for i in range(self.process_count):
            row = []
            for j in range(self.resource_count):
                e = tk.Entry(self.allocation_frame, width=3)
                e.grid(row=i, column=j)
                e.insert(0, "0")
                row.append(e)
            self.allocation_entries.append(row)
        tk.Label(self.root, text="Enter Max Matrix: (max resources needed by each process)").pack()
        self.max_entries = []
        self.max_frame = tk.Frame(self.root)
        self.max_frame.pack()
        for i in range(self.process_count):
            row = []
            for j in range(self.resource_count):
                e = tk.Entry(self.max_frame, width=3)
                e.grid(row=i, column=j)
                e.insert(0, "0")
                row.append(e)
            self.max_entries.append(row)
        tk.Label(self.root, text="Enter Available Vector: (resources available)").pack()
        self.available_entries = []
        self.available_frame = tk.Frame(self.root)
        self.available_frame.pack()
        for j in range(self.resource_count):
            e = tk.Entry(self.available_frame, width=3)
            e.grid(row=0, column=j)
            e.insert(0, "0")
            self.available_entries.append(e)
        tk.Button(self.root, text="Start Simulation", command=self.simulation_gui).pack(pady=10)

    def simulation_gui(self):
        try:
            allocation = [[int(self.allocation_entries[i][j].get()) for j in range(self.resource_count)] for i in range(self.process_count)]
            max_need = [[int(self.max_entries[i][j].get()) for j in range(self.resource_count)] for i in range(self.process_count)]
            available = [int(self.available_entries[j].get()) for j in range(self.resource_count)]
        except:
            messagebox.showerror("Error", "Please enter valid integer values in matrices.")
            return
        self.backend.setup(self.process_names, self.resource_names, allocation, max_need, available)
        self.refresh_simulation()

    def refresh_simulation(self):
        self.clear_frame()
        tk.Label(self.root, text="Deadlock Simulation", font=("Arial", 14, "bold")).pack(pady=10)

        # Show Matrices
        self.display_matrix("Allocation Matrix", self.backend.allocation)
        self.display_matrix("Max Matrix", self.backend.max_need)
        need = self.backend.get_need()
        self.display_matrix("Need Matrix", need)
        self.display_vector("Available Vector", self.backend.available)

        # Deadlock detection
        deadlocked, safe_seq = self.backend.detect_deadlock()
        if not deadlocked:
            tk.Label(self.root, text="System is in SAFE STATE!", fg="green", font=("Arial", 12, "bold")).pack()
            tk.Label(self.root, text="Safe Sequence: " + " -> ".join([self.backend.process_names[i] for i in safe_seq])).pack()
        else:
            tk.Label(self.root, text="System is in DEADLOCK!", fg="red", font=("Arial", 12, "bold")).pack()
            dead_proc = [self.backend.process_names[i] for i in deadlocked]
            tk.Label(self.root, text="Deadlocked Processes: " + ", ".join(dead_proc)).pack()

            # Recovery options
            tk.Label(self.root, text="Recovery Options:").pack(pady=3)
            kill_frame = tk.Frame(self.root)
            kill_frame.pack()
            tk.Label(kill_frame, text="Kill Process:").pack(side=tk.LEFT)
            kill_var = tk.StringVar(value=dead_proc[0] if dead_proc else "")
            kill_menu = ttk.Combobox(kill_frame, textvariable=kill_var, values=dead_proc, state="readonly")
            kill_menu.pack(side=tk.LEFT)
            tk.Button(kill_frame, text="Kill", command=lambda: self.kill_process(kill_var.get())).pack(side=tk.LEFT, padx=5)

        tk.Button(self.root, text="Restart Input", command=self.init_gui).pack(pady=8)
        tk.Button(self.root, text="Exit", command=self.root.destroy).pack()

    def display_matrix(self, name, matrix):
        frame = tk.Frame(self.root)
        frame.pack()
        tk.Label(frame, text=name, font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=self.resource_count+1)
        header = tk.Label(frame, text="", width=8)
        header.grid(row=1, column=0)
        for j in range(self.resource_count):
            tk.Label(frame, text=self.resource_names[j], width=4, borderwidth=1, relief="solid").grid(row=1, column=j+1)
        for i in range(self.process_count):
            tk.Label(frame, text=self.process_names[i], width=8, borderwidth=1, relief="solid").grid(row=i+2, column=0)
            for j in range(self.resource_count):
                bg = "#f0f0f0" if self.backend.terminated[i] else "white"
                tk.Label(frame, text=str(matrix[i][j]), width=4, borderwidth=1, relief="solid", bg=bg).grid(row=i+2, column=j+1)

    def display_vector(self, name, vector):
        frame = tk.Frame(self.root)
        frame.pack()
        tk.Label(frame, text=name, font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=self.resource_count)
        for j in range(self.resource_count):
            tk.Label(frame, text=self.resource_names[j], width=8, borderwidth=1, relief="solid").grid(row=1, column=j)
        for j in range(self.resource_count):
            tk.Label(frame, text=str(vector[j]), width=8, borderwidth=1, relief="solid").grid(row=2, column=j)

    def kill_process(self, pname):
        self.backend.kill_process(pname)
        messagebox.showinfo("Killed", f"Process {pname} killed and resources released!")
        self.refresh_simulation()

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = DeadlockSimulatorGUI(root)
    root.mainloop()
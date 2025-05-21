import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
from deadlock_backend import DeadlockBackend

class DeadlockSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadlock Simulator")
        self.root.geometry("1000x600")
        ctk.set_appearance_mode("dark")
        self.backend = DeadlockBackend()
        self.init_gui()

    def init_gui(self):
        self.clear_frame()
        ctk.CTkLabel(self.root, text="Deadlock Simulator", font=("Arial", 24, "bold")).pack(pady=20)
        ctk.CTkLabel(self.root, text="Enter number of processes:").pack()
        self.process_entry = ctk.CTkEntry(self.root)
        self.process_entry.pack()
        ctk.CTkLabel(self.root, text="Enter number of resource types:").pack()
        self.resource_entry = ctk.CTkEntry(self.root)
        self.resource_entry.pack()
        ctk.CTkButton(self.root, text="Next", command=self.get_names).pack(pady=10)

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

        ctk.CTkLabel(self.root, text="Enter process names:").pack()
        self.process_name_entries = []
        for i in range(process_count):
            e = ctk.CTkEntry(self.root)
            e.pack()
            e.insert(0, f"P{i}")
            self.process_name_entries.append(e)

        ctk.CTkLabel(self.root, text="Enter resource names:").pack()
        self.resource_name_entries = []
        for i in range(resource_count):
            e = ctk.CTkEntry(self.root)
            e.pack()
            e.insert(0, f"R{i}")
            self.resource_name_entries.append(e)

        ctk.CTkButton(self.root, text="Next", command=self.get_matrices).pack(pady=10)

    def get_matrices(self):
        self.process_names = [e.get() for e in self.process_name_entries]
        self.resource_names = [e.get() for e in self.resource_name_entries]
        self.clear_frame()

        ctk.CTkLabel(self.root, text="Enter Allocation Matrix:").pack()
        self.allocation_entries = []
        alloc_frame = ctk.CTkFrame(self.root)
        alloc_frame.pack()
        for i in range(self.process_count):
            row = []
            for j in range(self.resource_count):
                e = ctk.CTkEntry(alloc_frame, width=40)
                e.grid(row=i, column=j, padx=2, pady=2)
                e.insert(0, "0")
                row.append(e)
            self.allocation_entries.append(row)

        ctk.CTkLabel(self.root, text="Enter Max Matrix:").pack()
        self.max_entries = []
        max_frame = ctk.CTkFrame(self.root)
        max_frame.pack()
        for i in range(self.process_count):
            row = []
            for j in range(self.resource_count):
                e = ctk.CTkEntry(max_frame, width=40)
                e.grid(row=i, column=j, padx=2, pady=2)
                e.insert(0, "0")
                row.append(e)
            self.max_entries.append(row)

        ctk.CTkLabel(self.root, text="Enter Available Vector:").pack()
        self.available_entries = []
        avail_frame = ctk.CTkFrame(self.root)
        avail_frame.pack()
        for j in range(self.resource_count):
            e = ctk.CTkEntry(avail_frame, width=40)
            e.grid(row=0, column=j, padx=2, pady=2)
            e.insert(0, "0")
            self.available_entries.append(e)

        ctk.CTkButton(self.root, text="Start Simulation", command=self.simulation_gui).pack(pady=10)

    def simulation_gui(self):
        try:
            allocation = [[int(self.allocation_entries[i][j].get()) for j in range(self.resource_count)] for i in range(self.process_count)]
            max_need = [[int(self.max_entries[i][j].get()) for j in range(self.resource_count)] for i in range(self.process_count)]
            available = [int(self.available_entries[j].get()) for j in range(self.resource_count)]
        except:
            messagebox.showerror("Error", "Please enter valid integers.")
            return
        self.backend.setup(self.process_names, self.resource_names, allocation, max_need, available)
        self.refresh_simulation()

    def refresh_simulation(self):
        self.clear_frame()
        ctk.CTkLabel(self.root, text="Simulation Results", font=("Arial", 20, "bold")).pack(pady=10)

        self.display_matrix("Allocation Matrix", self.backend.allocation)
        self.display_matrix("Max Matrix", self.backend.max_need)
        need = self.backend.get_need()
        self.display_matrix("Need Matrix", need)
        self.display_vector("Available Vector", self.backend.available)

        deadlocked, safe_seq = self.backend.detect_deadlock()
        if not deadlocked:
            ctk.CTkLabel(self.root, text="System is in SAFE STATE!", text_color="green", font=("Arial", 14, "bold")).pack()
            ctk.CTkLabel(self.root, text="Safe Sequence: " + " -> ".join([self.backend.process_names[i] for i in safe_seq])).pack()
        else:
            ctk.CTkLabel(self.root, text="System is in DEADLOCK!", text_color="red", font=("Arial", 14, "bold")).pack()
            dead_proc = [self.backend.process_names[i] for i in deadlocked]
            ctk.CTkLabel(self.root, text="Deadlocked Processes: " + ", ".join(dead_proc)).pack(pady=2)

            kill_frame = ctk.CTkFrame(self.root)
            kill_frame.pack(pady=5)
            ctk.CTkLabel(kill_frame, text="Kill Process:").pack(side="left", padx=4)
            self.kill_var = ctk.StringVar(value=dead_proc[0])
            self.kill_menu = ttk.Combobox(kill_frame, textvariable=self.kill_var, values=dead_proc, state="readonly")
            self.kill_menu.pack(side="left")
            ctk.CTkButton(kill_frame, text="Kill", command=lambda: self.kill_process(self.kill_var.get())).pack(side="left", padx=5)

        ctk.CTkButton(self.root, text="Restart Input", command=self.init_gui).pack(pady=5)
        ctk.CTkButton(self.root, text="Exit", command=self.root.destroy).pack()

    def display_matrix(self, name, matrix):
        frame = ctk.CTkFrame(self.root)
        frame.pack(pady=4)
        ctk.CTkLabel(frame, text=name, font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=self.resource_count+1, pady=2)
        for j in range(self.resource_count):
            ctk.CTkLabel(frame, text=self.resource_names[j], width=4).grid(row=1, column=j+1)
        for i in range(self.process_count):
            ctk.CTkLabel(frame, text=self.process_names[i], width=6).grid(row=i+2, column=0)
            for j in range(self.resource_count):
                val = matrix[i][j]
                label = ctk.CTkLabel(frame, text=str(val), width=4)
                label.grid(row=i+2, column=j+1)

    def display_vector(self, name, vector):
        frame = ctk.CTkFrame(self.root)
        frame.pack(pady=4)
        ctk.CTkLabel(frame, text=name, font=("Arial", 12, "bold")).pack()
        row_frame = ctk.CTkFrame(frame)
        row_frame.pack()
        for j in range(self.resource_count):
            ctk.CTkLabel(row_frame, text=self.resource_names[j], width=6).grid(row=0, column=j)
        for j in range(self.resource_count):
            ctk.CTkLabel(row_frame, text=str(vector[j]), width=6).grid(row=1, column=j)

    def kill_process(self, pname):
        self.backend.kill_process(pname)
        messagebox.showinfo("Killed", f"Process {pname} killed. Resources released.")
        self.refresh_simulation()

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = ctk.CTk()
    DeadlockSimulatorGUI(app)
    app.mainloop()

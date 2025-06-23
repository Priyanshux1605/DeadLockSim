# main.py

import customtkinter as ctk
from tkinter import messagebox, ttk
from PIL import Image
from deadlock_backend import DeadlockBackend
import os

# This class inherits from your original GUI class logic
class DeadlockSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.backend = DeadlockBackend()
        self.rag_image_tk = None # To hold a reference to the graph image

    # This method displays your stylish start screen
    def show_start_screen(self):
        self.clear_frame()
        self.root.geometry("1000x600")
        self.root.title("🧠 Deadlock Simulator")
        
        ctk.CTkLabel(self.root, text="🧠 Deadlock Detection & Recovery", font=("Segoe UI", 26, "bold"), text_color="cyan").place(relx=0.5, rely=0.1, anchor="center")
        ctk.CTkLabel(self.root, text="A simple simulator to understand deadlocks in OS", font=("Segoe UI", 16), text_color="lightgray").place(relx=0.5, rely=0.18, anchor="center")
        ctk.CTkButton(self.root, text="🚀 START", font=("Segoe UI", 18, "bold"), corner_radius=32, fg_color="purple", hover_color="#5E17EB", command=self.init_gui).place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkButton(self.root, text="ℹ️ About", command=self.show_about, width=100).place(relx=0.95, rely=0.95, anchor="se")

    # The rest of the methods are from your original GUI, slightly adapted
    # to fit the new flow and features.
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
        ctk.CTkButton(self.root, text="⬅️ Back to Home", command=self.show_start_screen).pack()

    def get_names(self):
        try:
            self.process_count = int(self.process_entry.get())
            self.resource_count = int(self.resource_entry.get())
            if self.process_count <= 0 or self.resource_count <= 0: raise ValueError
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Please enter valid positive integers.")
            return
        
        self.clear_frame()
        scroll_frame = ctk.CTkScrollableFrame(self.root)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll_frame, text="Enter process names:").pack()
        self.process_name_entries = [ctk.CTkEntry(scroll_frame, placeholder_text=f"P{i}") for i in range(self.process_count)]
        for entry in self.process_name_entries: entry.pack()

        ctk.CTkLabel(scroll_frame, text="Enter resource names:").pack()
        self.resource_name_entries = [ctk.CTkEntry(scroll_frame, placeholder_text=f"R{i}") for i in range(self.resource_count)]
        for entry in self.resource_name_entries: entry.pack()
        ctk.CTkButton(scroll_frame, text="Next", command=self.get_matrices).pack(pady=10)

    def get_matrices(self):
        self.process_names = [e.get() or e.cget("placeholder_text") for e in self.process_name_entries]
        self.resource_names = [e.get() or e.cget("placeholder_text") for e in self.resource_name_entries]
        
        self.clear_frame()
        scroll_frame = ctk.CTkScrollableFrame(self.root)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll_frame, text="Enter Allocation Matrix:").pack()
        self.allocation_entries = self._create_matrix_ui(scroll_frame, self.process_count, self.resource_count)
        
        ctk.CTkLabel(scroll_frame, text="Enter Max Matrix:").pack()
        self.max_entries = self._create_matrix_ui(scroll_frame, self.process_count, self.resource_count)

        ctk.CTkLabel(scroll_frame, text="Enter Available Vector:").pack()
        self.available_entries = self._create_vector_ui(scroll_frame, self.resource_count)
        ctk.CTkButton(scroll_frame, text="Start Simulation", command=self.simulation_gui).pack(pady=10)

    def _create_matrix_ui(self, parent, rows, cols):
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=5)
        entries = [[ctk.CTkEntry(frame, width=40, placeholder_text="0") for _ in range(cols)] for _ in range(rows)]
        for i in range(rows):
            for j in range(cols):
                entries[i][j].grid(row=i, column=j, padx=2, pady=2)
        return entries
    
    def _create_vector_ui(self, parent, cols):
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=5)
        entries = [ctk.CTkEntry(frame, width=40, placeholder_text="0") for _ in range(cols)]
        for j, entry in enumerate(entries): entry.grid(row=0, column=j, padx=2, pady=2)
        return entries

    def simulation_gui(self):
        try:
            allocation = [[int(e.get() or 0) for e in row] for row in self.allocation_entries]
            max_need = [[int(e.get() or 0) for e in row] for row in self.max_entries]
            available = [int(e.get() or 0) for e in self.available_entries]
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Please enter valid integers.")
            return
        
        self.backend.setup(self.process_names, self.resource_names, allocation, max_need, available)
        self.refresh_simulation_view()

    def refresh_simulation_view(self):
        self.clear_frame()
        self.root.geometry("1200x750")

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkScrollableFrame(self.root)
        left_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(left_panel, text="Simulation Results", font=("Arial", 20, "bold")).pack(pady=10)
        self.display_matrix(left_panel, "Allocation Matrix", self.backend.allocation)
        self.display_matrix(left_panel, "Max Matrix", self.backend.max_need)
        self.display_matrix(left_panel, "Need Matrix", self.backend.get_need())
        self.display_vector(left_panel, "Available Vector", self.backend.available)

        deadlocked, safe_seq = self.backend.detect_deadlock()
        if not deadlocked:
            ctk.CTkLabel(left_panel, text="System is in SAFE STATE!", text_color="green", font=("Arial", 14, "bold")).pack()
            safe_names = [self.backend.process_names[i] for i in safe_seq if not self.backend.terminated[i]]
            ctk.CTkLabel(left_panel, text="Safe Sequence: " + " -> ".join(safe_names)).pack()
        else:
            ctk.CTkLabel(left_panel, text="System is in DEADLOCK!", text_color="red", font=("Arial", 14, "bold")).pack()
            dead_proc_names = [self.backend.process_names[i] for i in deadlocked]
            ctk.CTkLabel(left_panel, text="Deadlocked Processes: " + ", ".join(dead_proc_names)).pack(pady=2)

            kill_frame = ctk.CTkFrame(left_panel)
            kill_frame.pack(pady=10)
            ctk.CTkButton(kill_frame, text="Auto Recover", command=self.auto_recover).pack(side="left", padx=5)
            self.kill_var = ctk.StringVar(value=dead_proc_names[0] if dead_proc_names else "")
            self.kill_menu = ctk.CTkOptionMenu(kill_frame, variable=self.kill_var, values=dead_proc_names)
            self.kill_menu.pack(side="left")
            ctk.CTkButton(kill_frame, text="Kill Selected", command=lambda: self.kill_process(self.kill_var.get())).pack(side="left", padx=5)

        ctk.CTkButton(left_panel, text="Restart Simulation", command=self.show_start_screen).pack(pady=20)
        
        graph_panel = ctk.CTkFrame(self.root)
        graph_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(graph_panel, text="Resource Allocation Graph", font=("Arial", 20, "bold")).pack(pady=10)
        self.graph_label = ctk.CTkLabel(graph_panel, text="Graph will be displayed here.")
        self.graph_label.pack(expand=True, fill="both", padx=10, pady=10)
        self.update_graph_display()

    def update_graph_display(self):
        graph_path = "rag_graph.png"
        self.backend.generate_rag_image(graph_path)
        if os.path.exists(graph_path):
            img = Image.open(graph_path)
            self.rag_image_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(500, 450))
            self.graph_label.configure(image=self.rag_image_tk, text="")

    def display_matrix(self, parent, name, matrix):
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=4)
        ctk.CTkLabel(frame, text=name, font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=self.backend.resource_count + 1, pady=2)
        for j in range(self.backend.resource_count): ctk.CTkLabel(frame, text=self.backend.resource_names[j]).grid(row=1, column=j + 1)
        for i in range(self.backend.process_count):
            p_name = self.backend.process_names[i]
            if self.backend.terminated[i]: p_name += " (Killed)"
            ctk.CTkLabel(frame, text=p_name).grid(row=i + 2, column=0, padx=5)
            for j in range(self.backend.resource_count):
                ctk.CTkLabel(frame, text=str(matrix[i][j])).grid(row=i + 2, column=j + 1)

    def display_vector(self, parent, name, vector):
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=4)
        ctk.CTkLabel(frame, text=name, font=("Arial", 12, "bold")).pack()
        row_frame = ctk.CTkFrame(frame); row_frame.pack()
        for j in range(self.backend.resource_count): ctk.CTkLabel(row_frame, text=self.backend.resource_names[j]).grid(row=0, column=j, padx=5)
        for j in range(self.backend.resource_count): ctk.CTkLabel(row_frame, text=str(vector[j])).grid(row=1, column=j)

    def kill_process(self, pname):
        if not pname: return
        self.backend.kill_process(pname)
        messagebox.showinfo("Killed", f"Process {pname} killed. Resources released.")
        self.refresh_simulation_view()
        
    def auto_recover(self):
        killed_pname = self.backend.auto_recover()
        if killed_pname:
            messagebox.showinfo("Auto Recover", f"System chose to kill process {killed_pname} to break the deadlock.")
            self.refresh_simulation_view()

    def clear_frame(self):
        for widget in self.root.winfo_children(): widget.destroy()

    def show_about(self):
        messagebox.showinfo("About", "Created by Priyanshu\nDeadlock Simulator v1.0")


if __name__ == "__main__":
    app_root = ctk.CTk()
    ctk.set_appearance_mode("dark")
    gui = DeadlockSimulatorGUI(app_root)
    gui.show_start_screen() # Start with the style screen
    app_root.mainloop()
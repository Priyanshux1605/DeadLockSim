import customtkinter as ctk

# Setup
ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.geometry("1000x600")
app.title("🧠 Deadlock Simulator")

# Fancy title label
title_label = ctk.CTkLabel(
    master=app,
    text="🧠 Deadlock Detection & Recovery",
    font=("Segoe UI", 26, "bold"),
    text_color="cyan"
)
title_label.place(relx=0.5, rely=0.1, anchor="center")

# Subtitle label
subtitle = ctk.CTkLabel(
    master=app,
    text="A simple simulator to understand deadlocks in OS",
    font=("Segoe UI", 16),
    text_color="lightgray"
)
subtitle.place(relx=0.5, rely=0.18, anchor="center")

# Glowing START button with hover effect
start_btn = ctk.CTkButton(
    master=app,
    text="🚀 START",
    font=("Segoe UI", 18, "bold"),
    corner_radius=32,
    fg_color="purple",
    hover_color="#5E17EB"  # hover shade
)
start_btn.place(relx=0.5, rely=0.5, anchor="center")

# About button at bottom right
def show_about():
    win = ctk.CTkToplevel(app)
    win.geometry("300x200")
    win.title("About")
    lbl = ctk.CTkLabel(win, text="Created by Priyanshu\nVersion 1.0", font=("Arial", 14))
    lbl.pack(pady=20)
    ctk.CTkButton(win, text="Close", command=win.destroy).pack()

about_btn = ctk.CTkButton(app, text="ℹ️ About", command=show_about, width=100)
about_btn.place(relx=0.95, rely=0.95, anchor="se")

# Run it!
app.mainloop()

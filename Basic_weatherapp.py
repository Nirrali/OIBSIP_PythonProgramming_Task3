import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
from PIL import Image, ImageTk
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

API_KEY = "653df4411d8f282fb04a544c5e37e194"  # Replace with your OpenWeatherMap API key

# ------------------ Fetch Current Weather ------------------
def get_current_weather(city):
    unit = "metric" if temp_unit.get() == "C" else "imperial"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={unit}"
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] != 200:
            messagebox.showerror("Error", f"City not found: {data['message']}")
            return None
        return data
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Network Error", str(e))
        return None

# ------------------ Fetch Forecast ------------------
def get_forecast(city):
    unit = "metric" if temp_unit.get() == "C" else "imperial"
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={unit}"
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] != "200":
            messagebox.showerror("Error", f"Forecast not found: {data['message']}")
            return None
        return data
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Network Error", str(e))
        return None

# ------------------ Update Weather ------------------
def update_weather():
    city = city_entry.get().strip()
    if not city:
        messagebox.showwarning("Input Error", "Please enter a city name.")
        return

    current = get_current_weather(city)
    forecast = get_forecast(city)
    if not current or not forecast:
        return

    # Current weather display
    temp = current["main"]["temp"]
    humidity = current["main"]["humidity"]
    condition = current["weather"][0]["description"]
    icon_code = current["weather"][0]["icon"]

    weather_text.set(f"Temperature: {temp}°{temp_unit.get()}\n"
                     f"Humidity: {humidity}%\n"
                     f"Condition: {condition.title()}")

    icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
    icon_response = requests.get(icon_url)
    icon_image = Image.open(BytesIO(icon_response.content))
    icon_photo = ImageTk.PhotoImage(icon_image)
    weather_icon_label.config(image=icon_photo)
    weather_icon_label.image = icon_photo

    # Hourly forecast chart (next 12 hours)
    hours = []
    temps = []
    now = datetime.datetime.now()
    for item in forecast["list"][:12]:
        dt = datetime.datetime.fromtimestamp(item["dt"])
        hours.append(dt.strftime("%H:%M"))
        temps.append(item["main"]["temp"])

    fig.clear()
    ax = fig.add_subplot(111)
    ax.plot(hours, temps, marker='o', linestyle='-', color='cyan')
    ax.set_title(f"{city.title()} Temperature Next 12 Hours")
    ax.set_xlabel("Time")
    ax.set_ylabel(f"Temp (°{temp_unit.get()})")
    ax.grid(True)
    fig.tight_layout()
    canvas.draw()

# ------------------ GUI ------------------
root = tk.Tk()
root.title("Advanced Weather App")
root.geometry("600x700")
root.configure(bg="#2E3F4F")

# Heading
tk.Label(root, text="Advanced Weather App", bg="#2E3F4F", fg="white",
         font=("Helvetica", 16, "bold")).pack(pady=10)

# City input
frame_city = tk.Frame(root, bg="#2E3F4F")
frame_city.pack(pady=5)
tk.Label(frame_city, text="Enter City:", bg="#2E3F4F", fg="white",
         font=("Arial", 12)).pack(side="left")
city_entry = tk.Entry(frame_city, width=25, font=("Arial", 12))
city_entry.pack(side="left", padx=5)

# Temperature unit toggle
temp_unit = tk.StringVar(value="C")
frame_unit = tk.Frame(root, bg="#2E3F4F")
frame_unit.pack(pady=5)
tk.Radiobutton(frame_unit, text="Celsius", variable=temp_unit, value="C",
               bg="#2E3F4F", fg="white", selectcolor="#4CAF50", font=("Arial", 10)).pack(side="left", padx=5)
tk.Radiobutton(frame_unit, text="Fahrenheit", variable=temp_unit, value="F",
               bg="#2E3F4F", fg="white", selectcolor="#4CAF50", font=("Arial", 10)).pack(side="left", padx=5)

# Get Weather button
tk.Button(root, text="Get Weather", command=update_weather, bg="#4CAF50", fg="white",
          font=("Arial", 12, "bold")).pack(pady=10)

# Current weather display
weather_text = tk.StringVar()
tk.Label(root, textvariable=weather_text, bg="#2E3F4F", fg="white", font=("Arial", 12), justify="left").pack(pady=10)
weather_icon_label = tk.Label(root, bg="#2E3F4F")
weather_icon_label.pack(pady=5)

# Matplotlib Figure for hourly forecast
fig = plt.Figure(figsize=(6,3), dpi=100, facecolor="#2E3F4F")
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=10)

root.mainloop()

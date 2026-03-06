import numpy as np
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import os
from Functions.misc import update_json, write_json, read_json
from Functions.sunpy_map_cut import sunpy_map_cut
from Functions.slit_maker import get_rectangle_on_map
from sunpy.map import Map as sm
from Functions.utilities import get_extent

class SlitFinderApp1:
    def __init__(self, root, zipped_arg):
        self.root = root
        self.root.title("Image Contrast Adjuster")
        # self.root.state('zoomed')  # Enable full-screen mode
        # self.root.attributes('-fullscreen', True)  # Works on Linux and macOS


        # Grid layout configuration
        self.root.grid_columnconfigure(0, weight=3)  # More space for figure
        self.root.grid_columnconfigure(1, weight=1)  # Less space for widgets
        self.root.grid_rowconfigure(0, weight=1)  # Expand row
        
        self.file, self.initial_vmin, self.initial_vmax, self.X, self.Y, self.DX, self.DY, self.angle, self.json_file_path = zipped_arg
        
        self.m = sm(self.file)
        self.date = str(self.m.date)
        self.image = self.m.data
        self.extent = get_extent(self.m)

        os.makedirs(os.path.dirname(self.json_file_path), exist_ok=True)
        if not os.path.isfile(self.json_file_path):
            info = {
                self.date: {
                    'vmin': self.initial_vmin,
                    'vmax': self.initial_vmax,
                    'X': self.X,
                    'Y': self.Y,
                    'DX': self.DX,
                    'DY': self.DY,
                    'angle': self.angle
                }
            }
            write_json(self.json_file_path, info)
        else:
            try:
                old_info = read_json(self.json_file_path)
                self.initial_vmin = old_info[self.date]['vmin']
                self.initial_vmax = old_info[self.date]['vmax']
                self.X = old_info[self.date]['X']
                self.Y = old_info[self.date]['Y']
                self.DX = old_info[self.date]['DX']
                self.DY = old_info[self.date]['DY']
                self.angle = old_info[self.date]['angle']
            except:
                old_info = read_json(self.json_file_path)
                old_info_key = list(old_info.keys())[-1]
                self.initial_vmin = old_info[old_info_key]['vmin']
                self.initial_vmax = old_info[old_info_key]['vmax']
                self.X = old_info[old_info_key]['X']
                self.Y = old_info[old_info_key]['Y']
                self.DX = old_info[old_info_key]['DX']
                self.DY = old_info[old_info_key]['DY']
                self.angle = old_info[old_info_key]['angle']

                info = {
                    self.date: {
                        'vmin': self.initial_vmin,
                        'vmax': self.initial_vmax,
                        'X': self.X,
                        'Y': self.Y,
                        'DX': self.DX,
                        'DY': self.DY,
                        'angle': self.angle
                    }
                }
                update_json(self.json_file_path, info)
        RECTANGLE, RECTANGLE_world, rectangles, rectangles_world, data_RECTANGLE, data_rectangles = get_rectangle_on_map(
            self.m, self.X, self.Y, self.DX, self.DY, self.angle, n=5, rotation_point='mid'
        )

        # Matplotlib figure setup
        self.fig, self.ax = plt.subplots(figsize=(6,6))
        self.img_display = self.ax.imshow(
            self.image, origin="lower", cmap='gray', extent=self.extent,
            vmin=self.initial_vmin, vmax=self.initial_vmax
        )
        self.ax.set_title("Adjust Image and Rectangles")
        
        self.im_RECTANGLE = self.ax.plot(RECTANGLE_world.Tx.value, RECTANGLE_world.Ty.value, linewidth=2)
        self.im_rectangles = [self.ax.plot(rect[:, 1], rect[:, 0]) for rect in rectangles_world]

        # Embed Matplotlib in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=10, sticky="nsew", padx=10, pady=10)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, root, pack_toolbar=False)
        self.toolbar.grid(row=10, column=0, sticky="ew", pady=5)
        
        self.create_widgets()

    def create_widgets(self):
        # Frame for sliders
        controls_frame = ttk.Frame(self.root)
        controls_frame.grid(row=0, column=1, rowspan=10, sticky="ns", padx=10, pady=10)
        
        def create_slider(label, from_, to, variable, callback):
            frame = ttk.Frame(controls_frame)
            frame.pack(fill="x", pady=5)
            ttk.Label(frame, text=label, width=8).pack(side="left")
            slider = ttk.Scale(frame, from_=from_, to=to, orient="horizontal", variable=variable, command=callback)
            slider.pack(side="left", fill="x", expand=True, padx=5)
            value_label = ttk.Label(frame, text=f"{variable.get():.2f}")
            value_label.pack(side="right")
            variable.trace_add("write", lambda *args: value_label.config(text=f"{variable.get():.2f}"))
            return slider
        
        self.vmin_var = tk.DoubleVar(value=self.initial_vmin)
        self.vmax_var = tk.DoubleVar(value=self.initial_vmax)
        self.x_var = tk.DoubleVar(value=self.X)
        self.y_var = tk.DoubleVar(value=self.Y)
        self.dx_var = tk.DoubleVar(value=self.DX)
        self.dy_var = tk.DoubleVar(value=self.DY)
        self.angle_var = tk.DoubleVar(value=self.angle)

        create_slider("vmin:", np.min(self.image), np.max(self.image), self.vmin_var, self.update_image)
        create_slider("vmax:", np.min(self.image), np.max(self.image), self.vmax_var, self.update_image)
        create_slider("X:", self.extent[0], self.extent[1], self.x_var, self.update_rectangles)
        create_slider("Y:", self.extent[2], self.extent[3], self.y_var, self.update_rectangles)
        create_slider("DX:", 1, self.extent[1]-self.extent[0], self.dx_var, self.update_rectangles)
        create_slider("DY:", 1, self.extent[1]-self.extent[0], self.dy_var, self.update_rectangles)
        create_slider("Angle:", -180, 180, self.angle_var, self.update_rectangles)

    def update_image(self, event=None):
        vmin, vmax = self.vmin_var.get(), self.vmax_var.get()
        old_info = read_json(self.json_file_path)
        new_info = {
            self.date: {
                'vmin': round(vmin, 2),
                'vmax': round(vmax, 2),
                'X': old_info[self.date]['X'],
                'Y': old_info[self.date]['Y'],
                'DX': old_info[self.date]['DX'],
                'DY': old_info[self.date]['DY'],
                'angle': old_info[self.date]['angle']
            }
        }
        update_json(self.json_file_path, new_info)

        if vmin >= vmax:
            return
        self.img_display.set_clim(vmin, vmax)
        self.canvas.draw()

    def update_rectangles(self, event=None):
        x, y, dx, dy, angle = self.x_var.get(), self.y_var.get(), self.dx_var.get(), self.dy_var.get(), self.angle_var.get()
        old_info = read_json(self.json_file_path)
        new_info = {
            self.date: {
                'vmin': old_info[self.date]['vmin'],
                'vmax': old_info[self.date]['vmax'],
                'X': round(x, 2),
                'Y': round(y, 2),
                'DX': round(dx, 2),
                'DY': round(dy, 2),
                'angle': round(angle, 2)
            }
        }
        update_json(self.json_file_path, new_info)

        _, RECTANGLE_world, _, rectangles_world, _, _ = get_rectangle_on_map(self.m, x, y, dx, dy, angle, n=5, rotation_point='mid')
        self.im_RECTANGLE[0].set_data(RECTANGLE_world.Tx.value, RECTANGLE_world.Ty.value)
        for rect_plot, rect_world in zip(self.im_rectangles, rectangles_world):
            rect_plot[0].set_data(rect_world[:, 1], rect_world[:, 0])
        self.canvas.draw()

class SlitFinderApp:
    def __init__(self, root, zipped_arg):
        self.root = root
        self.root.title("Image Contrast Adjuster")
        self.file, self.initial_vmin, self.initial_vmax, self.X, self.Y, self.DX, self.DY, self.angle, self.json_file_path = zipped_arg
        
        self.m = sm(self.file)
        self.date = str(self.m.date)
        self.image = self.m.data
        self.extent = get_extent(self.m)

        os.makedirs(os.path.dirname(self.json_file_path), exist_ok=True)
        if not os.path.isfile(self.json_file_path):
            info = {
                self.date: {
                    'vmin': self.initial_vmin,
                    'vmax': self.initial_vmax,
                    'X':self.X,
                    'Y':self.Y,
                    'DX':self.DX,
                    'DY':self.DY,
                    'angle':self.angle
                    }
                }
            write_json(self.json_file_path, info)
        else:
            old_info = read_json(self.json_file_path)
            self.initial_vmin = old_info[self.date]['vmin']
            self.initial_vmax = old_info[self.date]['vmax']
            self.X = old_info[self.date]['X']
            self.Y = old_info[self.date]['Y']
            self.DX = old_info[self.date]['DX']
            self.DY = old_info[self.date]['DY']
            self.angle = old_info[self.date]['angle']

        
        RECTANGLE, RECTANGLE_world, rectangles, rectangles_world, data_RECTANGLE, data_rectangles = get_rectangle_on_map(
            self.m, self.X, self.Y, self.DX, self.DY, self.angle, n=5, rotation_point='mid'
        )
        
        self.fig, self.ax = plt.subplots()

        self.img_display = self.ax.imshow(
            self.image, origin="lower", cmap='gray', extent=self.extent,
            vmin=self.initial_vmin, vmax=self.initial_vmax
        )
        self.ax.set_title("Adjust Image and Rectangles")
        
        self.im_RECTANGLE = self.ax.plot(RECTANGLE_world.Tx.value, RECTANGLE_world.Ty.value, linewidth=2)
        self.im_rectangles = [self.ax.plot(rect[:, 1], rect[:, 0]) for rect in rectangles_world]
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=3, padx=10, pady=10)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, root, pack_toolbar=False)
        self.toolbar.grid(row=1, column=0, columnspan=3, pady=5)
        
        self.create_widgets()

        
    
    def create_widgets(self):
        def create_slider(label, from_, to, row, variable, callback):
            frame = ttk.Frame(self.root)
            frame.grid(row=row, column=0, columnspan=3, pady=5, sticky="ew")
            ttk.Label(frame, text=label).pack(side="left")
            slider = ttk.Scale(frame, from_=from_, to=to, orient="horizontal", variable=variable, command=callback)
            slider.pack(side="left", fill="x", expand=True, padx=5)
            value_label = ttk.Label(frame, text=f"{variable.get():.2f}")
            value_label.pack(side="right")
            variable.trace_add("write", lambda *args: value_label.config(text=f"{variable.get():.2f}"))
            return slider
        
        self.vmin_var = tk.DoubleVar(value=self.initial_vmin)
        self.vmax_var = tk.DoubleVar(value=self.initial_vmax)
        self.x_var = tk.DoubleVar(value=self.X)
        self.y_var = tk.DoubleVar(value=self.Y)
        self.dx_var = tk.DoubleVar(value=self.DX)
        self.dy_var = tk.DoubleVar(value=self.DY)
        self.angle_var = tk.DoubleVar(value=self.angle)
        
        create_slider("vmin:", np.min(self.image), np.max(self.image), 2, self.vmin_var, self.update_image)
        create_slider("vmax:", np.min(self.image), np.max(self.image), 3, self.vmax_var, self.update_image)
        create_slider("X:", self.extent[0], self.extent[1], 4, self.x_var, self.update_rectangles)
        create_slider("Y:", self.extent[2], self.extent[3], 5, self.y_var, self.update_rectangles)
        create_slider("DX:", 1, self.extent[1]-self.extent[0], 6, self.dx_var, self.update_rectangles)
        create_slider("DY:", 1, self.extent[1]-self.extent[0], 7, self.dy_var, self.update_rectangles)
        create_slider("Angle:", -180, 180, 8, self.angle_var, self.update_rectangles)
    
    def update_image(self, event=None):
        vmin, vmax = self.vmin_var.get(), self.vmax_var.get()
        old_info = read_json(self.json_file_path)
        new_info = {
            self.date: {
                'vmin': round(vmin, 2),
                'vmax': round(vmax, 2),
                'X':old_info[self.date]['X'],
                'Y':old_info[self.date]['Y'],
                'DX':old_info[self.date]['DX'],
                'DY':old_info[self.date]['DY'],
                'angle':old_info[self.date]['angle']
                }
            }
        update_json(self.json_file_path, new_info)

        if vmin >= vmax:
            return
        self.img_display.set_clim(vmin, vmax)
        self.canvas.draw()
    
    def update_rectangles(self, event=None):
        x, y, dx, dy, angle = self.x_var.get(), self.y_var.get(), self.dx_var.get(), self.dy_var.get(), self.angle_var.get()
        old_info = read_json(self.json_file_path)
        new_info = {
            self.date: {
                'vmin': old_info[self.date]['vmin'],
                'vmax': old_info[self.date]['vmax'],
                'X':round(x,2),
                'Y':round(y,2),
                'DX':round(dx,2),
                'DY':round(dy,2),
                'angle':round(angle,2)
                }
            }
        update_json(self.json_file_path, new_info)
        _, RECTANGLE_world, _, rectangles_world, _, _ = get_rectangle_on_map(self.m, x, y, dx, dy, angle, n=5, rotation_point='mid')
        self.im_RECTANGLE[0].set_data(RECTANGLE_world.Tx.value, RECTANGLE_world.Ty.value)
        for rect_plot, rect_world in zip(self.im_rectangles, rectangles_world):
            rect_plot[0].set_data(rect_world[:, 1], rect_world[:, 0])
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = SlitFinderApp(root, ("./../../iris_dem/DATA_TEST/2016-03-19T16:13:30.000000.fits", 40, 400, 25, 350, 15, 75, 0, './parameters/data.json'))
    root.mainloop()

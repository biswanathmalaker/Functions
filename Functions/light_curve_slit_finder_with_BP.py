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
from Functions.sunpy_map_cut import cut_one_map_from_another
from matplotlib.colors import TwoSlopeNorm
import copy
import datetime
from Functions.derotate import de_rotate

class SlitFinderApp:
    def __init__(self, root, zipped_arg):
        self.root = root
        self.root.geometry("1500x1000") 
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.title("BASE PARAMETER FINDER")
        self.files, self.initial_vmin, self.initial_vmax, self.initial_vmin_hmi, self.initial_vmax_hmi, self.XCEN, self.YCEN, self.DX, self.DY,self.DY_HMI, self.angle, self.json_file_path = zipped_arg
        
        r_up = False
        bl = [100,-500]
        tr = [500,-100]
        if r_up:
            bl = [100,100]
            tr = [500,500]
        self.hmi_angle=0
        if self.YCEN > 0:
            self.hmi_angle = 180
        
        self.m = sunpy_map_cut(sm(self.files[0]),bl,tr)
        self.m_hmi = cut_one_map_from_another(sm(self.files[1]),self.m)

        self.date = str(self.m.date)
        self.date_obj = datetime.datetime.strptime(self.date,'%Y-%m-%dT%H:%M:%S.%f')

        self.image = self.m.data
        self.extent = get_extent(self.m)

        self.date_hmi = str(self.m_hmi.date)
        self.image_hmi = self.m_hmi.data
        self.extent_hmi = get_extent(self.m_hmi)

        self.norm_hmi = TwoSlopeNorm(0,self.initial_vmin_hmi,self.initial_vmax_hmi)

        os.makedirs(os.path.dirname(self.json_file_path), exist_ok=True)

        self.DX_BP = copy.deepcopy(self.DX)
        self.DY_BP = self.DY_HMI
        if not os.path.isfile(self.json_file_path):
            info = {
                self.date: {
                    'vmin': self.initial_vmin,
                    'vmax': self.initial_vmax,
                    'vmin_hmi': self.initial_vmin_hmi,
                    'vmax_hmi': self.initial_vmax_hmi,
                    'XCEN':self.XCEN,
                    'YCEN':self.YCEN,
                    'DX':self.DX,
                    'DY':self.DY,
                    'DX_BP':self.DX,
                    'DY_BP':self.DY_HMI,
                    'DY_HMI':self.DY_HMI,
                    'angle':self.angle,
                    'hmi_angle':self.hmi_angle
                    }
                }
            write_json(self.json_file_path, info)
        else:
            old_info = read_json(self.json_file_path)
            if self.date in list(old_info.keys()):
                self.initial_vmin = old_info[self.date]['vmin']
                self.initial_vmax = old_info[self.date]['vmax']
                self.initial_vmin_hmi = old_info[self.date]['vmin_hmi']
                self.initial_vmax_hmi = old_info[self.date]['vmax_hmi']
                self.XCEN = old_info[self.date]['XCEN']
                self.YCEN = old_info[self.date]['YCEN']
                self.DX = old_info[self.date]['DX']
                self.DY = old_info[self.date]['DY']
                self.DX_BP = old_info[self.date]['DX_BP']
                self.DY_BP = old_info[self.date]['DY_BP']
                self.DY_HMI = old_info[self.date]['DY_HMI']
                self.angle = old_info[self.date]['angle']
                self.hmi_angle = old_info[self.date]['hmi_angle']
            else:
                existed_keys = np.array(list(old_info.keys()))
                key_datetime_obj = [datetime.datetime.strptime(t,"%Y-%m-%dT%H:%M:%S.%f") for t in existed_keys]
                key_datetime_obj = np.array(key_datetime_obj)

                DT = [abs((t-self.date_obj).total_seconds()) for t in key_datetime_obj]
                DT = np.array(DT)
                DT_sorted_ind = np.argmin(DT)
                nearest_key = existed_keys[DT_sorted_ind]
                # print(nearest_key)
                # print(self.date)
                # print([old_info[nearest_key]['YCEN'],old_info[nearest_key]['YCEN']])

                self.initial_vmin = old_info[nearest_key]['vmin']
                self.initial_vmax = old_info[nearest_key]['vmax']
                self.initial_vmin_hmi = old_info[nearest_key]['vmin_hmi']
                self.initial_vmax_hmi = old_info[nearest_key]['vmax_hmi']
                self.XCEN,self.YCEN = de_rotate(
                    self.files[0],
                    [old_info[nearest_key]['XCEN'],old_info[nearest_key]['YCEN']],
                    nearest_key,
                    self.date
                    )
                self.DX = old_info[nearest_key]['DX']
                self.DY = old_info[nearest_key]['DY']
                self.DX_BP = old_info[nearest_key]['DX_BP']
                self.DY_BP = old_info[nearest_key]['DY_BP']
                self.DY_HMI = old_info[nearest_key]['DY_HMI']
                self.angle = old_info[nearest_key]['angle']
                self.hmi_angle = old_info[nearest_key]['hmi_angle']
                # print("Will update things..")

                info = {
                    self.date: {
                        'vmin': self.initial_vmin,
                        'vmax': self.initial_vmax,
                        'vmin_hmi': self.initial_vmin_hmi,
                        'vmax_hmi': self.initial_vmax_hmi,
                        'XCEN':self.XCEN,
                        'YCEN':self.YCEN,
                        'DX':self.DX,
                        'DY':self.DY,
                        'DX_BP':self.DX_BP,
                        'DY_BP':self.DY_BP,
                        'DY_HMI':self.DY_HMI,
                        'angle':self.angle,
                        'hmi_angle':self.hmi_angle
                        }
                    }
                update_json(self.json_file_path, info)



        self.X = self.XCEN-self.DX/2
        self.Y = self.YCEN
   
        _, RECTANGLE_world = get_rectangle_on_map(
            self.m, self.X, self.Y, self.DX, self.DY, self.angle, n=None, rotation_point='mid',return_DN=False
        )
        _, RECTANGLE_world_HMI = get_rectangle_on_map(
            self.m, self.X, self.Y, self.DX, self.DY_HMI, self.hmi_angle, n=None, rotation_point='mid',return_DN=False
        )

        _, RECTANGLE_world_BP = get_rectangle_on_map(
            self.m, self.X, self.Y, self.DX_BP, self.DY_BP, self.hmi_angle, n=None, rotation_point='mid',return_DN=False
        )

        # self.fig, self.ax = plt.subplots()
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1,2,1)
        self.ax_hmi = self.fig.add_subplot(1,2,2,sharex=self.ax,sharey=self.ax)

        self.img_display = self.ax.imshow(
            self.image, origin="lower", cmap='gray', extent=self.extent,
            vmin=self.initial_vmin, vmax=self.initial_vmax
        )

        self.img_display_hmi = self.ax_hmi.imshow(
            self.image_hmi, origin="lower", cmap='gray',norm=self.norm_hmi, extent=self.extent,
        )
        # print((f"{self.date_hmi}"))
        self.ax.set_title(f"{self.date}")
        self.ax_hmi.set_title(f"{self.date_hmi}")

        
        self.im_RECTANGLE = self.ax.plot(RECTANGLE_world.Tx.value, RECTANGLE_world.Ty.value, linewidth=2,color='red')
        self.im_RECTANGLE_HMI = self.ax.plot(RECTANGLE_world_HMI.Tx.value, RECTANGLE_world_HMI.Ty.value, linewidth=2,color='blue')
        self.im_RECTANGLE_BP = self.ax.plot(RECTANGLE_world_BP.Tx.value, RECTANGLE_world_BP.Ty.value, linewidth=2,color='cyan')

        # self.im_rectangles = [self.ax.plot(rect[:, 1], rect[:, 0]) for rect in rectangles_world]
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=3, padx=10, pady=10)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, root, pack_toolbar=False)
        self.toolbar.grid(row=1, column=0, columnspan=3, pady=5)
        
        self.create_widgets()

    def on_close(self):
        plt.close(self.fig)
        self.root.destroy()

    def create_widgets(self):
        def create_slider(label, from_, to, row, variable, callback):
            frame = ttk.Frame(self.root)
            frame.grid(row=row, column=0, columnspan=3, pady=5, sticky="ew")
            ttk.Label(frame, text=label).pack(side="left")
            slider = ttk.Scale(frame, from_=from_, to=to, orient="horizontal", variable=variable, command=callback,length=800)
            slider.pack(side="left", fill="x", expand=True, padx=5)
            value_label = ttk.Label(frame, text=f"{variable.get():.2f}")
            value_label.pack(side="right")
            variable.trace_add("write", lambda *args: value_label.config(text=f"{variable.get():.2f}"))
            return slider
        
        self.vmin_var = tk.DoubleVar(value=self.initial_vmin)
        self.vmax_var = tk.DoubleVar(value=self.initial_vmax)
        self.vmin_hmi_var = tk.DoubleVar(value=self.initial_vmin_hmi)
        self.vmax_hmi_var = tk.DoubleVar(value=self.initial_vmax_hmi)
        self.x_var = tk.DoubleVar(value=self.X)
        self.y_var = tk.DoubleVar(value=self.Y)
        self.dx_var = tk.DoubleVar(value=self.DX)
        self.dy_var = tk.DoubleVar(value=self.DY)
        self.angle_var = tk.DoubleVar(value=self.angle)
        self.dy_hmi_var = tk.DoubleVar(value=self.DY_HMI)
        self.dx_bp_var = tk.DoubleVar(value=self.DX_BP)
        self.dy_bp_var = tk.DoubleVar(value=self.DY_BP)

        create_slider("vmin:", np.min(self.image), np.max(self.image), 2, self.vmin_var, self.update_image)
        create_slider("vmax:", np.min(self.image), np.max(self.image), 3, self.vmax_var, self.update_image)
        create_slider("vmin_hmi:", np.min(self.image_hmi), np.max(self.image_hmi), 4, self.vmin_hmi_var, self.update_image)
        create_slider("vmax_hmi:", np.min(self.image_hmi), np.max(self.image_hmi), 5, self.vmax_hmi_var, self.update_image)
        create_slider("X:", self.extent[0], self.extent[1], 6, self.x_var, self.update_rectangles)
        create_slider("Y:", self.extent[2], self.extent[3], 7, self.y_var, self.update_rectangles)
        create_slider("DX:", 1, self.extent[1]-self.extent[0], 8, self.dx_var, self.update_rectangles)
        create_slider("DY:", 1, self.extent[3]-self.extent[2], 9, self.dy_var, self.update_rectangles)
        create_slider("Angle:", -180, 180, 10, self.angle_var, self.update_rectangles)
        create_slider("DY_HMI:", 1, self.extent[3]-self.extent[2], 11, self.dy_hmi_var, self.update_rectangles)
        create_slider("DX_BP:", 1, self.extent[3]-self.extent[2], 12, self.dx_bp_var, self.update_rectangles)
        create_slider("DY_BP:", 1, self.extent[3]-self.extent[2], 13, self.dy_bp_var, self.update_rectangles)

    def update_image(self, event=None):
        vmin, vmax = self.vmin_var.get(), self.vmax_var.get()
        vmin_hmi, vmax_hmi = self.vmin_hmi_var.get(), self.vmax_hmi_var.get()
        old_info = read_json(self.json_file_path)
        new_info = {
            self.date: {
                'vmin': round(vmin, 2),
                'vmax': round(vmax, 2),
                'vmin_hmi': round(vmin_hmi, 2),
                'vmax_hmi': round(vmax_hmi, 2),
                'XCEN':old_info[self.date]['XCEN'],
                'YCEN':old_info[self.date]['YCEN'],
                'DX':old_info[self.date]['DX'],
                'DY':old_info[self.date]['DY'],
                'DX_BP':old_info[self.date]['DX_BP'],
                'DY_BP':old_info[self.date]['DY_BP'],
                'DY_HMI':old_info[self.date]['DY_HMI'],
                'angle':old_info[self.date]['angle'],
                'hmi_angle':old_info[self.date]['hmi_angle']

                }
            }
        update_json(self.json_file_path, new_info)

        if vmin >= vmax:
            return
        if vmin_hmi >= vmax_hmi:
            return
        self.img_display.set_clim(vmin, vmax)
        self.img_display_hmi.set_clim(vmin_hmi, vmax_hmi)

        self.canvas.draw()
    
    def update_rectangles(self, event=None):
        x, y, dx, dy, angle , dy_hmi = self.x_var.get(), self.y_var.get(), self.dx_var.get(), self.dy_var.get(), self.angle_var.get(),self.dy_hmi_var.get()
        dx_bp , dy_bp = self.dx_bp_var.get(), self.dy_bp_var.get()

        hmi_angle = 0
        if y>0:
            hmi_angle = 180
        # y_hmi = y-dy_hmi
        # if y<0:
        #     y_hmi = y + dy_hmi
        
        old_info = read_json(self.json_file_path)
        new_info = {
            self.date: {
                'vmin': old_info[self.date]['vmin'],
                'vmax': old_info[self.date]['vmax'],
                'vmin_hmi': old_info[self.date]['vmin_hmi'],
                'vmax_hmi': old_info[self.date]['vmax_hmi'],
                'XCEN':round(x+dx/2,2),
                'YCEN':round(y,2),
                'DX':round(dx,2),
                'DY':round(dy,2),
                'DX_BP':round(dx_bp,2),
                'DY_BP':round(dy_bp,2),
                'DY_HMI':round(dy_hmi,2),
                'angle':round(angle,2),
                'hmi_angle':round(hmi_angle,2)
                }
            }
        update_json(self.json_file_path, new_info)
        _, RECTANGLE_world = get_rectangle_on_map(self.m, x, y, dx, dy, angle, n=None, rotation_point='mid',return_DN=False)
        _, RECTANGLE_world_HMI = get_rectangle_on_map(
            self.m, x, y, dx, dy_hmi, hmi_angle, n=None, rotation_point='mid',return_DN=False
        )
        _, RECTANGLE_world_BP = get_rectangle_on_map(
            self.m, x, y, dx_bp, dy_bp, hmi_angle, n=None, rotation_point='mid',return_DN=False
        )
        self.im_RECTANGLE[0].set_data(RECTANGLE_world.Tx.value, RECTANGLE_world.Ty.value)
        self.im_RECTANGLE_HMI[0].set_data(RECTANGLE_world_HMI.Tx.value, RECTANGLE_world_HMI.Ty.value)
        self.im_RECTANGLE_BP[0].set_data(RECTANGLE_world_BP.Tx.value, RECTANGLE_world_BP.Ty.value)

        # for rect_plot, rect_world in zip(self.im_rectangles, rectangles_world):
        #     rect_plot[0].set_data(rect_world[:, 1], rect_world[:, 0])
        self.canvas.draw()

if __name__ == "__main__":

    r_up = True
    bl = [100,-500]
    tr = [500,-100]
    if r_up:
        bl = [100,100]
        tr = [500,500]


    files = ["./../../LIGHT_CURVES_data/data_aia/aia.lev1_euv_12s.2019-03-01T000010Z.171.image_lev1.fits","./../../LIGHT_CURVES_data/data_hmi/hmi.m_45s.20190301_000045_TAI.2.magnetogram.fits"]
    initial_vmin = 40
    initial_vmax = 400

    initial_vmin_hmi = -40
    initial_vmax_hmi = 400

    XCEN = (bl[0]+tr[0])//2
    YCEN = (bl[1]+tr[1])//2
    DX = 15
    DY = 75
    DY_HMI = 20
    angle = 0
    json_file_path = './parameters/data_bp.json'
    ziped_args = (files, initial_vmin, initial_vmax, initial_vmin_hmi, initial_vmax_hmi, XCEN, YCEN, DX, DY,DY_HMI, angle,json_file_path)
    root = tk.Tk()
    
    app = SlitFinderApp(root,ziped_args)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        plt.close('all')
        root.destroy()









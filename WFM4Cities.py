from scipy.spatial.distance import pdist, squareform, cdist
from sklearn.datasets import make_blobs
import tkinter as tk
from tkinter import Text
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pysal.lib import weights
from pysal.explore import esda
import geopandas as gpd
from shapely.geometry import Point
from scipy.interpolate import griddata
import itertools
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.animation import FuncAnimation
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.cm import get_cmap
from matplotlib.collections import PolyCollection
import matplotlib.patches as patches
import numpy as np
import matplotlib.gridspec as gridspec
from numpy.polynomial.polynomial import Polynomial
from scipy.spatial import Delaunay
from numpy.linalg import norm
import matplotlib
import tkinter as tk
from tkinter import messagebox
from matplotlib import rcParams
rcParams['font.family'] = 'SimHei'
matplotlib.use('TkAgg')  # 显式使用 TkAgg 后端
current_language = "English"  # 或 "Chinese"
import numpy as np
inf = np.inf


def main():
    print("软件界面已启动")

    # 创建主窗口
    root1 = tk.Tk()  # 创建Tkinter主窗口
    root1.geometry('800x480')  # 设置窗口大小
    root1.configure(background='#D3D3D3')  # 设置窗口背景色
    root1.title("Water-Flooding Model")  # 设置窗口标题

    # 初始化翻译器（默认为英文）
    global translator
    translator = Translator(language="English")

    # 创建软件标题标签
    title_font = ('Arial', 20, 'bold')
    title_label = tk.Label(
        root1,
        text=translator.translate("Water-flooding Method for Urban 3D-morphology"),
        bg='#D3D3D3',
        fg='black',
        font=title_font
    )
    title_label.place(relx=0.5, rely=0.1, anchor='center')

    # 创建框架用于容纳滑块
    frame1 = tk.Frame(root1)
    frame1.place(relx=0.5, rely=0.25, anchor='center', relwidth=1.0)
    frame1.grid_columnconfigure(0, weight=1, minsize=50)
    frame1.grid_columnconfigure(4, weight=1, minsize=50)

    # 初始化并生成2D图形
    generate_plot_fig()

    # 创建3D图形窗口并初始化
    create_or_update_fig2(water_level=0.5)  # 默认水位为0.5（可以根据需求调整）

    # 创建语言选择按钮，点击时弹出语言选择窗口
    language_button = tk.Button(root1, text="Language", command=choose_language)
    language_button.place(relx=0.95, rely=0.1, anchor='ne')

    # 启动Tkinter主事件循环
    root1.mainloop()

# 将 Translator 类的代码直接放在 Water_flooding_Model.py 文件的顶部

class Translator:
    def __init__(self, language="English"):
        self.language = language
        self.translations = {
            "Water-flooding Method for Urban 3D-morphology": {
                "English": "Water-flooding Method for Urban 3D-morphology",
                "Chinese": "“地形-漫水”城市复杂空间演化模拟分析系统"},

            "Step1:Create 2D Plot": {"English": "Step1:Create 2D Plot", "Chinese": "步骤1：创建2D图"},
            "Step2:Create 3D Plot": {"English": "Step2:Create 3D Plot", "Chinese": "步骤2：创建3D图"},
            "Step3:Water-flooding Simulation": {"English": "Step3:Water-flooding Simulation", "Chinese": "步骤3：淹水模拟"},
            "① Number of Points": {"English": "① Number of Points", "Chinese": "① 点的数量"},
            "② Noise Ratio": {"English": "② Noise Ratio", "Chinese": "② 噪声比例"},
            "③ Number of Clusters": {"English": "③ Number of Clusters", "Chinese": "③ 聚类数量"},
            "④ Cluster Standard Deviation": {"English": "④ Cluster Standard Deviation", "Chinese": "④ 聚类标准差"},
            "⑤ Minimum Distance": {"English": "⑤ Minimum Distance", "Chinese": "⑤ 最小距离"},
            "⑥ Water Level": {"English": "⑥ Water Level", "Chinese": "⑥ 水位"},
            "⑦ X Slice": {"English": "⑦ X Slice", "Chinese": "⑦ X切片"},
            "⑧ Y Slice": {"English": "⑧ Y Slice", "Chinese": "⑧ Y切片"},
            "Language": {"English": "Language", "Chinese": "语言"},
        }

    def translate(self, element_name):
        return self.translations.get(element_name, {}).get(self.language, element_name)

    def set_language(self, language):
        self.language = language

# 在主程序中使用 Translator
translator = Translator(language="English")
print(translator.translate("Step1:Create 2D Plot"))



def generate_clusters(num_clusters, min_distance):
    centers = np.random.uniform(0, 10, (1, 2))
    while len(centers) < num_clusters:
        new_center = np.random.uniform(0, 10, (1, 2))
        if np.all(np.min(cdist(new_center, centers), axis=1) > min_distance):
            centers = np.vstack([centers, new_center])
    return centers

def plot_cube(ax, lower_limits, upper_limits, base_height):
    lower_limits[2] += base_height
    upper_limits[2] += base_height
    vertices = np.array(list(itertools.product(*zip(lower_limits, upper_limits))))
    faces = [[vertices[j] for j in face] for face in
             [[0, 1, 5, 4], [4, 5, 7, 6], [6, 7, 3, 2], [2, 3, 1, 0], [1, 3, 7, 5], [0, 4, 6, 2]]]
    ax.add_collection3d(Poly3DCollection(faces, linewidths=1, edgecolors='r', alpha=0.2))


def calculate_cavity_volume(grid_x, grid_y, grid_z):
    min_height = np.nanmin(grid_z)
    volume = 0.0
    for i in range(grid_x.shape[0] - 1):
        for j in range(grid_x.shape[1] - 1):
            if not np.isnan(grid_z[i, j]) and not np.isnan(grid_z[i + 1, j]) and not np.isnan(
                    grid_z[i, j + 1]) and not np.isnan(grid_z[i + 1, j + 1]):
                height = (grid_z[i, j] + grid_z[i + 1, j] + grid_z[i, j + 1] + grid_z[i + 1, j + 1]) / 4 - min_height
                base_area = (grid_x[i + 1, j] - grid_x[i, j]) * (grid_y[i + 1, j + 1] - grid_y[i + 1, j])
                volume += base_area * height
    return volume

def calculate_surface_area_above_water(grid_x, grid_y, grid_z, water_surface):
    # Flatten the grids to get the points
    points = np.array([grid_x.flatten(), grid_y.flatten(), grid_z.flatten()]).T
    # Use Delaunay triangulation to get the triangles
    tri = Delaunay(points[:,:2])
    triangles = points[tri.simplices]

    surface_area = 0

    # Loop over each triangle
    for triangle in triangles:
        # Check if the triangle is above the water surface
        if all(vertex[2] > water_surface for vertex in triangle):
            # Calculate the area of the triangle using the cross product
            edge1 = triangle[1] - triangle[0]
            edge2 = triangle[2] - triangle[0]
            triangle_area = norm(np.cross(edge1, edge2)) / 2
            surface_area += triangle_area

    return surface_area


def update_volume_info(cavity_volume, water_above_volume, water_below_volume, water_volume, surface_area_above_water):
    # 确保 volume_info 已经在其他地方创建
    global volume_info
    if 'volume_info' in globals():
        volume_info.config(state=tk.NORMAL)
        volume_info.delete(1.0, tk.END)
        volume_info.insert(tk.END, f"Total Cavity Volume: {cavity_volume}\n")
        volume_info.insert(tk.END, f"Water Above Volume: {water_above_volume}\n")
        volume_info.insert(tk.END, f"Water Below Volume: {water_below_volume}\n")
        volume_info.insert(tk.END, f"Water Volume: {water_volume}\n")
        volume_info.insert(tk.END, f"Surface Area Above Water: {surface_area_above_water}\n")
        volume_info.config(state=tk.DISABLED)
    else:
        print("Error: volume_info does not exist. It should be created before calling update_volume_info.")



def calculate_water_above_volume_data(grid_x, grid_y, grid_z):
    min_z_value = np.nanmin(grid_z)
    max_z_value = np.nanmax(grid_z)
    water_levels = np.linspace(0, 1, 10)
    water_above_volume_data = []

    for water_level in water_levels:
        water_surface = (water_level * (max_z_value - min_z_value)) + min_z_value
        water_above_volume = calculate_cavity_volume(grid_x, grid_y, np.where(grid_z > water_surface, grid_z, np.nan))
        water_above_volume_data.append((water_level, water_above_volume))

    return water_above_volume_data


def plot_top_view_of_water(ax, grid_x, grid_y, grid_z, water_surface):
    above_water = np.where(grid_z > water_surface, grid_z, np.nan)
    ax.contourf(grid_x, grid_y, above_water, cmap='viridis')
    if current_language == "Chinese":
        ax.set_title("俯视图：三维模型水上部分")
    else:
        ax.set_title("Top view: 3D-model above water")

    ax.set_xlabel("x")
    ax.set_ylabel("y")

root2 = tk.Tk()  # Create the root window only once outside the function
root2.title("2D Plot")
canvas = None
def generate_plot_fig():
    global fig, canvas, root2
    if canvas:  # If canvas already exists, destroy it to recreate it
        canvas.get_tk_widget().destroy()

    fig = plt.figure(figsize=(10, 10))
    fig.clf()
    fig.subplots_adjust(hspace=0.4)  # 增加子图之间的上下间距

    canvas = FigureCanvasTkAgg(fig, master=root2)
    canvas.get_tk_widget().pack()

    # Call your plotting function
    ax6 = None  # You can change this if needed
    plot_k_function_and_distribution(
        fig, ax6,
        slider_points.get(),
        slider_clusters.get(),
        slider_std.get(),
        slider_min_distance.get(),
        slider_water_level.get()
    )

    root2.mainloop()


def plot_k_function_and_distribution(fig, ax6, num_points, num_clusters, cluster_std, min_distance, water_level):
    global grid_x, grid_y, grid_z, water_above_volume_data, cavity_volume, grid_z_original
    from matplotlib import rcParams
    rcParams['font.family'] = 'SimHei'  # 设置为黑体


    # 获取噪声点的占比
    noise_ratio = slider_noise_ratio.get()

    # 计算噪声点和聚类点的数量
    num_noise_points = int(noise_ratio * num_points)
    num_cluster_points = num_points - num_noise_points

    # 生成聚类中心
    centers = generate_clusters(num_clusters, min_distance)

    # 生成噪声点和聚类点
    noise_points = np.random.uniform(0, 10, (num_noise_points, 2))
    cluster_points, _ = make_blobs(n_samples=num_cluster_points, centers=centers, cluster_std=cluster_std)

    # 合并噪声点和聚类点
    data = np.vstack([noise_points, cluster_points])

    x, y = data[:, 0], data[:, 1]
    x_centers, y_centers = centers[:, 0], centers[:, 1]

    radius = 1.0
    density = np.array([np.sum(np.sqrt(np.sum((data - point) ** 2, axis=1)) < radius) for point in data])

    distances = squareform(pdist(np.column_stack((x, y))))

    distances_to_centers = cdist(np.column_stack((x, y)), centers)
    labels = np.argmin(distances_to_centers, axis=1)

    gdf = gpd.GeoDataFrame({"X": x, "Y": y, "label": labels, "geometry": [Point(xy) for xy in zip(x, y)]})
    gdf["label"] = gdf["label"].astype(float)
    w = weights.Kernel.from_dataframe(gdf, fixed=False, k=15)
    morans_I = esda.moran.Moran(gdf["label"], w)
    morans_lag = weights.lag_spatial(w, gdf["label"])

    grid_x, grid_y = np.mgrid[0:10:100j, 0:10:100j]
    grid_z = griddata((x, y), density, (grid_x, grid_y), method='cubic')
    grid_z_original = np.copy(grid_z)
    cavity_volume = calculate_cavity_volume(grid_x, grid_y, grid_z)

    min_z_value = np.nanmin(grid_z)
    max_z_value = np.nanmax(grid_z)
    water_surface = min_z_value + water_level * (max_z_value - min_z_value)

    # 计算Water Above Volume随着水面上升高度的变化数据
    water_above_volume_data = calculate_water_above_volume_data(grid_x, grid_y, grid_z)

    water_above_volume = calculate_cavity_volume(grid_x, grid_y, np.where(grid_z > water_surface, grid_z, np.nan))
    water_below_volume = cavity_volume - water_above_volume

    water_volume = (100 * water_level * (max_z_value - min_z_value)) - water_below_volume


    # Compute the surface area
    surface_area_above_water = calculate_surface_area_above_water(grid_x, grid_y, grid_z, water_surface)

    update_volume_info(cavity_volume, water_above_volume, water_below_volume, water_volume, surface_area_above_water)

    print("Total Cavity Volume:", round(cavity_volume, 2))
    print("Water Above Volume:", round(water_above_volume, 2))
    print("Water Below Volume:", round(water_below_volume, 2))
    print("Water Volume:", round(water_volume, 2))
    print("surface_area_above_water:", round(surface_area_above_water, 2))

    # fig.clear()  # 这里不需要清除整个figure

    ax1 = fig.add_subplot(221)
    ax1.scatter(x, y, label="Points")
    ax1.scatter(x_centers, y_centers, color='red', label="Centers")
    ax1.set_xlim([0, 10])
    ax1.set_ylim([0, 10])
    ax1.set_aspect('equal', 'box')
    # 根据当前语言设置标题
    if current_language == "Chinese":
        ax1.set_title("点分布")
    else:
        ax1.set_title("Point Distribution")
    ax1.legend()



    def ripley_k(distances, r, area):
        N = distances.shape[0]
        densities = np.sum(distances < r, axis=1) - 1
        return np.sum(densities) / (N * (N - 1) / 2) * area

    r_values = np.linspace(0, np.sqrt(2) * 10, 100)
    area = 10 * 10
    k_values = [ripley_k(distances, r, area) for r in r_values]

    np.random.seed(0)
    num_simulations = 1000
    k_values_simulations = np.empty((num_simulations, len(r_values)))
    for i in range(num_simulations):
        x_sim, y_sim = make_blobs(n_samples=num_points, centers=centers, n_features=2, cluster_std=cluster_std)
        distances_sim = squareform(pdist(np.column_stack((x_sim, y_sim))))
        k_values_simulations[i, :] = [ripley_k(distances_sim, r, area) for r in r_values]

    lower_bound = np.percentile(k_values_simulations, 2.5, axis=0)
    upper_bound = np.percentile(k_values_simulations, 97.5, axis=0)

    ax3 = fig.add_subplot(222)
    ax3.plot(r_values, k_values, label="Ripley's K-function")
    ax3.fill_between(r_values, lower_bound, upper_bound, color='gray', alpha=0.5, label="95% Confidence Interval")
    ax3.set_xlabel("r")
    ax3.set_ylabel("K(r)")
    ax3.legend()
    if current_language == "Chinese":
        ax3.set_title("Ripley的K函数和95%置信区间")
    else:
        ax3.set_title("Ripley's K-function and 95% Confidence Interval")

    # Assuming fig is the main figure you're working with
    ax4 = fig.add_subplot(224)

    # Plot the histogram for x coordinates and get the values
    n, bins, patches = ax4.hist(x, bins=10, range=(0, 10), color='lightblue', edgecolor='black')

    # Set xticks to 0 to 10
    ax4.set_xticks(np.arange(0, 11, 1))

    # Set x limits to ensure that histogram covers the entire range
    ax4.set_xlim(0, 10)

    # Setting grid visibility
    ax4.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Removing top and right borders
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)

    # Setting title and labels
    if current_language == "Chinese":
        ax4.set_title("x轴分布直方图")
    else:
        ax4.set_title("Histogram of x-coordinate Distribution")
    ax4.set_xlabel("x")
    ax4.set_ylabel("Frequency")

    # Add frequency value on top of each bar
    for i in range(10):
        ax4.text(bins[i] + 0.5, n[i] + 0.5, str(int(n[i])), ha='center', va='center', fontsize=10)

    # Assuming fig is the main figure you're working with
    ax2 = fig.add_subplot(223)

    # Plot the histogram for y coordinates and get the values
    n, bins, patches = ax2.hist(y, bins=10, range=(0, 10), orientation='horizontal', color='lightpink',
                                edgecolor='black')

    # Set yticks to 0 to 10
    ax2.set_yticks(np.arange(0, 11, 1))

    # Set y limits to ensure that histogram covers the entire range
    ax2.set_ylim(0, 10)

    # Setting grid visibility
    ax2.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Removing top and right borders
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    # Setting title and labels
    if current_language == "Chinese":
        ax2.set_title("y轴分布直方图")
    else:
        ax2.set_title("Histogram of y-coordinate Distribution")
    ax2.set_xlabel("Frequency")
    ax2.set_ylabel("y")

    # Add frequency value on top of each bar
    for i in range(10):
        ax2.text(n[i] + 0.5, bins[i] + 0.5, str(int(n[i])), ha='center', va='center', fontsize=10)


global root3, canvas2, fig2, ax7, ax8, ax9, first_update
def create_or_update_fig2(water_level):
    global root3, canvas2, fig2, ax7, ax8, ax9
    if 'root3' not in globals():
        root3 = tk.Tk()
        root3.title("3D Plot")
        fig2 = plt.figure(figsize=(10, 10))
        canvas2 = FigureCanvasTkAgg(fig2, master=root3)
        canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        gs = gridspec.GridSpec(2, 2, width_ratios=[1, 1], height_ratios=[2, 1])
        ax7 = fig2.add_subplot(gs[0, :2], projection='3d')
        ax8 = fig2.add_subplot(gs[1, 0])
        ax9 = fig2.add_subplot(gs[1, 1])


    def update_fig2(water_level):
        global root3, canvas2, fig2, ax7, ax8, ax9
        # 清除子图内容
        ax7.clear()
        ax8.clear()
        ax9.clear()

        # 定义中间剖面图的点数
        num_points = 100

        # 找到x=5所对应的索引
        middle_index_x = np.abs(grid_x[0, :] - 5).argmin()

        # 创建y的插值网格
        grid_y_middle = np.linspace(np.min(grid_y), np.max(grid_y), num_points)

        # 获取滑块的值
        slice_x = slider_slice_x.get()
        slice_y = slider_slice_y.get()

        # 获取x=slice_x这个平面上所有点的值
        middle_plane_z_x = griddata((grid_x.flatten(), grid_y.flatten()), grid_z.flatten(), (slice_x, grid_y_middle))

        # 找到y=6所对应的索引
        middle_index_y = np.abs(grid_y[:, 0] - 6).argmin()

        # 创建x的插值网格
        grid_x_middle = np.linspace(np.min(grid_x), np.max(grid_x), num_points)

        # 获取y=slice_y这个平面上所有点的值
        middle_plane_z_y = griddata((grid_x.flatten(), grid_y.flatten()), grid_z.flatten(), (grid_x_middle, slice_y))

        # 创建一个颜色映射对象
        cmap = get_cmap('viridis')

        # 获取z值的范围
        min_z_value = np.nanmin(grid_z)
        max_z_value = np.nanmax(grid_z)

        # 创建一个用于将数据值映射到颜色映射范围的对象
        norm = Normalize(vmin=min_z_value, vmax=max_z_value)

        # 创建一个新的图形窗口
        ax7.plot_surface(grid_x, grid_y, grid_z, cmap='viridis')
        if current_language == "Chinese":
            ax7.set_title("三维模型", pad=0)
        else:
            ax7.set_title("3D-model", pad=0)

        ax7.set_xlabel("x")
        ax7.set_ylabel("y")
        ax7.set_zlabel("z")

        plot_cube(ax7, [0, 0, 0], [10, 10, max_z_value - min_z_value], min_z_value)
        water_surface = (water_level * (max_z_value - min_z_value)) + min_z_value
        ax7.plot_surface(grid_x, grid_y, np.full_like(grid_z, water_surface), color='blue', alpha=0.5)

        density_projection = np.full((grid_x.shape[0], grid_x.shape[1]), min_z_value)
        for i in range(grid_x.shape[0]):
            for j in range(grid_x.shape[1]):
                if not np.isnan(grid_z[i, j]):
                    density_projection[i, j] = grid_z[i, j]

        ax7.plot_surface(grid_x, grid_y, density_projection, alpha=0.4, cmap='Blues', zorder=2)
        ax7.contourf(grid_x, grid_y, density_projection, zdir='z', offset=min_z_value, cmap='viridis', alpha=0.7)

        # 在新的图形窗口中创建第一个子图来展示x=5的剖面图
        ax8.plot(grid_y_middle, middle_plane_z_x, color='red')
        for i in range(len(grid_y_middle) - 1):
            ax8.fill_between(grid_y_middle[i:i + 2], middle_plane_z_x[i:i + 2], min_z_value,
                             color=cmap(norm(middle_plane_z_x[i])))
        ax8.axhline(water_surface, color='blue', linestyle='--')
        if current_language == "Chinese":
            ax8.set_title(f"x = {slice_x}的剖面图")
        else:
            ax8.set_title(f"Cross Section at x = {slice_x}")
        ax8.set_xlabel("y")
        ax8.set_ylabel("z")
        ax8.set_ylim([min_z_value, max_z_value])
        ax8.set_xlim([0, 10])  # 设置横坐标固定范围为0到10

        # 在新的图形窗口中创建第二个子图来展示y=6的剖面图
        ax9.plot(grid_x_middle, middle_plane_z_y, color='red')
        for i in range(len(grid_x_middle) - 1):
            ax9.fill_between(grid_x_middle[i:i + 2], middle_plane_z_y[i:i + 2], min_z_value,
                             color=cmap(norm(middle_plane_z_y[i])))
        ax9.axhline(water_surface, color='blue', linestyle='--')
        if current_language == "Chinese":
            ax9.set_title(f"y = {slice_y}的剖面图")
        else:
            ax9.set_title(f"Cross Section at y = {slice_y}")
        ax9.set_xlabel("x")
        ax9.set_ylabel("z")
        ax9.set_ylim([min_z_value, max_z_value])

    fig2.tight_layout()
    fig2.subplots_adjust(top=0.95)
    canvas2.draw()
    update_fig2(water_level)

    # plot_water_above_volume(ax6, water_above_volume_data)
    canvas.draw()  # 在绘制完成后进行画布的更新


ani = None
fig4 = plt.figure(figsize=(10, 10))
ax6 = fig4.add_subplot(222)
ax10 = fig4.add_subplot(221, projection='3d')
ax11 = fig4.add_subplot(224)
ax5_fig4 = fig4.add_subplot(223)


def animate_water():
    global ani, fig4, ax6, ax10, ax11, ax5_fig4, canvas4, root4

    root4 = tk.Tk()
    root4.title("Water-flooding Method")

    global water_above_volume_data
    global surface_area_data
    water_above_volume_data = []  # Clear the list before starting the animation
    surface_area_data = []
    water_levels = np.linspace(0, 1, 10)

    # 确保在这里只初始化一次 ax5_fig4
    if 'ax5_fig4' not in globals():
        ax5_fig4 = fig4.add_subplot(223)

    ani = FuncAnimation(fig4, update_water_surface, fargs=(ax6, ax10), frames=water_levels, interval=100, repeat=False)
    canvas4 = FigureCanvasTkAgg(fig4, master=root4)
    canvas4.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    canvas4.draw()

    root4.mainloop()


def update_water_surface(water_level, ax6, ax10):
    from matplotlib import rcParams
    rcParams['font.family'] = 'SimHei'  # 设置为黑体
    global grid_x, grid_y, grid_z, grid_z_original
    global water_above_volume_data
    global surface_area_data
    global canvas4
    global ax5_fig4  # 确保使用全局变量

    plot_k_function_and_distribution(fig, ax6, slider_points.get(), slider_clusters.get(), slider_std.get(),
                                     slider_min_distance.get(), water_level)
    min_z_value = np.nanmin(grid_z)
    max_z_value = np.nanmax(grid_z)
    water_surface = (water_level * (max_z_value - min_z_value)) + min_z_value

    if water_level == 0:
        water_above_volume = calculate_cavity_volume(grid_x, grid_y, grid_z_original)  # Use original grid_z
    else:
        water_above_volume = calculate_cavity_volume(grid_x, grid_y, np.where(grid_z > water_surface, grid_z, np.nan))

    # Before appending the new data
    if water_level == 0:
        # Remove existing points in ax6 with x=0
        lines_to_remove = []
        for line in ax6.lines:
            xdata, ydata = line.get_data()
            if len(xdata) == 1 and xdata[0] == 0:
                lines_to_remove.append(line)
        for line in lines_to_remove:
            line.remove()

        # Check and remove any existing entry for water_level = 0 from water_above_volume_data
        water_above_volume_data = [data for data in water_above_volume_data if data[0] != 0]

    # Append this data to water_above_volume_data
    water_above_volume_data.append((water_level, water_above_volume))

    # Prepare data for plotting
    water_above_volume_values = [data[1] for data in water_above_volume_data]
    water_level_values = [data[0] for data in water_above_volume_data]

    # 获取最新的数据点
    current_water_level = water_level_values[-1]
    current_water_volume = water_above_volume_values[-1]

    # 多项式回归
    p = Polynomial.fit(water_level_values, water_above_volume_values, 4)  # 这里的3表示三次多项式
    x_fit = np.linspace(min(water_level_values), current_water_level, 500)
    y_fit = p(x_fit)

    # 仅为最新的数据点添加一个点
    ax6.plot(current_water_level, current_water_volume, 'bo',
             label="Volume" if len(water_above_volume_data) == 1 else "")

    # 清除现有的拟合线
    for line in ax6.lines:
        if line.get_label() == "Fitted Curve":
            line.remove()
            break

    # 使用拟合结果来绘制曲线
    ax6.plot(x_fit, y_fit, 'r-', label="Fitted Curve")
    ax6.set_xlabel("Water Level")
    ax6.set_ylabel("Volume")
    if current_language == "Chinese":
        ax6.set_title("水面之上模型体积")
    else:
        ax6.set_title("3D-model Above Water")

    ax6.legend()

    # 在函数的开始部分计算 surface_area_above_water
    surface_area = calculate_surface_area_above_water(grid_x, grid_y, grid_z, water_surface)

    # 在函数的适当位置存储和绘制这些数据
    if water_level == 0:
        # Remove existing points in ax11 with x=0
        lines_to_remove_ax11 = []
        for line in ax11.lines:
            xdata, ydata = line.get_data()
            if len(xdata) == 1 and xdata[0] == 0:
                lines_to_remove_ax11.append(line)
        for line in lines_to_remove_ax11:
            line.remove()

        # Check and remove any existing entry for water_level = 0 from surface_area_data
        surface_area_data = [data for data in surface_area_data if data[0] != 0]

    # 首先，您可能需要一个全局列表来存储这些数据，就像 water_above_volume_data
    surface_area_data.append((water_level, surface_area))

    # 准备用于绘图的数据
    surface_area_values = [data[1] for data in surface_area_data]
    water_level_values = [data[0] for data in surface_area_data]

    # 获取最新的数据点
    current_water_level = water_level_values[-1]
    current_surface_area = surface_area_values[-1]

    # 使用 ax6 的多项式回归方法
    degree = 4 if len(water_level_values) >= 5 else 2 if len(water_level_values) >= 3 else 1
    try:
        p_surface = Polynomial.fit(water_level_values, surface_area_values, degree)
        x_fit_surface = np.linspace(min(water_level_values), current_water_level, 500)
        y_fit_surface = p_surface(x_fit_surface)
    except np.linalg.LinAlgError:
        # 如果有问题，仅连接点
        x_fit_surface = water_level_values
        y_fit_surface = surface_area_values

    # 仅为最新的数据点添加一个点
    ax11.plot(current_water_level, current_surface_area, 'go',
              label="Surface Area" if len(surface_area_data) == 1 else "")
    # 清除现有的拟合线
    for line in ax11.lines:
        if line.get_label() == "Fitted Curve Surface":
            line.remove()
            break

    # 使用拟合结果来绘制曲线
    ax11.plot(x_fit_surface, y_fit_surface, 'r-', label="Fitted Curve Surface")
    ax11.set_xlabel("Water Level")
    ax11.set_ylabel("Surface Area")
    ax11.set_title("3D-model Above Water")
    ax11.legend()

    ax10.clear()
    ax10.plot_surface(grid_x, grid_y, grid_z, cmap='viridis')
    if current_language == "Chinese":
        ax11.set_title("水面之上模型表面积")
    else:
        ax11.set_title("3D-model Above Water")
    ax10.set_xlabel("x")
    ax10.set_ylabel("y")
    ax10.set_zlabel("z")

    plot_cube(ax10, [0, 0, 0], [10, 10, max_z_value - min_z_value], min_z_value)
    water_surface = (water_level * (max_z_value - min_z_value)) + min_z_value
    ax10.plot_surface(grid_x, grid_y, np.full_like(grid_z, water_surface), color='blue', alpha=0.5)

    density_projection = np.full((grid_x.shape[0], grid_x.shape[1]), min_z_value)
    for i in range(grid_x.shape[0]):
        for j in range(grid_x.shape[1]):
            if not np.isnan(grid_z[i, j]):
                density_projection[i, j] = grid_z[i, j]

    ax10.plot_surface(grid_x, grid_y, density_projection, alpha=0.4, cmap='Blues', zorder=2)
    ax10.contourf(grid_x, grid_y, density_projection, zdir='z', offset=min_z_value, cmap='viridis', alpha=0.7)
    ax10.xaxis.set_tick_params(pad=1)  # 设置X轴刻度标注的距离
    ax10.yaxis.set_tick_params(pad=1)  # 设置Y轴刻度标注的距离
    ax10.zaxis.set_tick_params(pad=1)  # 设置Z轴刻度标注的距离

    # 在 fig4 中绘制与 ax5 相同的内容
    #ax5_fig4 = fig4.add_subplot(223)  # or any other desired position
    ax5_fig4.clear()
    plot_top_view_of_water(ax5_fig4, grid_x, grid_y, grid_z, water_surface)
    canvas4.draw()

from tkinter import Tk, Toplevel, Radiobutton, StringVar
import tkinter as tk

# 初始化翻译器（默认英文）
translator = Translator(language="English")

# 示例函数存根（请根据您实际逻辑修改）
global first_click
first_click = True


def double_update():
    global volume_info, first_click
    # 检查volume_info是否已经创建，如果没有则创建它
    if 'volume_info' not in globals():
        # 创建并放置Text组件
        volume_info = Text(root1, wrap=tk.WORD, width=50, height=5)
        volume_info.place(relx=0.5, rely=1.2, anchor='center')

        # 如果这是第一次点击，我们需要调整窗口大小
        if first_click:
            current_width = root1.winfo_width()
            # 增加窗口高度以适应新的Text组件
            new_height = root1.winfo_height() + 100  # 请根据Text组件的实际高度调整这个值
            root1.geometry(f"{current_width}x{new_height}")

        # 创建并放置Text组件
        volume_info = Text(root1, wrap=tk.WORD, width=40, height=5)
        volume_info.place(relx=0.37, rely=1.0, anchor='se')
    plot_k_function_and_distribution(fig, ax6, slider_points.get(),
                                     slider_clusters.get(), slider_std.get(),
                                     slider_min_distance.get(),
                                     slider_water_level.get())
    create_or_update_fig2(slider_water_level.get())
    if first_click:
        root1.after(500, lambda: plot_k_function_and_distribution(fig, ax6, slider_points.get(),
                                                                  slider_clusters.get(), slider_std.get(),
                                                                  slider_min_distance.get(),
                                                                  slider_water_level.get()))
        first_click = False


# 更新UI文本的函数
def update_texts():
    global current_language
    current_language = translator.language
    """
    在切换语言后，更新界面上所有需要翻译的文本。
    """
    if current_language == "Chinese":
        title_label.config(
            text=translator.translate("“地形-漫水”城市复杂空间演化模拟分析系统"),
            font=("SimHei", 20)  # 黑体 + 字号
        )
    else:
        title_label.config(
            text=translator.translate("Water-flooding Method for Urban 3D-morphology"),
            font=("Arial", 16)  # 默认字体
        )

    # 更新滑块的label并尝试强制刷新显示
    slider_points.config(label=translator.translate("① Number of Points"))
    slider_points.update_idletasks()
    slider_noise_ratio.config(label=translator.translate("② Noise Ratio"))
    slider_noise_ratio.update_idletasks()
    slider_clusters.config(label=translator.translate("③ Number of Clusters"))
    slider_clusters.update_idletasks()
    slider_std.config(label=translator.translate("④ Cluster Standard Deviation"))
    slider_std.update_idletasks()
    slider_min_distance.config(label=translator.translate("⑤ Minimum Distance"))
    slider_min_distance.update_idletasks()
    slider_water_level.config(label=translator.translate("⑥ Water Level"))
    slider_water_level.update_idletasks()
    slider_slice_x.config(label=translator.translate("⑦ X Slice"))
    slider_slice_x.update_idletasks()
    slider_slice_y.config(label=translator.translate("⑧ Y Slice"))
    slider_slice_y.update_idletasks()


    # 更新按钮的文本
    btn_plot_fig.config(text=translator.translate("Step1:Create 2D Plot"))
    button.config(text=translator.translate("Step2:Create 3D Plot"))
    slider_water_level_button.config(text=translator.translate("Step3:Water-flooding Simulation"))
    language_button.config(text=translator.translate("Language"))

# 自定义语言选择窗口
def choose_language():
    """
    打开一个新的Toplevel窗口，使用Radiobutton让用户选择English或简体中文，点击“确定”后更新语言并关闭窗口。
    """
    # 获取按钮在屏幕上的位置
    button_x = language_button.winfo_rootx()
    button_y = language_button.winfo_rooty()

    # 创建语言选择窗口
    lang_window = Toplevel(root1)
    lang_window.title("Choose Language")

    # 设置窗口位置，使其在按钮旁边
    lang_window.geometry(f"220x120+{button_x+language_button.winfo_width()}+{button_y}")

    # 定义变量并设置初始值
    lang_var = StringVar(value="English")

    # Radiobutton 的回调函数
    def set_language(new_lang):
        print(f"Language changed to {new_lang}")
        translator.set_language(new_lang)
        update_texts()

    # 创建 Radiobutton 并绑定变量和回调
    r_english = Radiobutton(lang_window, text="English", variable=lang_var, value="English",
                            command=lambda: set_language("English"))
    r_chinese = Radiobutton(lang_window, text="简体中文", variable=lang_var, value="Chinese",
                            command=lambda: set_language("Chinese"))

    # 设置默认选中 English
    r_english.select()

    # 布局 Radiobutton
    r_english.pack(pady=5)
    r_chinese.pack(pady=5)

    # 保持窗口打开，直到选择语言
    lang_window.mainloop()

# 主界面代码
root1 = tk.Tk()
root1.geometry('800x480')
root1.configure(background='#D3D3D3')  # 设置窗口背景为浅灰色
root1.title("Consol")  # 设置窗口标题


# 创建一个标签用于显示软件名称
title_font = ('Arial', 20, 'bold')
title_label = tk.Label(
    root1,
    text=translator.translate("Water-flooding Method for Urban 3D-morphology"),
    bg='#D3D3D3',
    fg='black',
    font=title_font
)
title_label.place(relx=0.5, rely=0.1, anchor='center')

# 创建框架用于容纳滑块
frame1 = tk.Frame(root1)
frame1.place(relx=0.5, rely=0.25, anchor='center', relwidth=1.0)

frame1.grid_columnconfigure(0, weight=1, minsize=50)
frame1.grid_columnconfigure(4, weight=1, minsize=50)

slider_length = 180

slider_points = tk.Scale(
    frame1, from_=10, to=500, resolution=10,
    orient="horizontal", label=translator.translate("① Number of Points"),
    length=slider_length
)
slider_points.grid(in_=frame1, row=0, column=1, padx=15)
slider_points.set(100)

slider_noise_ratio = tk.Scale(
    frame1, from_=0, to=1, resolution=0.01,
    orient="horizontal", label=translator.translate("② Noise Ratio"),
    length=slider_length
)
slider_noise_ratio.grid(in_=frame1, row=0, column=2, padx=15)
slider_noise_ratio.set(0.5)

slider_clusters = tk.Scale(
    frame1, from_=1, to=10, resolution=1,
    orient="horizontal", label=translator.translate("③ Number of Clusters"),
    length=slider_length
)
slider_clusters.grid(in_=frame1, row=0, column=3, padx=15)
slider_clusters.set(3)

frame2 = tk.Frame(root1)
frame2.place(relx=0.5, rely=0.42, anchor='center', relwidth=1.0)
frame2.grid_columnconfigure(0, weight=1)
frame2.grid_columnconfigure(3, weight=1)

slider_std = tk.Scale(
    frame2, from_=0.1, to=3.0, resolution=0.1,
    orient=tk.HORIZONTAL, label=translator.translate("④ Cluster Standard Deviation"),
    length=slider_length
)
slider_std.grid(in_=frame2, row=0, column=1, padx=15)

slider_min_distance = tk.Scale(
    frame2, from_=0, to=10, resolution=0.1,
    orient=tk.HORIZONTAL, label=translator.translate("⑤ Minimum Distance"),
    length=slider_length
)
slider_min_distance.grid(in_=frame2, row=0, column=2, padx=15)

frame3 = tk.Frame(root1, bg='blue')
frame3.place(relx=0.5, rely=0.55, anchor='center')

frame3.grid_columnconfigure(0, weight=1)
frame3.grid_columnconfigure(2, weight=1)

btn_plot_fig = tk.Button(
    frame3,
    text=translator.translate("Step1:Create 2D Plot"),
    bg='#bac6d6',
    fg='black',
    command=generate_plot_fig
)
btn_plot_fig.grid(row=0, column=1)

# 框架4：水位、X/Y切片滑块
frame4 = tk.Frame(root1)
frame4.place(relx=0.5, rely=0.68, anchor='center', relwidth=1.0)
frame4.grid_columnconfigure(0, weight=1)
frame4.grid_columnconfigure(4, weight=1)

slider_water_level = tk.Scale(
    frame4, from_=0, to=1, resolution=0.01,
    orient=tk.HORIZONTAL, label=translator.translate("⑥ Water Level"),
    sliderlength=30, length=slider_length
)
slider_water_level.grid(row=0, column=1, padx=15)
slider_water_level.set(0)

slider_slice_x = tk.Scale(
    frame4, from_=0.0, to=10.0, resolution=0.1,
    orient=tk.HORIZONTAL, label=translator.translate("⑦ X Slice"),
    length=slider_length
)
slider_slice_x.grid(row=0, column=2, padx=15)
slider_slice_x.set(0)

slider_slice_y = tk.Scale(
    frame4, from_=0.0, to=10.0, resolution=0.1,
    orient=tk.HORIZONTAL, label=translator.translate("⑧ Y Slice"),
    length=slider_length
)
slider_slice_y.grid(row=0, column=3, padx=15)
slider_slice_y.set(0)

# Step3按钮
slider_water_level_button = tk.Button(
    root1,
    text=translator.translate("Step3:Water-flooding Simulation"),
    bg='#bac6d6',
    fg='black',
    command=animate_water
)
slider_water_level_button.place(relx=0.5, rely=0.91, anchor='center')

# Step2按钮
button = tk.Button(
    root1,
    text=translator.translate("Step2:Create 3D Plot"),
    bg='#bac6d6',
    fg='black',
    command=double_update
)
button.place(relx=0.5, rely=0.81, anchor='center')



# Language按钮（自定义对话框）
language_button = tk.Button(
    root1,
    text=translator.translate("Language"),
    command=choose_language
)
language_button.place(relx=0.95, rely=0.95, anchor='se')

root1.mainloop()

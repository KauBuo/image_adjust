import tkinter as tk # tkinter 是一个 Python 的 GUI 库，用于创建图形用户界面
from PIL import Image, ImageTk # PIL 是一个处理图像的库，我们这里用于打开和处理图像
from tkinter import filedialog # filedialog 是 tkinter 中的一个模块，用于创建文件对话框
import cv2 # cv2 是 OpenCV 的 Python 接口，用于实现计算机视觉相关的功能
import numpy as np # numpy 用于科学计算，如图像处理中的各种矩阵操作
import matplotlib.pyplot as plt # matplotlib.pyplot 用于绘图，如直方图等

# matplotlib.backends.backend_tkagg 是 matplotlib 的 tkinter 后端，用于将 matplotlib 的图表嵌入到 tkinter 的 GUI 中
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 定义 load_image 函数，用于载入用户选择的图片
def load_image():
    global img
    filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if not filepath:
        return
    img = Image.open(filepath)
    max_size = 400
    if img.size[0] > max_size or img.size[1] > max_size:
        img.thumbnail((max_size, max_size))
    update_image()

# 定义 update_image 函数，用于更新图片及其直方图
def update_image():
    global img, img_tk, canvas
    if img is None:
        return

    # 调整亮度
    # 使用numpy库将PIL的Image对象转化为numpy数组，然后将数组的数据类型转换为浮点数，以便于进行后续的数学运算。
    img_np = np.array(img).astype(float)
    # 获取滑块的当前值，然后用它乘以图像的每个像素值，以此来调整图像的亮度。
    scale = brightness_scale.get() # 获取滑块当前值
    img_np = img_np * scale 
    # 使用numpy的clip函数将像素值限制在0-255的范围内。
    # 这个操作是必要的，因为在亮度调整过程中，像素值可能会超过这个范围，导致显示错误。
    img_np = np.clip(img_np, 0, 255)  # 防止像素值溢出
    # 将调整亮度后的numpy数组转换回PIL的Image对象，并将数据类型转回uint8，这样才能正常显示图像。
    img_bright = Image.fromarray(img_np.astype(np.uint8))


    # 调整对比度
    # 将调节过亮度的 img_bright 先转为numpy数组，然后再转为灰度图
    img_bright_np = cv2.cvtColor(np.array(img_bright), cv2.COLOR_RGB2GRAY)
    # 创建CLAHE对象，设置对比度限制为从contrast_scale获取的值
    limit = contrast_scale.get() #获取滑块当前值
    clahe = cv2.createCLAHE(clipLimit=limit, tileGridSize=(8,8)) # 创建CLAHE对象
    img_clahe_np = clahe.apply(img_bright_np) # 应用CLAHE对象，确保使用limit调节CLAHE阈值
    # 将numpy数组转换回PIL图像对象
    img_clahe_pil = Image.fromarray(img_clahe_np)

    # 更新图片
    img_tk = ImageTk.PhotoImage(img_clahe_pil)
    image_label.config(image=img_tk)

    # 更新直方图
    fig.clear()
    # 使用plt绘制图像对象直方图，确定其数据范围为0到255，256个区间。
    plt.hist(img_clahe_np.ravel(), bins=256, range=[0, 256])
    plt.xlabel('Pixel range: 0~255')
    plt.ylabel('Pixel count')
    canvas.draw()

# 初始化全局变量
img = None
img_tk = None
canvas = None

# 创建主窗口
root = tk.Tk()

# 创建载入图片按钮
load_button = tk.Button(root, text="Load Image", command=load_image)
load_button.pack()

# 创建图片显示标签
image_label = tk.Label(root)
image_label.pack()

# 创建亮度调节滑块
brightness_scale = tk.Scale(root,  # 这是滑动条将被附加到的Tkinter窗口对象。
                            from_=0.1, # 这是滑动条的最小值，设置为0.1。
                            to=3.0, # 这是滑动条的最大值，设置为3.0。
                            resolution=0.1, # 这是滑动条的步长，设置为0.1。这意味着滑动条会以0.1的增量在0.1到3.0之间移动。
                            label="亮度", # 给滑动条一个标签，这里为"Brightness"，表示它用于调整图像的亮度。
                            orient="horizontal", #  设置滑动条的方向。这里设置为"horizontal"，表示滑动条是水平方向的。
                            command=lambda x: update_image()) # 当滑动条的值发生改变时，这个参数规定了应该执行的函数。
                                                              # 在这里，我们使用了一个lambda函数。
                                                              # 它接受x (滑动条的当前值)并调用`update_image()`函数。
                                                              # `update_image()`函数应该是负责接收滑动条的值并以此来更新显示的图像的亮度。
brightness_scale.set(1.0)
brightness_scale.pack()

# 创建对比度调节滑块
contrast_scale = tk.Scale(root, from_=1.0, to=10.0, resolution=1.0, label="CLAHE clipLimit", orient="horizontal", command=lambda x: update_image())
contrast_scale.set(1.0)
contrast_scale.pack()

# 创建直方图绘图区
fig = plt.figure(figsize=(4, 2))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# 启动主循环
root.mainloop()

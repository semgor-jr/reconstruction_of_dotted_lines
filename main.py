import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import steerable as st
import filter as ft

def navigation(event):
    global present_img
    global images
    global label
    if event.keysym == "Right":
        if present_img < len(images) - 1:
            present_img += 1
    elif event.keysym == "Left":
        if present_img > 0:
            present_img -= 1
    label["image"] = images[present_img]


def close_program():
    root.destroy()


def close_window():
    global final_page
    final_page.destroy()


def save_image(img_contours):
    global present_img
    filepath = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
    if filepath:
        Image.fromarray(img_contours[present_img]).save(filepath)


def validate_input(char):
    return char.isdigit()


def check_start_button():
  global filepath
  if size.get() != "" and angle.get() != "" and iterations.get() != "" and threshold.get() != "" and filepath != "":
    start_button.config(state=tk.NORMAL)
  else:
    start_button.config(state=tk.DISABLED)


def open_file():
  global filepath

  filepath = filedialog.askopenfilename(
    initialdir="/",
    title="Выберите файл",
    filetypes= (("Изображения jpg", "*.jpg"), ("Изображения png", "*.png")))


def reconstruction_start(filepath,
                         method,
                         size_data=19, angle_data=10, iterations_data=10,
                         threshold_data=30):
    global present_img
    global images
    global label
    global img_contours
    global final_page
    final_page = tk.Toplevel(root)
    final_page.title("Результаты реконструкции")

    if method == "Метод 1":
        img_contours = st.open_do_give(filepath, size_data, angle_data, iterations_data)
    elif method == "Метод 2":
        img_contours = ft.open_do_give(filepath, threshold_data)

    for i in range(len(img_contours)):
        images.append(ImageTk.PhotoImage(Image.fromarray(img_contours[i])))

    label = tk.Label(final_page, image=images[0])
    label.pack()
    back_button = tk.Button(final_page, text="Закрыть окно", command=close_window)
    back_button.pack()
    save_button = tk.Button(final_page, text="Сохранить изображение", command=lambda: save_image(img_contours))
    save_button.pack()
    final_page.bind("<Right>", navigation)
    final_page.bind("<Left>", navigation)
    final_page.mainloop()

root = tk.Tk()
root.title("Выбор файла")
present_img = 0
images = []
img_contours = None
label = None
filepath = ""
open_button = tk.Button(root, text="Выбрать изображение", command=open_file)
open_button.pack()

method = tk.StringVar(value="Метод с использованием фильтра")

radio_1 = tk.Radiobutton(root, text="Метод с использованием фильтра", variable=method, value="Метод 1")
radio_1.pack()

radio_2 = tk.Radiobutton(root, text="Метод анализа контуров", variable=method, value="Метод 2")
radio_2.pack()


size_name = tk.Label(root, text='Введите размер ядра:')
size_name.pack()

size = tk.Entry(root, width=10, validate="key", validatecommand=(root.register(validate_input), '%S'))
size.pack()

angle_name = tk.Label(root, text='Введите шаг угла:')
angle_name.pack()
angle = tk.Entry(root, width=10, validate="key", validatecommand=(root.register(validate_input), '%S'))
angle.pack()
angle.bind("<KeyRelease>", lambda event: check_start_button())

iterations_name = tk.Label(root, text='Введите количество итераций:')
iterations_name.pack()
iterations = tk.Entry(root, width=10, validate="key", validatecommand=(root.register(validate_input), '%S'))
iterations.pack()
iterations.bind("<KeyRelease>", lambda event: check_start_button())

threshold_name = tk.Label(root, text='Введите пороговое значение для заполнения разрывов:')
threshold_name.pack()
threshold = tk.Entry(root, width=10, validate="key", validatecommand=(root.register(validate_input), '%S'))
threshold.pack()
threshold.bind("<KeyRelease>", lambda event: check_start_button())

start_button = tk.Button(root, text="Начать реконструкцию",
                         command=lambda: reconstruction_start(filepath,
                                                              method.get(),
                                                              int(size.get()),
                                                              int(angle.get()),
                                                              int(iterations.get()),
                                                              int(threshold.get())),
                         state='disabled')
start_button.pack()


stop_button = tk.Button(root, text="Завершить программу", command=close_program)
stop_button.pack()

root.mainloop()


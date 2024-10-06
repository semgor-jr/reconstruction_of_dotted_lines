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


def save_image():
    global images
    global img_contours
    global present_img
    file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
    if file_path:
        Image.fromarray(img_contours[present_img]).save(file_path)


def validate_input(char):
    return char.isdigit()


def open_file():
  global filepath

  filepath = filedialog.askopenfilename(
    initialdir="/",
    title="Выберите файл",
    filetypes= (("Изображения jpg", "*.jpg"), ("Изображения png", "*.png")))
  if filepath:
      start_button['state'] = 'normal'


def reconstruction_start():
    global filepath
    global present_img
    global images
    global label
    global img_contours
    global final_page
    global size
    global angle
    global iterations
    final_page = tk.Toplevel(root)
    final_page.title("Результаты реконструкции")

    size_data = int(size.get())
    angle_data = int(angle.get())
    iterations_data = int(iterations.get())
    filtered_contours = ft.open_do_give(filepath, 30)
    steerable_filtered_contours = st.open_do_give(filepath, kernel_size=size_data,
                                                  angle=angle_data,
                                                  iterations=iterations_data)

    img_contours = [filtered_contours[0], filtered_contours[1], filtered_contours[2],
                    steerable_filtered_contours[0], steerable_filtered_contours[1]]

    for i in range(len(img_contours)):
        images.append(ImageTk.PhotoImage(Image.fromarray(img_contours[i])))

    label = tk.Label(final_page, image=images[0])
    label.pack()
    back_button = tk.Button(final_page, text="Закрыть окно", command=close_window)
    back_button.pack()
    save_button = tk.Button(final_page, text="Сохранить изображение", command=save_image)
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

start_button = tk.Button(root, text="Начать реконструкцию", command=reconstruction_start, state='disabled')
start_button.pack()

stop_button = tk.Button(root, text="Завершить программу", command=close_program)
stop_button.pack()


size_name = tk.Label(root, text='Введите размер ядра:')
size_name.pack()

size = tk.Entry(root, width=10, validate="key", validatecommand=(root.register(validate_input), '%S'))
size.pack()

angle_name = tk.Label(root, text='Введите шаг угла:')
angle_name.pack()

angle = tk.Entry(root, width=10, validate="key", validatecommand=(root.register(validate_input), '%S'))
angle.pack()

iterations_name = tk.Label(root, text='Введите количество итераций:')
iterations_name.pack()

iterations = tk.Entry(root, width=10, validate="key", validatecommand=(root.register(validate_input), '%S'))
iterations.pack()


root.mainloop()


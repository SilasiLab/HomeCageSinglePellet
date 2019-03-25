from tkinter import *
from tkinter import filedialog, simpledialog
import deeplabcut
import yaml
import multiprocessing
import time
import os
import shutil

class Window:
    def __init__(self):
        self.name_of_project = None
        self.video_list = []
        self.experimenter = 'Mackenzie'
        self.path_config_file = None
        self.working_directory = None
        self.body_parts = []
        self.start_window()
        self.analyse_directory = None
        self.generate_labeled_video = False
        self.buffer_size=30


    def start_window(self):
        window = Tk()

        window.title("Deeplabcut project helper")

        window.geometry('400x200')

        def clicked_create():
            self.select_working_directory(window)
            window.destroy()
            self.get_window_for_project_name()
            self.path_config_file = deeplabcut.create_new_project(self.name_of_project, self.experimenter, self.video_list,
                                                             working_directory=self.working_directory,
                                                             copy_videos=True)
            self.select_body_parts()
            self.add_new_videos()
            print(self.video_list)
            if len(self.video_list) > 0:
                deeplabcut.add_new_videos(self.path_config_file, self.video_list, copy_videos=True)
                deeplabcut.extract_frames(self.path_config_file, 'automatic', 'kmeans', checkcropping=False, crop=True)

            self.working_window_for_deeplabcut()

        btn1 = Button(window, text="create a new project", command=clicked_create)

        btn1.grid(column=1, row=1)

        def clicked_add():

            self.load_an_exsiting_project(window)
            window.destroy()
            self.select_body_parts()
            self.add_new_videos()
            # for item in self.video_list:
            #     if len(item) < 2:
            #         self.video_list.remove(item)
            print(self.video_list)
            if len(self.video_list) > 0:
                deeplabcut.add_new_videos(self.path_config_file, self.video_list, copy_videos=True)
                deeplabcut.extract_frames(self.path_config_file,'automatic', 'kmeans', checkcropping=False, crop=True)

            self.working_window_for_deeplabcut()

        btn2 = Button(window, text="add new videos to a existing project", command=clicked_add)

        btn2.grid(column=1, row=2)

        def download_file(my_download_flag, my_download_list):

            my_download_flag = True
            for file_name in self.video_list:
                attribute_list = file_name.split('/')
                root_index = attribute_list.index("AnimalProfiles")
                mouse_name = attribute_list[root_index + 1]
                video_name = attribute_list[root_index + 3]
                if not os.path.exists(os.path.join(self.analyse_directory, mouse_name)):
                    os.mkdir(os.path.join(self.analyse_directory, mouse_name))

                video_directory = os.path.join(self.analyse_directory, mouse_name, video_name.split('.')[0])
                if not os.path.exists(video_directory):
                    os.mkdir(video_directory)
                shutil.copy(file_name, video_directory)

                video_directory = os.path.join(video_directory, file_name.split('/')[-1])
                print(video_directory)
                my_download_list.append(video_directory)
                while len(my_download_list) >= self.buffer_size:
                    time.sleep(1)
            my_download_flag = False

        def anaslyse_deeplabcut(my_download_flag, my_download_list):

            time.sleep(2)
            print(my_download_flag)
            while my_download_flag or len(my_download_list) > 0:
                if len(my_download_list) > 0:
                    directory = my_download_list[0]
                    # print(directory)
                    if os.path.exists(directory):
                        deeplabcut.analyze_videos(self.path_config_file, [directory], save_as_csv=True)
                        if self.generate_labeled_video:
                            deeplabcut.create_labeled_video(self.path_config_file, [directory])
                        os.remove(directory)
                        my_download_list.remove(directory)

        def clicked_analyse():

            self.load_an_exsiting_project(window)
            self.select_analyse_directory(window)
            window.destroy()
            self.add_new_videos()
            assert len(self.video_list) > 0
            manager = multiprocessing.Manager()
            my_download_flag = manager.Value("b", True)
            my_download_list = manager.list()

            p1 = multiprocessing.Process(target=download_file, args=[my_download_flag, my_download_list])
            p2 = multiprocessing.Process(target=anaslyse_deeplabcut, args=[my_download_flag, my_download_list])
            p1.start()
            p2.start()
            p1.join()
            p2.join()

        def radiobutton_generate():
            self.generate_labeled_video = True
        def radiobutton_off():
            self.generate_labeled_video = False

        btn3 = Button(window, text="Analyse videos", command=clicked_analyse)

        btn3.grid(column=1, row=3)

        frame = Frame()

        v = BooleanVar()
        v.set(False)

        Radiobutton(frame, variable=v, value=1, text="Generate Labeled Video (Select a few to test plz)", command=radiobutton_generate).pack()
        Radiobutton(frame, variable=v, value=2, text="Without Labeled Video", command=radiobutton_off).pack()

        frame.grid(column=1, row=4)
        window.mainloop()




    def get_window_for_project_name(self):
        window = Tk()

        window.title("Deeplabcut new project")

        window.geometry('500x100')

        lbl = Label(window, text="Please input name of your new project")

        lbl.grid(column=0, row=0)

        txt = Entry(window, width=30)

        txt.grid(column=0, row=1)

        def clicked():
            print(txt.get())
            if txt.get():
                self.name_of_project = txt.get()
                window.destroy()


        btn = Button(window, text="Confirm", command=clicked)

        btn.grid(column=1, row=1)

        window.mainloop()



    def load_an_exsiting_project(self, window):
        self.path_config_file = filedialog.askopenfilename(initialdir="/home/", title="Select config file",
                                              filetypes=(("Deeplabcut config file", "*.yaml"), ("all files", "*.*")), parent=window)
        with open(self.path_config_file, 'r') as stream:
            data_loaded = yaml.load(stream)
        self.name_of_project = data_loaded['Task']

    def add_new_videos(self):
        window = Tk()

        window.title("Adding Videos (Project: %s)"%self.name_of_project)

        window.geometry('1200x1000')
        list_frame = Frame(window)
        list_frame.grid(column=0, row=0)

        lsb = Listbox(list_frame, width=150, height=60)
        lsb.pack()
        self.init_filename = "/mnt/"

        def clicked_add():
            print(self.init_filename)
            filename_list = filedialog.askopenfilenames(initialdir=self.init_filename, title="Select video files")
            filename_list = list(filename_list)
            for filename in filename_list:
                lsb.insert(END, filename)
                length = len(filename.split('/'))
                self.init_filename = "/"
                for items in range(0, length-1):
                    self.init_filename += filename.split('/')[items]
                    self.init_filename += "/"
                self.video_list.append(filename)

        def clicked_delete():
            index = lsb.curselection()
            print(index)
            print(lsb.get(index[0]))
            if lsb.get(index[0]) in self.video_list:
                self.video_list.remove(lsb.get(index[0]))
            lsb.delete(index[0], index[0])

        def clicked_confirm():
            window.destroy()

        button_frame = Frame(window)
        button_frame.grid(column=0, row=1)

        btn_add = Button(button_frame, text="add", command=clicked_add)
        btn_add.pack(side=RIGHT)

        btn_delete = Button(button_frame, text="delete", command=clicked_delete)
        btn_delete.pack(side=RIGHT)

        btn_confirm = Button(button_frame, text="confirm", command=clicked_confirm)
        btn_confirm.pack(side=RIGHT)

        window.mainloop()


    def select_working_directory(self, window):
        self.working_directory = filedialog.askdirectory(title="select working directory", parent=window)

    def select_analyse_directory(self, window):
        self.analyse_directory = filedialog.askdirectory(title="select directory to save analysed result", parent=window)

    def select_body_parts(self):

        window = Tk()

        window.title("Selecting body parts (Project: %s)" % self.name_of_project)

        window.geometry('1200x1000')

        with open(self.path_config_file, 'r') as stream:
            data_loaded = yaml.load(stream)

        self.body_parts = data_loaded['bodyparts']
        list_frame = Frame(window)
        list_frame.grid(column=0, row=0)
        lsb = Listbox(list_frame, width=150, height=60)
        lsb.pack()
        for item in self.body_parts:
            lsb.insert(END, item)

        def clicked_add():
            answer = simpledialog.askstring("Input the name of a body part", "Input a name of a body part",
                                            parent=window)

            lsb.insert(END, answer)
            self.body_parts.append(answer)

        def clicked_delete():
            index = lsb.curselection()
            if lsb.get(index[0]) in self.body_parts:
                self.body_parts.remove(lsb.get(index[0]))
            lsb.delete(index[0], index[0])

        def clicked_confirm():
            if len(self.body_parts) > 0:
                data_loaded['bodyparts'] = self.body_parts
                with open(self.path_config_file, 'w') as outfile:
                    yaml.dump(data_loaded, outfile, default_flow_style=False)
            window.destroy()

        button_frame = Frame(window)
        button_frame.grid(column=0, row=1)

        btn_add = Button(button_frame, text="add", command=clicked_add)
        btn_add.pack(side=RIGHT)

        btn_delete = Button(button_frame, text="delete", command=clicked_delete)
        btn_delete.pack(side=RIGHT)

        btn_confirm = Button(button_frame, text="confirm", command=clicked_confirm)
        btn_confirm.pack(side=RIGHT)

        window.mainloop()

    def working_window_for_deeplabcut(self):
        window = Tk()
        window.title("working place (Project: %s)" % self.name_of_project)

        window.geometry('500x500')


        def clicked_label():
            deeplabcut.label_frames(self.path_config_file)

        def clicked_check():
            deeplabcut.check_labels(self.path_config_file)

        def clicked_creat_dataset():
            deeplabcut.create_training_dataset(self.path_config_file)

        def clicked_train_network():
            max_iter = int(entry.get())
            print("max Iter", max_iter)
            deeplabcut.train_network(self.path_config_file, maxiters=max_iter)

        frame = Frame()
        Label(frame, text="max iterations").pack()
        entry = Entry(frame).pack

        btn_label = Button(window, text="1.labele frames", command=clicked_label)
        btn_label.grid(column=0, row=0)
        btn_check = Button(window, text="2.check", command=clicked_check)
        btn_check.grid(column=0, row=1)

        btn_create = Button(window, text="3.create training set", command=clicked_creat_dataset)
        btn_create.grid(column=1, row=0)
        Button(frame, text="4.train", command=clicked_train_network).pack()
        frame.grid(column=1, row=1)

        window.mainloop()


if __name__ == '__main__':
    w = Window()



import backend_timer as ti
import backend_task as db
from threading import Thread, Event
from tkinter import *
from tkinter import ttk
from tkinter.font import Font
from PIL import ImageTk, Image

class Main:
    def __init__(self):
        self.timer = ti.Timer(0,0)
        self.count = 0
        #Raiz del programa
        self.root = Tk()
        self.root.title("Pomodoro Timer - By Baldini & Jopia")
        #self.root.geometry("800x600")
        self.root.wm_state('zoomed')
        self.root.wm_attributes('-transparentcolor','grey')
        self.root.resizable(True, False)
        #vuelvo propiedad el frame para añadir datos pero no la inicializo sin ningun valor
        self.add_data_frame = None
        self.edit_data_frame = None
        self.table = None
        self.add_data_name_input = None
        self.add_data_description_input = None
        self.count_records = None
        self.edit_data_name_input = None
        self.edit_data_description_input = None
        #--------------------------  conectar a la base de datos  --------------------------
        self.db_tasks = db.Database()

        #--------------------------                               -------------------------- 

        #------------------ ejemplo del array para insertar a la tabla hardcodeado ------------------
        self.example_task_name = ['Trabajo', 'Estudio','Comida']
        self.example_task_description = ['Llegar al trabajo antes de las 7 am', 'Estudiar a las 8 pm','Preparar comida al mediodia']
        #------------------                                                        ------------------
        #  Abre la imagen
        cross_img = Image.open("images/cross.png").resize((25,25))
        background_img = Image.open("images/pomodoro.png")

        # Crea una instancia de PhotoImage
        self.cross_img_tk = ImageTk.PhotoImage(cross_img)
        self.background_img_tk = ImageTk.PhotoImage(background_img)

        self.root.iconphoto(False,self.background_img_tk)

        # variables
        self.show_add_frame = BooleanVar()
        self.show_edit_frame = BooleanVar()
        self.delete_boolean = BooleanVar()
        self.completed_boolean = BooleanVar()
        self.edit_boolean = BooleanVar()

        #Estilos
        self.color_obscure = "#a11b36"
        self.timer_color = "#7a092e"
        self.color_vivid = "#d62d2d"
        self.color_orange = "#fc4830"
        #Estilo de tabla
        self.tableStyle = ttk.Style()
        self.tableStyle.theme_use("clam")
        self.tableStyle.configure("Treeview",
                                   background="#a11b36",#fondo de la fila
                                   foreground="white",#borde de la tabla
                                   rowheight= 55, #tamaño de las filas
                                   fieldbackground= "#a11b36",#cambia color debajo de las filas 
                                   bordercolor= "white", 
                                   borderwidth=0)
        #cambia color al seleccionar
        self.tableStyle.map('Treeview', background=[('selected', '#fc3d3d')])
        
        #color del encabezado
        self.tableStyle.configure("Treeview.Heading",
                            background="#a11b36",
                            foreground="white",
                            relief="flat")
        self.tableStyle.map("Treeview.Heading",
                      background=[('active', '#fc3d3d')])

        #estilo de la scrollbar de la tabla
        self.scrollbarStyle = ttk.Style()
        self.scrollbarStyle.configure("arrowless.Vertical.TScrollbar", troughcolor="fc3d3d")

        #SideBar
        self.sidebarFrame = Frame(self.root)
        self.sidebarFrame.config(bg=self.color_obscure)
        self.sidebarFrame.pack(padx=0, pady=0, fill=Y, side="left")

        self.big_font = Font(family='Helvetica', size=103, weight='bold')
        self.medium_font = Font(family='Helvetica', size=20, weight='bold')
        self.small_font = Font(family='Helvetica', size=15, weight='bold')

        self.navbarButton1 = Button(self.sidebarFrame,
                                    text="Timer",
                                    font=self.small_font,
                                    height=4, width=10,
                                    bg=self.color_vivid,
                                    fg="white",
                                    borderwidth=0,
                                    command=lambda: self.change_tabs("timer"))
        self.navbarButton1.grid(row=0, column=0, padx=5, pady=10)
        self.navbarButton2 = Button(self.sidebarFrame,
                                    text="Task",
                                    font=self.small_font,
                                    height=4, width=10,
                                    bg=self.color_vivid,
                                    fg="white",
                                    borderwidth=0,
                                    command=lambda: self.change_tabs("task"))
        self.navbarButton2.grid(row=1, column=0, padx=5, pady=10)

        #Frame Principal
        self.app_main_frame = Frame(self.root, bg=self.color_vivid)
        self.app_main_frame.pack(side="left", fill=BOTH, expand=True)

        #------------------- imagen de fondo -------------------
        self.background_img_label = Label(self.app_main_frame, image=self.background_img_tk,bg=self.color_vivid)
        self.background_img_label.place(x= 600, y= -100, relwidth= 1, relheight= 2)

        #-------------------                 -------------------

        self.incompleted_tasks = []
        self.incom_task_num = 0

        self.pomodoro_value = [0, 0]
        self.descanso_value = [0, 0]
        self.descansolargo_value = [0, 0]

        self.ciclos_a_repetir = 0
        self.ciclos_counter = 1

        self.draw_timer_frame()

        self.root.mainloop()

    
    def change_tabs(self, value):
        self.destroy_main_frame_children()

        if value == "timer":
            self.draw_timer_frame()
        else:
            self.draw_task_frame()


    def destroy_main_frame_children(self):
        for widgets in self.app_main_frame.winfo_children():
            widgets.destroy()

    
    def previous_actual_task(self):
        if self.incom_task_num - 1 >= 0:
            self.incom_task_num -= 1
        self.currentTaskLabel.config(text=self.incompleted_tasks[self.incom_task_num].name)
        self.descriptionLabel.config(text=self.incompleted_tasks[self.incom_task_num].description)


    def next_actual_task(self):
        if self.incom_task_num + 1 < len(self.incompleted_tasks):
            self.incom_task_num += 1
        self.currentTaskLabel.config(text=self.incompleted_tasks[self.incom_task_num].name)
        self.descriptionLabel.config(text=self.incompleted_tasks[self.incom_task_num].description)


    def draw_timer_frame(self):
        #------------------- imagen de fondo -------------------
        self.background_img_label = Label(self.app_main_frame, image=self.background_img_tk,bg=self.color_vivid)
        self.background_img_label.place(x= 600, y= -100, relwidth= 1, relheight= 2)
        #-------------------                 -------------------

        self.incompleted_tasks = self.db_tasks.get_incompleted_tasks()

        self.innetTaskFrame = Frame(self.app_main_frame)
        self.innetTaskFrame.config(bg=self.color_obscure)
        self.innetTaskFrame.pack(pady=100)

        self.taskFrame = Frame(self.innetTaskFrame,width="200",height="350")
        self.taskFrame.config(bg=self.color_obscure)
        self.taskFrame.pack(pady=10)

        self.innTaskFrame = Frame(self.innetTaskFrame)
        self.innTaskFrame.config(bg=self.timer_color)
        self.innTaskFrame.pack()

        self.buttonsFrame = Frame(self.innTaskFrame)
        self.buttonsFrame.config(bg=self.color_obscure)
        self.buttonsFrame.pack()

        self.timerFrame = Frame(self.innTaskFrame)
        self.timerFrame.config(bg=self.timer_color)
        self.timerFrame.pack()

        self.taskLabel = Label(self.taskFrame, bg=self.color_obscure, fg="white", font=self.small_font, width=20, justify='center', text="Tarea Actual")
        self.taskLabel.grid(row=0, column=2, padx=10, pady=10)

        self.currentTaskLabel = Label(self.taskFrame, bg=self.color_vivid, fg="white", font=self.medium_font, width=20, justify='center',
                                      text=self.incompleted_tasks[self.incom_task_num].name)
        self.currentTaskLabel.grid(row=1, column=2, padx=10, pady=10)

        self.previousButton = Button(self.taskFrame, bg=self.color_orange, fg="white", text="<", font=self.medium_font,
                                     borderwidth=0, command=lambda: self.previous_actual_task())
        self.nextButton = Button(self.taskFrame, bg=self.color_orange, fg="white", text=">", font=self.medium_font,
                                 borderwidth=0, command=lambda: self.next_actual_task())

        self.previousButton.grid(row=1, column=1, padx=10, pady=10)
        self.nextButton.grid(row=1, column=3, padx=10, pady=10)

        self.description = StringVar()
        self.descriptionLabel = Label(self.taskFrame, bg=self.color_vivid, fg="white", font=self.small_font, width=30 ,
                                      text=self.incompleted_tasks[self.incom_task_num].description)
        self.descriptionLabel.grid(row=2, column=2, padx=10, pady=10)

        self.pomodoroButtonActived = True
        self.pomodoroButton = Button(self.buttonsFrame, bg=self.timer_color, fg="white", borderwidth=0,
                                     width=15,
                                 text="Pomodoro", font=self.small_font,
                                 command=lambda: self.timerButtons("pomodoro"))

        self.breakButtonActived = False
        self.breakButton = Button(self.buttonsFrame, bg=self.color_obscure, fg="white", borderwidth=0,
                                  width=15,
                                   text="Descanso", font=self.small_font,
                                   command=lambda: self.timerButtons("descanso"))

        self.longButtonActived = False
        self.longBreakButton = Button(self.buttonsFrame, bg=self.color_obscure, fg="white", borderwidth=0,
                                      width=15,
                                       text="Descanso largo", font=self.small_font,
                                       command=lambda: self.timerButtons("largo"))

        self.pomodoroButton.grid(row=0, column=0)
        self.breakButton.grid(row=0, column=1)
        self.longBreakButton.grid(row=0, column=2)

        self.stringEntryOne = StringVar()
        self.stringEntryOne.set("0")
        self.timerEntryOne = Entry(self.timerFrame, bg=self.timer_color, fg="white", font=self.big_font, width=2, justify='center',
                                   borderwidth=0, textvariable=self.stringEntryOne, validate="key")
        self.timerEntryOne['validatecommand'] = (self.timerEntryOne.register(self.testVal),'%P','%d')
        self.timerEntryOne.grid(row=0, column=0, padx=10, pady=10)

        self.timerLabel = Label(self.timerFrame, bg=self.timer_color, fg="white", font=self.big_font, justify='center', text=":")
        self.timerLabel.grid(row=0, column=1)
        
        self.stringEntryTwo = StringVar()
        self.stringEntryTwo.set("0")
        self.timerEntryTwo = Entry(self.timerFrame, bg=self.timer_color, fg="white", font=self.big_font, width=2, justify='center',
                                   borderwidth=0, textvariable=self.stringEntryTwo, validate="key")
        self.timerEntryTwo['validatecommand'] = (self.timerEntryTwo.register(self.testVal),'%P','%d')
        self.timerEntryTwo.grid(row=0, column=2)

        self.ciclosLabelOne = Label(self.timerFrame, bg=self.timer_color, fg="white", font=self.small_font,
                                    justify='center', text="ciclos a repetir:")
        self.ciclosLabelOne.grid(row=1, column=0)

        self.ciclosEntry = Entry(self.timerFrame, bg=self.timer_color, fg="white", font=self.small_font, width=2, justify='center',
                                   borderwidth=0, validate="key")
        self.ciclosEntry['validatecommand'] = (self.timerEntryOne.register(self.testVal),'%P','%d')
        self.ciclosEntry.grid(row=1, column=1)
        self.ciclosEntry.insert(0, 4)

        self.ciclosLabelTwo = Label(self.timerFrame, bg=self.timer_color, fg="white", font=self.small_font,
                                    justify='center', text="ciclos")
        self.ciclosLabelTwo.grid(row=1, column=2)

        self.startButton = Button(self.timerFrame, text="Empezar", font=self.small_font, width=15,
                                   bg=self.color_orange, fg="white", borderwidth=0,
                                 command=lambda: self.start_timer())
        self.startButton.grid(row=2, column=0, pady=10)
        self.stopButton = Button(self.timerFrame, text="Stop", font=self.small_font, width=15,
                                   bg=self.color_orange, fg="white", borderwidth=0,
                                   command=lambda: self.stop_timer())
        self.stopButton.grid(row=2, column=2)


    def timerButtons(self, value):
        if value == "pomodoro" and self.pomodoroButtonActived:
            self.pomodoro_value = [self.timerEntryOne.get(), self.timerEntryTwo.get()]

        elif value == "pomodoro" and not self.pomodoroButtonActived:
            if self.breakButtonActived:
                self.descanso_value = [self.timerEntryOne.get(), self.timerEntryTwo.get()]
            elif self.longButtonActived:
                self.descansolargo_value = [self.timerEntryOne.get(), self.timerEntryTwo.get()]

            self.pomodoroButton.config(bg=self.timer_color)
            self.breakButton.config(bg=self.color_obscure)
            self.longBreakButton.config(bg=self.color_obscure)

            self.timerEntryOne.delete(0, END)
            self.timerEntryTwo.delete(0, END)

            self.timerEntryOne.insert(0, self.pomodoro_value[0])
            self.timerEntryTwo.insert(0, self.pomodoro_value[1])

            self.pomodoroButtonActived = True
            self.breakButtonActived = False
            self.longButtonActived = False

        elif value == "descanso" and not self.breakButtonActived:
            if self.pomodoroButtonActived:
                self.pomodoro_value = [self.timerEntryOne.get(), self.timerEntryTwo.get()]
            elif self.longButtonActived:
                self.descansolargo_value = [self.timerEntryOne.get(), self.timerEntryTwo.get()]

            self.pomodoroButton.config(bg=self.color_obscure)
            self.breakButton.config(bg=self.timer_color)
            self.longBreakButton.config(bg=self.color_obscure)

            self.timerEntryOne.delete(0, END)
            self.timerEntryTwo.delete(0, END)

            self.timerEntryOne.insert(0, self.descanso_value[0])
            self.timerEntryTwo.insert(0, self.descanso_value[1])

            self.pomodoroButtonActived = False
            self.breakButtonActived = True
            self.longButtonActived = False

        elif value == "largo" and not self.longButtonActived:
            if self.pomodoroButtonActived:
                self.pomodoro_value = [self.timerEntryOne.get(), self.timerEntryTwo.get()]
            elif self.breakButtonActived:
                self.descanso_value = [self.timerEntryOne.get(), self.timerEntryTwo.get()]

            self.pomodoroButton.config(bg=self.color_obscure)
            self.breakButton.config(bg=self.color_obscure)
            self.longBreakButton.config(bg=self.timer_color)

            self.timerEntryOne.delete(0, END)
            self.timerEntryTwo.delete(0, END)

            self.timerEntryOne.insert(0, self.descansolargo_value[0])
            self.timerEntryTwo.insert(0, self.descansolargo_value[1])

            self.pomodoroButtonActived = False
            self.breakButtonActived = False
            self.longButtonActived = True


    def testVal(self, inStr, acttyp):
        if acttyp == '1': #insert
            if not inStr.isdigit() or len(inStr) > 2:
                return False
        return True

    def execute_timer(self):
        self.timer.play()

    def cambiar_ciclo(self):
        self.ciclos_a_repetir = self.ciclosEntry.get()
        minuteP, secondP = self.pomodoro_value[0], self.pomodoro_value[1]
        minuteB, secondB = self.descanso_value[0], self.descanso_value[1]
        minuteL, secondL = self.descansolargo_value[0], self.descansolargo_value[1]

        if not (self.ciclos_counter % 2) == 0 or self.ciclos_counter == 0:
            self.timer.set_time(int(minuteP), int(secondP))
        else:
            self.timer.set_time(int(minuteB), int(secondB))

        if (self.ciclos_counter % int(self.ciclos_a_repetir)) == 0 and self.ciclos_counter != 0:
            self.timer.set_time(int(minuteL), int(secondL))
        Thread(target=self.execute_timer).start()

    def change_numbers_front(self):
        self.startButton["state"] = "disabled"
        self.pomodoroButton["state"] = "disabled"
        self.breakButton["state"] = "disabled"
        self.longBreakButton["state"] = "disabled"

        actual_time = self.timer.get_actual_time()

        while True and not self.eventTimer:
            self.stringEntryOne.set(f'{actual_time[0]}')
            self.stringEntryTwo.set(f'{actual_time[1]}')
            actual_time = self.timer.get_actual_time()

            if actual_time == [0, 0]:
                self.ciclos_counter += 1
                self.cambiar_ciclo()

        self.startButton["state"] = "normal"
        self.pomodoroButton["state"] = "normal"
        self.breakButton["state"] = "normal"
        self.longBreakButton["state"] = "normal"


    def start_timer(self):
        self.eventTimer = False
        self.timerButtons("pomodoro")
        
        self.cambiar_ciclo()

        self.thread_execution_front = Thread(target=self.change_numbers_front)
        self.thread_execution_front.start()

    
    def stop_timer(self):
        self.timer.pause()
        self.eventTimer = True
        self.startButton["state"] = "normal"
        self.pomodoroButton["state"] = "normal"
        self.breakButton["state"] = "normal"
        self.longBreakButton["state"] = "normal"


    def change_data_frame(self, boolean_value, parent_widget, value): #entra la variable con valor booleano a la funcion y valor para abrir
    #                                                                 algun widget en especifico

        get_focused_item = self.table.focus()

        if boolean_value.get() is False: # si la var es falsa, llamara a la funcion para mostrar el widget 
             if value == "add" and self.show_edit_frame.get() is False:
                self.show_input_data()
                boolean_value.set(True)
             elif value == "edit" and self.show_add_frame.get() is False and get_focused_item != "":
                self.show_edit_input_data()
                boolean_value.set(True)
             
        else: # en caso contrario, si es true este oculta el widget
            parent_widget.pack_forget()
            boolean_value.set(False)
    

    #-------------  Agregar datos al presionar el boton añadir ------------- 
    def show_input_data(self):
        #frame principal
        self.add_data_frame = Frame(self.app_main_frame,width="200",height="550")
        self.add_data_frame.config(bg=self.color_obscure)
        self.add_data_frame.pack(side=LEFT, padx= 10 , pady= 10)


        #frame image
        img_frame = Frame(self.add_data_frame)
        img_frame.config(bg=self.color_vivid)
        img_frame.pack(side=LEFT)
        img_frame.grid(row=0, column=1, sticky=W, padx= 10 , pady= 10)

        #labels del titulo
        add_data_label_title = Label(self.add_data_frame, font=self.small_font,
                                      bg=self.color_obscure, fg="white",
                                     width=22, justify='center', text="Añadir Tarea ") 
        add_data_label_title.grid(row=0, column=0, padx= 10 , pady= 10, sticky=E)

        #se inserta la imagen en una label
        button_img = Button(img_frame,
                            image = self.cross_img_tk,
                            bg=self.color_orange, fg="white", borderwidth=0,
                            command=lambda: self.change_data_frame(self.show_add_frame, self.add_data_frame, "add"))
        button_img.grid(row=0, column=1)

        #frame del formulario
        form_frame = Frame(self.add_data_frame)
        form_frame.config(bg=self.color_obscure)
        form_frame.grid(row=1, column=0)
        
        #labels e inputs del form
        nameLabel = Label(form_frame, font=self.small_font, width=10,
                          bg=self.color_obscure, fg="white", justify='center', text="Nombre: ")
        nameLabel.grid(row=1, column=0, padx= 10 , pady= 10)

        self.add_data_name_input = Entry(form_frame, font=self.small_font, width=15, justify='center')
        self.add_data_name_input.grid(row=1, column=1 , padx= 10 , pady= 10)
        descriptionLabel = Label(form_frame, font=self.small_font,
                                 bg=self.color_obscure, fg="white",
                                 width=10, justify='center', text="Descripcion: ")
        descriptionLabel.grid(row=2, column=0, padx= 10 , pady= 10)

        self.add_data_description_input = Entry(form_frame, font=self.small_font, width=15, justify='center')
        self.add_data_description_input.grid(row=2, column=1,  padx= 10 , pady= 10)

        #boton de enviar

        add_data_button = Button(form_frame,
                                  bg=self.color_orange, fg="white", borderwidth=0,
                            command=lambda:self.add_data(), 
                            text="Enviar",
                            font=self.small_font,
                            width=12)
        add_data_button.grid(row=3, column=1,  padx= 10 , pady= 10)
       
    # Seleccionar Registro
    def select_record(self,event):
        # Limpia los campos
        self.edit_data_name_input.delete(0, END)
        self.edit_data_description_input.delete(0, END)

        # Agarra el numero el id del registro
        selected = self.table.focus()
        # agarra los valores del registro
        values = self.table.item(selected, 'values')

        # muestra los valores seleccionados en la caja
        self.edit_data_name_input.insert(0, values[0])
        self.edit_data_description_input.insert(0, values[1])
    

    #-------------  Editar datos al presionar el boton añadir ------------- 
    def show_edit_input_data(self):
        self.edit_data_frame = Frame(self.app_main_frame,width="200",height="550")
        self.edit_data_frame.config(bg=self.color_obscure)
        self.edit_data_frame.pack(side=LEFT, padx= 10 , pady= 10)

        #frame image
        img_frame = Frame(self.edit_data_frame)
        img_frame.config(bg=self.color_vivid)
        img_frame.pack(side=LEFT)
        img_frame.grid(row=0, column=1, sticky=W, padx= 10 , pady= 10)

        #labels del titulo
        edit_data_label_title = Label(self.edit_data_frame, font=self.small_font,
                                      bg=self.color_obscure, fg="white",
                                      width=22, justify='center', text="Editar Tarea ") 
        edit_data_label_title.grid(row=0, column=0, padx= 10 , pady= 10, sticky=E)

        button_img = Button(img_frame,
                             bg=self.color_orange, fg="white", borderwidth=0,
                            image = self.cross_img_tk,
                            command=lambda: self.change_data_frame(self.show_edit_frame, self.edit_data_frame, "edit"))
        #se visualiza la imagen
        button_img.grid(row=0, column=1)

        #frame del formulario
        form_frame = Frame(self.edit_data_frame)
        form_frame.config(bg=self.color_obscure)
        form_frame.grid(row=1, column=0)
        
        #labels e inputs del form
        nameLabel = Label(form_frame, font=self.small_font,
                          bg=self.color_obscure, fg="white",
                          width=10, justify='center', text="Nombre: ")
        nameLabel.grid(row=1, column=0, padx= 10 , pady= 10)

        self.edit_data_name_input = Entry(form_frame, font=self.small_font, width=15, justify='center')
        self.edit_data_name_input.grid(row=1, column=1 , padx= 10 , pady= 10)
        descriptionLabel = Label(form_frame, font=self.small_font,
                                 bg=self.color_obscure, fg="white",
                                 width=10, justify='center', text="Descripcion: ")
        descriptionLabel.grid(row=2, column=0, padx= 10 , pady= 10)

        self.edit_data_description_input = Entry(form_frame, font=self.small_font, width=15, justify='center')
        self.edit_data_description_input.grid(row=2, column=1,  padx= 10 , pady= 10)
        
        # Agarra el numero el id del registro
        selected = self.table.focus()
        # agarra los valores del registro
        values = self.table.item(selected, 'values')

        # muestra los valores seleccionados en la caja
        self.edit_data_name_input.insert(0, values[0])
        self.edit_data_description_input.insert(0, values[1])

        edit_data_button = Button(form_frame,
                            command=lambda: self.button_is_pressed(self.edit_boolean), 
                            text="Enviar",
                            font=self.small_font,
                             bg=self.color_orange, fg="white", borderwidth=0,
                            width=12)
        edit_data_button.grid(row=3, column=1,  padx= 10 , pady= 10)
        #bind de seleccion a la tabla
        self.table.bind("<ButtonRelease-1>", self.select_record)
        #booleano
        self.edit_boolean = BooleanVar(edit_data_button)
        self.edit_boolean.set(False)


    def draw_task_frame(self):
        #------------------- imagen de fondo -------------------
        self.background_img_label = Label(self.app_main_frame, image=self.background_img_tk,bg=self.color_vivid)
        self.background_img_label.place(x= 600, y= -100, relwidth= 1, relheight= 2)
        #-------------------                 -------------------

        #mostrar los datos de la base de datos apenas se muestra la tarea
    
        #contenedor de la lista tarea
        taskListFrame=Frame(self.app_main_frame)
        taskListFrame.config(bg=self.color_obscure)
        taskListFrame.pack(side=LEFT, padx=40)
            #--------------------------         Variables             --------------------------
        self.show_add_frame = BooleanVar(taskListFrame)
        self.show_add_frame.set(False)
            #--------------------------                               -------------------------- 
        
        taskTitleLabel = Label(taskListFrame, text="Tareas", bg=self.color_obscure, fg="white", font=self.medium_font, width=24)
        taskTitleLabel.grid(row=0, column=0, padx=10, pady=10)

        #tabla
        columns_list = ["name", "description", "completed"]
        self.table = ttk.Treeview(taskListFrame,
                              columns= columns_list,
                                show ='headings')

        self.table.column("name", anchor=CENTER)
        self.table.column("description", anchor=CENTER)
        self.table.column("completed", anchor=CENTER)

        self.table.heading('name', text= 'Nombre')
        self.table.heading('description', text= 'Descripcion')
        self.table.heading('completed', text= 'Completado')
        self.table.grid(row=1, column=0, padx=10)

        #scrollbar de la tabla
        self.table_scrollbar = Scrollbar(taskListFrame, orient="vertical", command=self.table.yview)
        self.table_scrollbar.grid(row=1, column=1, sticky='ns')

        self.table.configure(yscrollcommand= self.table_scrollbar.set)

        #configuracion de la srollbar
        self.table_scrollbar.config(command=self.table.yview)

        #contenedor de los botones CRUD
        buttonsFrame = Frame(self.app_main_frame)
        addButton= Button(buttonsFrame, text="Agregar",
                           font=self.small_font,
                            bg=self.color_orange, fg="white", borderwidth=0,
                             height=2, width=6,
                             command=lambda: self.change_data_frame(self.show_add_frame, self.add_data_frame, "add") ) #una vez llamada la funcion, se mostrar u ocultara el widget
        
        editButton= Button(buttonsFrame,
                          text="Editar",
                           bg=self.color_orange, fg="white", borderwidth=0,
                          font=self.small_font,
                          height=2,
                          width=6, 
                          command=lambda: self.change_data_frame(self.show_edit_frame, self.edit_data_frame, "edit"))
        deleteButton= Button(buttonsFrame,
                            text="Eliminar",
                             bg=self.color_orange, fg="white", borderwidth=0,
                            font=self.small_font,
                            height=2,
                            width=6, 
                            command= lambda: self.button_is_pressed(self.delete_boolean))
        completedButton= Button(buttonsFrame,
                                text="Completado",
                                 bg=self.color_orange, fg="white", borderwidth=0,
                                font=self.small_font,
                                height=2,
                                width=9,
                                command=lambda: self.button_is_pressed(self.completed_boolean))
        
        #test_button = Button(buttonsFrame,
        #                        text="test",
        #                        font=self.small_font,
        #                        height=2,
        #                        width=9,
        #                        command=self.change_values_of_completed_task)
        
        self.delete_boolean = BooleanVar(deleteButton)
        self.delete_boolean.set(False)

        buttonsFrame.pack(side=TOP, pady=55)
        #buttonsFrame.grid(row=0, column=1)
        buttonsFrame.config(bg=self.color_obscure)
        addButton.grid(row=0, column=5, padx=10, pady=10)
        editButton.grid(row=1, column=5, padx=10, pady=10)
        deleteButton.grid(row=1, column=6, padx=10, pady=10)
        completedButton.grid(row=1, column=7, padx=10, pady=10)

        #test_button.grid(row=1, column=8, padx=10, pady=10)

        self.query_database()
    
    
    #--------------------------       query base de datos         -------------------------- 

    
    #-------------  añadir datos a la tabla ------------- 
    def add_data(self):
       #se agrega los datos en la base
       self.db_tasks.add_task(self.add_data_name_input.get(), self.add_data_description_input.get())

       #limpiar los inputs
       self.add_data_name_input.delete(0, END)
       self.add_data_description_input.delete(0, END)

       #limpia la tabla
       self.table.delete(*self.table.get_children())
       self.query_database()


    def button_is_pressed(self,boolean):
       #primero se pregunta que var booleana se ingreso
       if boolean.get() is False:
        #se setea a true la variable booleana ingresada
        boolean.set(True)
        #print("paso a true")

        if self.delete_boolean.get() is True: #borra datos de la tabla. pregunta si el booleano es verdadero 
            if self.delete_boolean.get() is not None:
                #Se obtiene los valores de la fila seleccionada
                cur_item =self.table.focus()

                #se obtiene el valor ID de la fila seleccionada y se almacena
                if cur_item == "":
                    return
                name_row_value, desc_row_value = (self.table.item(cur_item)['values'][0],
                                              self.table.item(cur_item)['values'][1])

                #borrar visualmente
                x = self.table.selection()[0]
                self.table.delete(x)

                #borrar de la base de datos
                self.db_tasks.remove_task(name_row_value, desc_row_value)

                self.delete_boolean.set(False)

                #limpia la tabla
                self.table.delete(*self.table.get_children())
                self.query_database()

        elif self.completed_boolean.get() is True: # Marcar como completado datos del registro
            #Se obtiene los valores de la fila seleccionada
            cur_item =self.table.focus()

            #se obtiene el valor ID de la fila seleccionada y se almacena
            if cur_item == "":
                return
            name_row_value, desc_row_value = (self.table.item(cur_item)['values'][0],
                                              self.table.item(cur_item)['values'][1])

            #actualiza el valor a true de la base de datos
            if self.table.item(cur_item)['values'][2] == "No":
                self.db_tasks.change_state_task(name_row_value, desc_row_value, 1)
            else:
                self.db_tasks.change_state_task(name_row_value, desc_row_value, 0)         

            self.completed_boolean.set(False)

            #limpia la tabla
            self.table.delete(*self.table.get_children())
            self.query_database()
        
        elif self.edit_boolean.get() is True:     # Actualizar datos del registro
            #Se obtiene los valores de la fila seleccionada
            cur_item =self.table.focus()

            #se obtiene el valor ID de la fila seleccionada y se almacena
            if cur_item == "":
                return
            name_row_value, desc_row_value = (self.table.item(cur_item)['values'][0],
                                              self.table.item(cur_item)['values'][1])

            # se actualiza el registro
            self.table.item(cur_item, text="", values=(self.edit_data_name_input.get(), self.edit_data_description_input.get(),))
        
            #actualiza el valor a true de la base de datos 
            self.db_tasks.update_task(name_row_value, desc_row_value, self.edit_data_name_input.get(), self.edit_data_description_input.get())                

            self.edit_boolean.set(False)

            #limpia la tabla
            self.table.delete(*self.table.get_children())
            self.query_database()


    def change_values_of_completed_task(self):
        #se obtiene todos los valores de las filas
        rows = self.table.get_children()
        #inicio un contador para el while
        for row in rows:
            if self.table.item(row)["values"][2] == 0:
                self.table.set(row, "#3", "No")
            else:
                self.table.set(row, "#3", "SI")


    def query_database(self):
        # Limpia la tabla
        for record in self.table.get_children():
           self.table.delete(record)

        records = self.db_tasks.get_tasks()
        
        # muestra los datos en la tabla
        for record in records:
            self.table.insert(parent='',
                              index='end',
                              iid=self.count_records,
                              text='',
                              values=(record.name,record.description,record.completed ))

        self.change_values_of_completed_task()


main = Main()
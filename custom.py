from socket import *
import customtkinter
from threading import *
from PIL import Image

app_logo = customtkinter.CTkImage(light_image=Image.open("WhatsDown.png"),
                                  size=(50, 50))

customtkinter.set_appearance_mode("Light")
customtkinter.set_default_color_theme("blue")

client = socket(AF_INET, SOCK_STREAM)
ip = '127.0.0.1'
port = 55555
client.connect((ip, port))


class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("360x130")
        self.title("WhatsDown")
        self.label = customtkinter.CTkLabel(self, text="Do you want to exit?")
        self.label.pack(padx=20, pady=20)
        self.label.grid(row=0, column=0, columnspan=2, padx=20, pady=10)

        self.yes_button = customtkinter.CTkButton(self, text="Yes", command=self.exit_f)
        self.yes_button.grid(row=1, column=0, padx=20, pady=10)

        self.no_button = customtkinter.CTkButton(self, text="No", command=self.destroy)
        self.no_button.grid(row=1, column=1, padx=20, pady=10)

    def exit_f(self):
        self.destroy()
        exit()


def change_appearance_mode_event(new_appearance_mode: str):
    customtkinter.set_appearance_mode(new_appearance_mode)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.users = None
        self.sent_message = None
        self.received_message = None
        self.name = None
        self.message_counter = 1
        self.chat_counter = 2
        self.resizable(width=False, height=False)
        self.title("WhatsDown")
        self.geometry(f"{1100}x{580}")

        self.grid_columnconfigure(1, weight=1)

        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo = customtkinter.CTkLabel(self.sidebar_frame, image=app_logo, text="",
                                           font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Chats",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=1, column=0, padx=20)
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Clear Chat", command=self.clear_chat)
        self.sidebar_button_1.grid(row=2, column=0, padx=20, pady=10)

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_options = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                                   values=["Light", "Dark", "System"],
                                                                   command=change_appearance_mode_event)
        self.appearance_mode_options.grid(row=5, column=0, padx=20, pady=(10, 10))

        self.exit_button = customtkinter.CTkButton(self.sidebar_frame, text="Exit", hover_color="Red",
                                                   command=self.exit_app)
        self.exit_button.grid(row=6, column=0, padx=20, pady=10)

        self.entry = customtkinter.CTkEntry(self, placeholder_text="Type a message")
        self.entry.grid(row=3, column=1, columnspan=1, padx=(20, 0), pady=(20, 20), sticky="nsew")

        self.main_button_1 = customtkinter.CTkButton(master=self, text="Send", fg_color="transparent", border_width=2,
                                                     text_color=("gray10", "#DCE4EE"), command=self.send_message)
        self.main_button_1.grid(row=3, column=2, padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.tabview = customtkinter.CTkTabview(master=self, width=250, height=490)
        self.tabview.grid(row=1, column=1, columnspan=2, padx=(20, 10), pady=(10, 0), sticky="nsew")

        self.tabview.add("All")  # add tab at the end
        self.tabview.set("All")  # set currently visible tab

        # set default values
        name_dialog = customtkinter.CTkInputDialog(text="What is your name:", title="WhatsDown")
        name = name_dialog.get_input()
        self.appearance_mode_options.set("Light")
        if name == "":
            exit()
        self.set_name(name=name)

        recv_thread = Thread(target=self.recv_message)
        recv_thread.daemon = True
        recv_thread.start()
        self.toplevel_window = None

    def exit_app(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self)
            self.toplevel_window.focus()
        else:
            self.toplevel_window.focus()

    def set_name(self, name):
        client.send(name.encode('utf8'))
        self.name = name
        self.logo_label.configure(text=name)

    def clear_chat(self):
        current_tab = self.tabview.get()
        for widget in self.tabview.tab(current_tab).grid_slaves():
            widget.grid_forget()

    def send_message(self):
        message = self.entry.get()
        if len(message) > 0:
            self.entry.delete(0, len(message))
            self.sent_message = customtkinter.CTkLabel(self.tabview.tab(self.tabview.get()), text=message + "\n",
                                                       width=840,
                                                       font=customtkinter.CTkFont(size=14), text_color=("gray10", "#DCE4EE"),
                                                       anchor="e")
            self.sent_message.grid(row=self.message_counter, column=1, columnspan=2, padx=(10, 10), sticky="nsew")
            self.message_counter = self.message_counter + 1
            detailed_message = self.tabview.get() + "--" + message
            client.send(detailed_message.encode('utf8'))

    def recv_message(self):
        while True:
            server_message = client.recv(1024).decode('utf8')
            print(server_message)
            message_array = server_message.split("--")
            if len(message_array) > 2:
                if message_array[1] == "All":
                    self.received_message = customtkinter.CTkLabel(self.tabview.tab("All"),
                                                                   text=message_array[0] + ": " + message_array[2],
                                                                   width=840,
                                                                   font=customtkinter.CTkFont(size=14),
                                                                   text_color=("gray10", "#DCE4EE"),
                                                                   anchor="w")
                    self.received_message.grid(row=self.message_counter, column=1, columnspan=2, padx=(10, 10),
                                               sticky="nsew")
                    self.message_counter = self.message_counter + 1
                elif message_array[1] == self.name:
                    self.received_message = customtkinter.CTkLabel(self.tabview.tab(message_array[0]),
                                                                   text=message_array[2], width=840,
                                                                   font=customtkinter.CTkFont(size=14),
                                                                   text_color="red",
                                                                   anchor="w")
                    self.received_message.grid(row=self.message_counter, column=1, columnspan=2, padx=(10, 10),
                                               sticky="nsew")
                    self.message_counter = self.message_counter + 1
            if server_message.startswith("new_client-"):
                self.tabview.add(server_message.split("-")[1])
            elif server_message.startswith("exit_client-"):
                self.tabview.delete(server_message.split("-")[1])
            elif server_message.startswith("Other users:"):
                self.users = server_message.split(":")[1]
                for us in self.users.split(","):
                    if us != self.name:
                        self.tabview.add(us)


if __name__ == "__main__":
    app = App()
    app.mainloop()

import tkxui
from PIL import Image, ImageTk

if __name__ in '__main__':
    root = tkxui.Tk(display=tkxui.FRAMELESS)
    root.title("Login") # Set a title
    root.config(bg="#2A2A2A") # Configure the background color of the window
    root.resizer_bg("#2A2A2A") # Configure the background color of the window resizer
    root.iconbitmap("icon.ico") # Set an icon

    # Configure the border of the frameless window
    root.config_border(
        {
            'border': {
                'bg': "#2A2A2A"
            },
            'maximize': {
                'fg': 'white',
                'hoverfg': 'white',
                'hoverbg': '#242424',
                'bg': '#2A2A2A'
            },
            'minimize': {
                'fg': 'white',
                'hoverfg': 'white',
                'hoverbg': '#242424',
                'bg': '#2A2A2A'
            },
            'close': {
                'hoverbg': '#F3350C',
                'hoverfg': 'white',
                'fg': 'white',
                'bg': '#2A2A2A'
            }
        }
    )

    # Set some attributes to the window
    root.geometry("400x500")
    root.minsize(width=400, height=500)
    root.resizable(height = True, width = True)

    root.center() # Center the window in the middle of the screen

    json_loader = tkxui.JSONLoader(root)
    json_loader.generate("ui.json")

    root.emailEntry.label.config(text="Username / email :")
    root.passwordEntry.label.config(text="Password :")

    temp = Image.open("logo.png")
    githubLogoImg = ImageTk.PhotoImage(temp)

    root.githubLogo.config(image=githubLogoImg)
    root.githubLogo.image = githubLogoImg

    root.mainloop()
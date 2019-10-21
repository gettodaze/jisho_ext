import tkinter
from jisho import Jisho
from PIL import Image, ImageTk
j = Jisho()
def click():
    entered_text = textentry.get()
    output.delete(0.0, tkinter.END)
window = tkinter.Tk()
window.title("John's Jisho")
window.configure(background="black")

# photo1 = ImageTk.PhotoImage(Image.open('assets/black_rowlett.gif').resize(100, 100))
# tkinter.Label(window, image=photo1, bg="black").grid(row=0,column=0,sticky=tkinter.E)

tkinter.Label(window, text="Keyword:", bg="black", fg="white", font="none 12 bold").grid(
    row=1, column=0, sticky=tkinter.W)
textentry = tkinter.Entry(window, width=20, bg="white")
textentry.grid(row=2, column = 0, sticky=tkinter.W)
tkinter.Button(window, text='SUBMIT', width=6,
               command=click).grid(row=3, column=0, sticky=tkinter.W)
tkinter.Label(window,text='\ndefinition', bg="black",fg="white", font="none 12 bold").grid(
    row=4, column=0, sticky=tkinter.W
)
output = tkinter.Text(window, width=75, height=9, wrap=tkinter.WORD, background="white")
output.grid(row=50, column=0, columnspan=2, sticky=tkinter.W)


window.mainloop()
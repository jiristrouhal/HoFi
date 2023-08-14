import tkinter as tk
import treeview as tw
import treemanager as tmg
import treelist as tl
import tree as treemod


EDIT_FRAME_LABEL = "Editor"


root = tk.Tk()
root.geometry("800x600")


edit_frame = tk.LabelFrame(root, text=EDIT_FRAME_LABEL)
manager_frame = tk.Frame(root)


manager_frame.pack(expand=1,fill=tk.BOTH)
edit_frame.pack(expand=2,fill=tk.BOTH)


treelist = tl.TreeList()
manager = tmg.Tree_Manager(treelist, manager_frame)
editor = tw.Treeview(edit_frame)


if __name__=="__main__":
    root.mainloop()
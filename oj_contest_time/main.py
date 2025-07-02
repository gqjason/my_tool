# app/main.py
import tkinter as tk
from ui_and_logic.main_logic import AppLogic
from ui_and_logic.main_ui import AppUI

def main():
    root = tk.Tk()
    
    # 创建逻辑类实例
    app_logic = AppLogic()
    
    # 创建UI类实例，并传入逻辑类实例
    app_ui = AppUI(root, app_logic)
    
    root.mainloop()

if __name__ == "__main__":
    main()
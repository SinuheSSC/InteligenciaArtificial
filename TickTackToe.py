import tkinter as tk
from tkinter import messagebox
import math

class GatoImbatible:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Gato IA: Modo Imbatible")
        
        # Configuramos quién es quién
        self.ia = "X"
        self.jugador = "O"
        
        self.tablero = [" " for _ in range(9)]
        self.botones = []
        self.crear_interfaz()
        
        # ¡La IA hace el primer movimiento de inmediato!
        self.movimiento_ia()

    def crear_interfaz(self):
        for i in range(9):
            boton = tk.Button(self.ventana, text=" ", font=('Arial', 20, 'bold'), 
                             width=5, height=2, bg="#f0f0f0",
                             command=lambda i=i: self.movimiento_jugador(i))
            boton.grid(row=i//3, column=i%3, padx=2, pady=2)
            self.botones.append(boton)

    def verificar_ganador(self, t):
        lineas = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]]
        for c in lineas:
            if t[c[0]] == t[c[1]] == t[c[2]] != " ":
                return t[c[0]]
        return "Empate" if " " not in t else None

    def minimax(self, tablero, es_maximizando):
        resultado = self.verificar_ganador(tablero)
        if resultado == self.ia: return 1
        if resultado == self.jugador: return -1
        if resultado == "Empate": return 0

        if es_maximizando:
            mejor_p = -math.inf
            for i in range(9):
                if tablero[i] == " ":
                    tablero[i] = self.ia
                    p = self.minimax(tablero, False)
                    tablero[i] = " "
                    mejor_p = max(p, mejor_p)
            return mejor_p
        else:
            mejor_p = math.inf
            for i in range(9):
                if tablero[i] == " ":
                    tablero[i] = self.jugador
                    p = self.minimax(tablero, True)
                    tablero[i] = " "
                    mejor_p = min(p, mejor_p)
            return mejor_p

    def movimiento_ia(self):
        mejor_p = -math.inf
        movimiento = -1
        
        # Optimización: Si el tablero está vacío, elegir una esquina o el centro rápido
        if self.tablero.count(" ") == 9:
            movimiento = 0 # Ocupa la esquina superior izquierda
        else:
            for i in range(9):
                if self.tablero[i] == " ":
                    self.tablero[i] = self.ia
                    p = self.minimax(self.tablero, False)
                    self.tablero[i] = " "
                    if p > mejor_p:
                        mejor_p = p
                        movimiento = i
        
        if movimiento != -1:
            self.ejecutar_jugada(movimiento, self.ia)

    def movimiento_jugador(self, i):
        if self.tablero[i] == " " and not self.verificar_ganador(self.tablero):
            self.ejecutar_jugada(i, self.jugador)
            if not self.verificar_ganador(self.tablero):
                # Le damos 300ms para que no parezca que la IA te responde con odio instantáneo
                self.ventana.after(300, self.movimiento_ia)

    def ejecutar_jugada(self, i, signo):
        self.tablero[i] = signo
        color = "#e74c3c" if signo == "X" else "#3498db" # Rojo para IA, Azul para Humano
        self.botones[i].config(text=signo, state="disabled", disabledforeground=color)
        
        res = self.verificar_ganador(self.tablero)
        if res:
            self.finalizar_juego(res)

    def finalizar_juego(self, resultado):
        if resultado == "Empate":
            msg = "¡Increíble! Lograste empatar contra la máquina."
        else:
            msg = f"La IA ({resultado}) ha ganado. ¡Sigue intentando!"
        
        messagebox.showinfo("Fin de la partida", msg)
        self.ventana.destroy()

    def iniciar(self):
        self.ventana.mainloop()

if __name__ == "__main__":
    juego = GatoImbatible()
    juego.iniciar()
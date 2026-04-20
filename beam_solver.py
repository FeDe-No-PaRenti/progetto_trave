#motore di calcolo
import numpy as np
from math import pi
import matplotlib.pyplot as plt
def build_matrix(n):
    A = np.zeros((n+1, n+1)) # matrice quadrata (n+1) × (n+1)
    coefficenti = [1, -4, 6, -4, 1] 
    for i in range(n+1):  
        for j, c in enumerate(coefficenti):
            col = i + (j - 2)    # j-2 perché i coefficienti vanno da i-2 a i+2
            if 0 <= col < n+1:  # solo se la colonna esiste
                A[i, col] = c 
    return A

# Test temporaneo
#A = build_matrix(6)
#print(np.array2string(A, precision=0, suppress_small=True))
#print(A)

# VERSIONE VECCHIA (per carico uniforme)
#def build_rhs(q, h, EJ, n): # right hand side
#    #b = np.zeros(n+1) #vettore lungo n+1
#    #for i in range(n+1):
#        #b[i] = -q * h**4 / EJ
#    b = np.full(n+1, -q * h**4 / EJ)
#    return b

# Test
#b = build_rhs(1000, 1.0, 1e6, 4)
#print(b)

# VERSIONE NUOVA comprende carico uniforme e non
def build_rhs(q, h, EJ, n): # right hand side
    b = -q * h**4 / EJ
    return b

def apply_boundary_conditions(A, b, bc_left, bc_right): #modifica la matrice A e il vettore b in base ai vincoli agli estremi.
                                                        #bc_left e bc_right saranno stringhe tipo "appoggio", "incastro", "libero"    
    n = A.shape[0] -1
    
    if bc_left == "Appoggio":
        A[0, :] = 0 #azzera tutta la riga 
        A[0, 0] = 1 #mette 1 sulla diagonale
        b[0] = 0    #termine noto = 0
        A[1][1] += -1 #perché  y₋₁ = -y₁. e quindi quando raccogli (es.diventa y₁(6-1) )
    elif bc_left == "Incastro":
        A[0, :] = 0 #azzera tutta la riga 
        A[0, 0] = 1
        b[0] = 0
        A[1][1] += +1 #perché y₋₁ = y₁.   e quindi quando raccogli (es.diventa y₁(6+1) )
    else :
        A[0][0] += -4
        A[0][2] += 1
        A[1][0] += 2
        A[1][1] += -1

    

    if bc_right == "Appoggio":
        A[n, :] = 0 #azzera tutta la riga 
        A[n, n] = 1 #mette 1 sulla diagonale
        b[n] = 0    #termine noto = 0
        A[n-1][n-1] += -1 #perché  y₋₁ = -y₁. e quindi quando raccogli (es.diventa y₁(6-1) )
    elif bc_right == "Incastro":
        A[n, :] = 0 #azzera tutta la riga 
        A[n, n] = 1
        b[n] = 0
        A[n-1][n-1] += +1 #perché y₋₁ = y₁.   e quindi quando raccogli (es.diventa y₁(6+1) )
    else :
        A[n][n] += -4
        A[n][n-2] += 1
        A[n-1][n] += 2
        A[n-1][n-1] += -1
    return A,b

# Test
#A = build_matrix(4)
#b = build_rhs(1000, 1.0, 1e6, 4)
#apply_boundary_conditions(A, b, "Appoggio", "Appoggio")
#print(A)
#print(b)


#esempio visivo supporti
#    |←————————— L ————————→|
#    
#    ↑           ↑           ↑
# appoggio   appoggio    appoggio
# sinistro   interno      destro
# (estremo)  (x = L/2)   (estremo)
#SPIEGAZIONE
# Il metodo delle differenze finite di default calcola la deformata come se la trave fosse libera di spostarsi in tutti i nodi interni. 
# Non sa che in quel punto c'è un appoggio.
# Dobbiamo quindi dirgli che in quel nodo y = 0 —> lo spostamento è zero perché c'è un vincolo. 
# Lo facciamo sostituendo la riga k con l'equazione y[k] = 0, 
# esattamente come abbiamo fatto per gli estremi.
def apply_internal_supports(A, b, supports):
    #for i in range(len(supports)):
    #    k = supports[i]
    for k in supports: # identico a sopra
        A[k, :] = 0
        A[k, k] = 1
        b[k] = 0
    return A,b
    

def solve_beam(L, EJ, n, q, bc_left, bc_right, direzione_carico, supports,  tipo_carico="Uniforme"):
    h = L / n
    x = np.linspace(0,L,n+1) #crea un array di N numeri equispaziati tra un valore iniziale e uno finale: np.linspace(inizio, fine, quanti_punti)
    A = build_matrix(n)
    if tipo_carico == "Uniforme":
        q_array = np.full(n+1, q)
    elif tipo_carico == "Triangolare":
        if direzione_carico == "Sinistra → Destra":
            q_array = np.linspace(0, q, n+1)  # cresce da 0 a q
        else:
            q_array = np.linspace(q, 0, n+1)  # specchiato
    elif tipo_carico == "Mezza trave":
        q_array = np.zeros(n+1)
        if direzione_carico == "Sinistra → Destra":
            q_array[:n//2] = q  # carico solo sulla prima metà  | assegna il valore q a tutti gli elementi dall'indice 0 fino a n//2". È la slice notation di numpy:
#| q_array = np.zeros(n+1) ->[0, 0, 0, 0, 0, 0], q_array[:3] = 1000 -> [1000, 1000, 1000, 0, 0, 0], q_array[3:] = 500 ->[1000, 1000, 1000, 500, 500, 500] 
        else:
            q_array[n//2:] = q  # specchiato
 
    b = build_rhs(q_array,h,EJ,n)
    apply_boundary_conditions(A,b,bc_left,bc_right)
    apply_internal_supports(A,b,supports)
    y = np.linalg.solve(A,b)
    #M(x) = EJ · y''      (seconda derivata di y)   quanto "tende a piegarsi" la trave in quel punto. Serve per verificare che la trave non si rompa
    #T(x) = EJ · y'''     (terza derivata di y)     la forza verticale interna. Serve anch'esso per la verifica strutturale
    #per i nodi interni, -> Entrambe le derivate si calcolano solo per i nodi interni (perché ai bordi mancano i vicini).
    #y''[i] = (y[i-1] - 2·y[i] + y[i+1]) / h²
    #y'''[i] = (-y[i-2] + 2·y[i-1] - 2·y[i+1] + y[i+2]) / (2·h³)
     
    M = np.zeros(n+1)
    T = np.zeros(n+1)
    for i in range(1,n):
        M[i] = EJ * (y[i-1] - 2*y[i] + y[i+1]) / h**2
    for i in range(2,n-1): 
        T[i] = EJ * (-y[i-2] + 2*y[i-1] - 2*y[i+1] + y[i+2]) / (2*h**3)
    # Bordo sinistro (forward)
    M[0] = EJ * (2*y[0] - 5*y[1] + 4*y[2] - y[3]) / h**2
    # Bordo destro (backward)
    M[n] = EJ * (2*y[n] - 5*y[n-1] + 4*y[n-2] - y[n-3]) / h**2

    # Bordo sinistro
    T[0] = EJ * (-5*y[0] + 18*y[1] - 24*y[2] + 14*y[3] - 3*y[4]) / (2*h**3)
    T[1] = T[0]
    # Bordo destro
    T[n] = EJ * (5*y[n] - 18*y[n-1] + 24*y[n-2] - 14*y[n-3] + 3*y[n-4]) / (2*h**3)
    T[n-1] = T[n]
    return x,y,M,T # x = posizioni dei nodi , y = gli spostamenti (la deformata) , M = momento flettente in ogni nodo, T = il taglio in ogni nodo
                                                                               
# Test
#x, y, M, T = solve_beam(
#    L=4, EJ=1e6, n=100, q=1000,
#    bc_left="Appoggio", bc_right="Appoggio",
#    supports=[]
#)
#print("y_max:", min(y)*1000, "mm")
#print("M_max:", max(M), "N·m")


def calcola_J(sezione, params):
    if sezione == "Quadrato pieno": #1
        H = params["H"]
        return H**4 / 12
    elif sezione == "Quadrato cavo": #2
        H = params["H"]
        h = params["h"]
        return (H**4 - h**4) / 12
    elif sezione == "Rettangolo pieno": #3
        B = params["B"]
        H = params["H"]
        return B * H**3 / 12
    elif sezione == "Rettangolo cavo": #4
        B = params["B"]
        H = params["H"]
        b = params["b"]
        h = params["h"]
        return 1/12*(B*H**3-b*h**3)
    elif sezione == "Cerchio pieno": #5
        D = params["D"]
        return pi * D**4 / 64
    elif sezione == "Cerchio cavo": #6
        D = params["D"]
        d = params["d"]
        return pi * (D**4 - d**4) / 64
    elif sezione == "Figura L": #7
        B = params["B"]
        H = params["H"]
        b = params["b"]
        h = params["h"]
        c = params["c"]
        d = params["d"]
        a = 1/2 * (c*H**2 + b * d**2) / (c*H + b * d)
        A = H - a
        return (B*a**3 - b * (h - A)**3 + c * A**3 )/ 3 
    elif sezione == "Figura T rovesciata": #8
        B = params["B"]
        H = params["H"]
        b = params["b"]
        h = params["h"]
        c = params["c"]
        d = params["d"]
        a = 1/2 * (c*H**2 + b * d**2) / (c*H + b * d)
        A = H - a
        return (B*a**3 - b * (h - A)**3 + c * A**3 )/ 3 
    

# confronto con la soluzione analitica
def soluzione_analitica(L, EJ, q, bc_left, bc_right, tipo_carico,supports):
    # il confronto ha senso solo con carico uniforme e schemi standard
    if tipo_carico != "Uniforme":
        return None
    # se ci sono appoggi interni non abbiamo formula analitica
    if len(supports) > 0:  
        return None
    if bc_left == "Appoggio" and bc_right == "Appoggio":
        y_max = -5 * q * L**4 / (384 * EJ)
        M_max = q * L**2 / 8
    elif bc_left == "Incastro" and bc_right == "Libero":
        y_max = -q * L**4 / (8 * EJ)
        M_max = q * L**2 / 2
    elif bc_left == "Incastro" and bc_right == "Incastro":
        y_max = -q * L**4 / (384 * EJ)
        M_max = q * L**2 / 12
    else:
        return None  # schema non standard, nessun confronto
    
    return y_max, M_max

def tabella_convergenza(L, EJ, q, bc_left, bc_right): 
    valori = [10,20,50,100,200,500]
    risultati = []
    risultato_analitico = soluzione_analitica(L, EJ, q, bc_left, bc_right, "Uniforme", [])
    for i in range(len(valori)):
        x, y, M, T = solve_beam(L, EJ, valori[i], q, bc_left, bc_right, direzione_carico="Sinistra → Destra", supports=[], tipo_carico="Uniforme")
        y_num = min(y) * 1000 # in mm 
        
        y_analitico = risultato_analitico[0] * 1000  # prende solo y_max in mm
    
        errore = abs((y_num - y_analitico) / y_analitico) * 100
        risultati.append({
        "n": valori[i],
        "y_max numerico (mm)": round(y_num, 4),
        "y_max analitico (mm)": round(y_analitico, 4),
        "errore (%)": round(errore, 4)
    })
    return risultati


def reazioni_vincolari(T, M, bc_left, bc_right, supports, n):
    reazioni = {}

    #reazione estremo sinistro
    if bc_left == "Appoggio" or bc_left == "Incastro":
        reazioni["R_sinistra (N)"] = round(T[0],2)

    #se è a incastro, aggiungi anche il momento
    if bc_left == "Incastro":
        reazioni["M_incastro_sx (N·m)"] = round(M[0], 2)

    # Reazione estremo destro 
    if bc_right == "Appoggio" or bc_right == "Incastro":
        reazioni["R_destra (N)"] = round(-T[n], 2)
    
    if bc_right == "Incastro":
        reazioni["M_incastro_dx (N·m)"] = round(-M[n], 2)
    
    # Reazioni appoggi interni — salto del taglio
    for idx, k in enumerate(supports):
        R_int = T[k+1] - T[k-1]
        reazioni[f"R_interna_{idx+1} (N)"] = round(R_int, 2)
    
    return reazioni

def disegno_trave(L, bc_left, bc_right, supports, tipo_carico, n, direzione_carico):
    fig, ax = plt.subplots(figsize=(10, 3)) 
    
    # Trave
    ax.plot([0, L], [0, 0], 'b-', linewidth=6)
    
   # Carico distribuito
    posizioni = np.linspace(0.1, L-0.1, 15)
    for i, x in enumerate(posizioni):
        if tipo_carico == "Uniforme":
            altezza = 0.3
        elif tipo_carico == "Triangolare":
            if direzione_carico == "Sinistra → Destra":
                altezza = 0.05 + 0.25 * (x / L)     # cresce da sinistra a destra
            else:
                altezza = 0.05 + 0.25 * (1 - x / L)  # specchiato  
        elif tipo_carico == "Mezza trave":
            if direzione_carico == "Sinistra → Destra":
                altezza = 0.3 if x < L/2 else 0  # solo prima metà
            else:
                altezza = 0.3 if x > L/2 else 0  # specchiato
    
        if altezza > 0:
            ax.annotate('', xy=(x, 0), xytext=(x, altezza),
                        arrowprops=dict(arrowstyle='->', color='red'))
            
    ax.text(L/2, 0.45, f'q = {tipo_carico}', ha='center', color='red')
    
    # Vincolo sinistro
    if bc_left == "Appoggio":
        ax.plot([0], [-0.1], 'k^', markersize=15)
    elif bc_left == "Incastro":
        ax.fill_betweenx([-0.2, 0.2], -0.2, 0, color='gray')
    
    # Vincolo destro
    if bc_right == "Appoggio":
        ax.plot([L], [-0.1], 'k^', markersize=15)
    elif bc_right == "Incastro":
        ax.fill_betweenx([-0.2, 0.2], L, L+0.2, color='gray')
    
    # Appoggi interni
    h = L / n
    for k in supports:
        x_int = k * h
        ax.plot([x_int], [-0.1], 'k^', markersize=15)
    
    ax.set_xlim(-0.3, L+0.3)
    ax.set_ylim(-0.4, 0.6)
    ax.axis('off')
    ax.set_title("Schema della trave")
    
    return fig
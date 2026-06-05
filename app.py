#l'interfaccia streamlit
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from beam_solver import calcola_J, solve_beam, soluzione_analitica, tabella_convergenza, reazioni_vincolari, disegno_trave, disegno_sezione
st.title("Risolutore linea elastica")  
st.set_page_config(layout="wide")
col1, col2 = st.columns([1, 2])

with col1:
    L = st.number_input("Lunghezza trave (m)", value=4.0) 
    n = st.number_input("Numero nodi", value=100, step=1, format="%d")
    q = st.number_input("Sforzo applicato (N/m)", value= 1000)
    tipo_carico = st.selectbox("Tipo di carico", ["Uniforme", "Triangolare", "Mezza trave"])
    if tipo_carico == "Triangolare" or tipo_carico == "Mezza trave":
        direzione_carico = st.selectbox("Direzione carico", ["Sinistra → Destra", "Destra → Sinistra"])
    else:
        direzione_carico = "Sinistra → Destra"
    bc_left = st.selectbox("Vincolo sinistro", ["Appoggio", "Incastro", "Libero"])
    bc_right = st.selectbox("Vincolo destro", ["Appoggio", "Incastro", "Libero"])
    n_supports = st.number_input("Numero appoggi interni", value=0, step=1, format="%d")

    supports = []
    for i in range(n_supports): 
        default_pos = L / (n_supports + 1) * (i + 1)  # distribuisce gli appoggi uniformemente
        pos = st.number_input(f"Posizione appoggio {i+1} (m)", value=default_pos, key=f"support_{i}") # f -> formatted string permette {i+1}
        if pos <= 0 or pos >= L:
            st.error(f"L'appoggio {i+1} deve essere dentro la trave (tra 0 e {L} m esclusi)")
            st.stop() 
        h = L / n
        k = round(pos / h)
        if k in supports:  # controlla se l'indice è già presente
            st.error(f"L'appoggio {i+1} coincide con un appoggio già inserito!")
            st.stop()
        supports.append(k)
    

    sezione = st.selectbox("Tipo di sezione", [
        "Nessuna (inserisci EJ manualmente)",
        "Quadrato pieno",
        "Quadrato cavo",
        "Rettangolo pieno",
        "Rettangolo cavo",
        "Cerchio pieno",
        "Cerchio cavo",
        "Figura L",
        "Figura T rovesciata"
    ])

    params = {}
    if sezione == "Quadrato pieno":
        params["H"] = st.number_input("H (m)", value=0.1)
    elif sezione == "Quadrato cavo":
        params["H"] = st.number_input("H (m)", value=0.1)
        params["h"] = st.number_input("h (m)", value=0.05)
    elif sezione == "Rettangolo pieno":
        params["B"] = st.number_input("B (m)", value=0.1)
        params["H"] = st.number_input("H (m)", value=0.2)
    elif sezione == "Rettangolo cavo":
        params["B"] = st.number_input("B (m)", value=0.1)
        params["H"] = st.number_input("H (m)", value=0.2)
        params["b"] = st.number_input("b (m)", value=0.08)
        params["h"] = st.number_input("h (m)", value=0.18)
    elif sezione == "Cerchio pieno":
        params["D"] = st.number_input("D (m)", value=0.1)
    elif sezione == "Cerchio cavo":
        params["D"] = st.number_input("D (m)", value=0.1)
        params["d"] = st.number_input("d (m)", value=0.08)
    elif sezione == "Figura L":
        params["B"] = st.number_input("B (m)", value=0.1)
        params["H"] = st.number_input("H (m)", value=0.2)
        params["b"] = st.number_input("b (m)", value=0.08)
        params["h"] = st.number_input("h (m)", value=0.18)
        params["c"] = st.number_input("c (m)", value=0.01)
        params["d"] = st.number_input("d (m)", value=0.01)
    elif sezione == "Figura T rovesciata":
        params["B"] = st.number_input("B (m)", value=0.1)
        params["H"] = st.number_input("H (m)", value=0.2)
        params["b"] = st.number_input("b (m)", value=0.08)
        params["h"] = st.number_input("h (m)", value=0.18)
        params["c"] = st.number_input("c (m)", value=0.01)
        params["d"] = st.number_input("d (m)", value=0.01)

    #determino EJ
    E = st.number_input("Modulo di Young E (N/m²)", value=2e11)

    if sezione != "Nessuna (inserisci EJ manualmente)":
        fig_sez = disegno_sezione(sezione, params)
        st.pyplot(fig_sez)
        J = calcola_J(sezione, params)
        EJ = E * J
        st.write(f"J calcolato: {J:.6e} m⁴")
        st.write(f"EJ calcolato: {EJ:.4e} N·m²")
    else:
        EJ = st.number_input("EJ (N·m²)", value=1e6)

 
if st.button("Calcola"):
    
    with col2:
        #controlli 
        if n < 4:
            st.error("Il numero di nodi deve essere almeno 4!")
            st.stop() 

        if bc_left == "Libero" and bc_right == "Libero":
            st.error("La trave non può essere libera su entrambi gli estremi!")
            st.stop()
        if L <= 0:
            st.error("La lunghezza della trave deve essere maggiore di zero!")
            st.stop()
        if EJ <= 0:
            st.error("EJ deve essere maggiore di zero!")
            st.stop()
        #calcolo 
        x, y, M, T = solve_beam(L, EJ, n, q, bc_left, bc_right, direzione_carico , supports=supports,  tipo_carico=tipo_carico)
        
        #disegno
        fig0 = disegno_trave(L, bc_left, bc_right, supports, tipo_carico, n, direzione_carico)
        st.pyplot(fig0)

        #grafici 
        # Grafico deformata
        graf1, graf2, graf3 = st.columns(3)

        with graf1:
            fig1, ax1 = plt.subplots()
            ax1.plot(x, y*1000)
            ax1.set_title("Deformata")
            ax1.set_xlabel("x (m)")
            ax1.set_ylabel("y (mm)")
            ax1.grid(True)
            st.pyplot(fig1)

        with graf2:
            fig2, ax2 = plt.subplots()
            ax2.plot(x, M)
            ax2.set_title("Momento flettente")
            ax2.set_xlabel("x (m)")
            ax2.set_ylabel("M (N·m)")
            ax2.grid(True)
            st.pyplot(fig2)

        with graf3:
            fig3, ax3 = plt.subplots()
            ax3.plot(x, T)
            ax3.set_title("Taglio")
            ax3.set_xlabel("x (m)")
            ax3.set_ylabel("T (N)")
            ax3.grid(True)
            st.pyplot(fig3)
    with col1:
        #risultati
        st.subheader("Risultati numerici")
        st.write(f"Spostamento massimo: {min(y)*1000:.4f} mm")
        st.write(f"Momento massimo: {max(abs(M)):.2f} N·m")
        st.write(f"Taglio massimo: {max(abs(T)):.2f} N")
        risultato_analitico = None
        if tipo_carico == "Uniforme":
            risultato_analitico = soluzione_analitica(L, EJ, q, bc_left, bc_right, tipo_carico, supports)

        if risultato_analitico is not None:
            y_analitico, M_analitico = risultato_analitico
            st.subheader("Confronto con soluzione analitica")
            st.write(f"y_max analitico: {y_analitico*1000:.4f} mm")
            st.write(f"y_max numerico:  {min(y)*1000:.4f} mm")
            errore_y = abs((min(y) - y_analitico) / y_analitico) * 100
            st.write(f"Errore y_max: {errore_y:.4f} %")
            st.write(f"M_max analitico: {M_analitico:.2f} N·m")
            st.write(f"M_max numerico:  {max(abs(M)):.2f} N·m")
            errore_M = abs((max(abs(M)) - M_analitico) / M_analitico) * 100
            st.write(f"Errore M_max: {errore_M:.4f} %")
        else:
            st.info("Confronto analitico non disponibile per questo schema.")

        if risultato_analitico is not None:
            st.subheader("Tabella di convergenza") 
            dati = tabella_convergenza(L, EJ, q, bc_left, bc_right)
            st.table(pd.DataFrame(dati))
        
        st.subheader("Reazioni vincolari")
        reazioni = reazioni_vincolari(T, M, bc_left, bc_right, supports, n)
        for nome, valore in reazioni.items():
            st.write(f"{nome}: {valore}")
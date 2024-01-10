import streamlit as st
import pandas as pd
import numpy as np
 
def R_dominance(data):
    donnee = data
    Points = list(donnee["Point"])
    nb_point = len(Points)
    donnee = donnee.drop(["Point"], axis = 1)
    donnee = donnee.apply(pd.to_numeric, errors='coerce')
    donnee.index = Points
    dominance = np.ones((nb_point,nb_point))
    np.fill_diagonal(dominance, np.zeros(nb_point))
    for i in range(nb_point-1):
        for j in range(i+1 ,nb_point):
            if (donnee.iloc[i] - donnee.iloc[j]).max() > 0 and (donnee.iloc[i] - donnee.iloc[j]).min() >= 0 :
                dominance[i,j] = -1
            elif(donnee.iloc[j] - donnee.iloc[i]).max() > 0 and (donnee.iloc[j] - donnee.iloc[i]).min() >= 0 :
                dominance[j,i] = -1
            else :
                dominance[j,i] = dominance[i,j] = 0
    data_dominance = pd.DataFrame(data = dominance,columns = Points, index = Points)
    return data_dominance
    
def lexico_dominance(data):
    donnee = data
    Points = list(donnee["Point"])
    nb_point = len(Points)
    donnee = donnee.drop(["Point"], axis = 1)
    donnee = donnee.apply(pd.to_numeric, errors='coerce')
    donnee.index = Points
    dominance = np.ones((nb_point,nb_point))
    np.fill_diagonal(dominance, np.zeros(nb_point))
    nb_objetif = donnee.shape[1]
    for i in range(nb_point-1):
        for j in range(i+1 ,nb_point):
            position = donnee.iloc[i] - donnee.iloc[j]
            arret = 0
            for obj in range(nb_objetif):
                if position[obj] > 0 :
                    dominance[i,j]  = -1
                    arret = 1
                    break
                elif  position[obj] < 0:
                    dominance[j,i]  = -1
                    arret = 1
                    break
                    
            if  arret == 0 :
                   dominance[j,i] = dominance[i,j] = 0
                  
    data_dominance = pd.DataFrame(data = dominance,columns = Points, index = Points)
    return data_dominance
    
def extreme_dominance(data, poids):
    donnee = data
    Points = list(donnee["Point"])
    nb_point = len(Points)
    donnee = donnee.drop(["Point"], axis = 1)
    donnee = donnee.apply(pd.to_numeric, errors='coerce')
    donnee.index = Points
    dominance = np.ones((nb_point,nb_point))
    np.fill_diagonal(dominance, np.zeros(nb_point))
    for i in range(nb_point-1):
        for j in range(i+1 ,nb_point):
            if poids.dot(donnee.iloc[i]) - poids.dot(donnee.iloc[j]) > 0  :
                dominance[i,j] = -1
            elif poids.dot(donnee.iloc[i]) - poids.dot(donnee.iloc[j]) < 0  :
                dominance[j,i] = -1
            else :
                dominance[j,i] = dominance[i,j] = 0

    data_dominance = pd.DataFrame(data = dominance,columns = Points, index = Points)
    return data_dominance
    
def max_dominance(data):
    donnee = data
    Points = list(donnee["Point"])
    nb_point = len(Points)
    donnee = donnee.drop(["Point"], axis = 1)
    donnee = donnee.apply(pd.to_numeric, errors='coerce')
    donnee.index = Points
    dominance = np.ones((nb_point,nb_point))
    np.fill_diagonal(dominance, np.zeros(nb_point))
    for i in range(nb_point-1):
        for j in range(i+1 ,nb_point):
            if donnee.iloc[i].max() > donnee.iloc[j].max() :
                dominance[i,j] = -1
            elif donnee.iloc[i].max() < donnee.iloc[j].max() :
                dominance[j,i] = -1
            else :
                dominance[j,i] = dominance[i,j] = 0
    data_dominance = pd.DataFrame(data = dominance,columns = Points, index = Points)
    return data_dominance
    
def cone_dominance(data, coef):
    donnee = data
    Points = list(donnee["Point"])
    nb_point = len(Points)
    donnee = donnee.drop(["Point"], axis = 1)
    donnee = donnee.apply(pd.to_numeric, errors='coerce')
    donnee.index = Points
    dominance = np.ones((nb_point,nb_point))
    np.fill_diagonal(dominance, np.zeros(nb_point))
    nb_objetif = donnee.shape[1]
    for i in range(nb_point-1):
        for j in range(i+1 ,nb_point):
            position = donnee.iloc[i] - donnee.iloc[j]
            if position.min() > 0  or (-position).min() > 0:
                
                arret = 0
                if position.min() > 0 :
                    
                    pos = position
                else :
                    pos = -position
                
                for i1 in range(nb_objetif-1):
                    for j1 in range(i1+1 ,nb_objetif):
                        if pos[i1] * coef > pos[j1] or  pos[j1] > pos[i1]/coef :
                            dominance[j,i] = dominance[i,j] = 0
                            arret = 1
                            break
                    if arret == 1 :
                        break
   
                if  arret == 0 and position.min() > 0 :
                   
                    dominance[i,j] = -1
                elif  arret == 0 :
                    dominance[j,i] = -1
            else :
                dominance[j,i] = dominance[i,j] = 0
                            

    data_dominance = pd.DataFrame(data = dominance,columns = Points, index = Points)
    return data_dominance
    
def rang_pareto(data):
    data_dominance = data
    Point = data.columns
    element = 0
    classement = {}
    classe = 0
    while element != len(Point):
        selection = []
        classe += 1
        for ind in data_dominance.index:
            if data_dominance.loc[ind].min() != -1.:
                element += 1
                selection.append(ind)
        chaine = '     '.join(selection)
        classement["Classe " + str(classe)] =  chaine
        data_dominance = data_dominance.drop(selection, axis = 1)
        data_dominance = data_dominance.drop(selection, axis = 0)
        
    return classement

def affichage(domine)  :             
        st.markdown("**Tableau de dominance  :**")
        st.write(domine)
        st.write("1 : dominant")
        st.write("-1 : dominer")
        st.write("0 : co-dominance")
        classement = pd.DataFrame(list((rang_pareto(domine)).items()), columns = ["Classe", "Points"])
        st.table(classement)

def main():
    st.title("OPTIMISATION MULTIOBJECTIF")

    # Afficher un widget pour télécharger un fichier
    uploaded_file = st.file_uploader("Choisissez un fichier Excel", type=["xls", "xlsx"])

    # Si un fichier est téléchargé
    if uploaded_file is not None:
        st.success("Fichier téléchargé avec succès!")

        # Charger le fichier Excel avec pandas
        df = pd.read_excel(uploaded_file)

        # Afficher le DataFrame
        st.markdown("**Contenu du fichier des solutions :**")
        st.write(df)
        st.markdown("**Contenu du fichier des solutions :**")
        st.write("Nombre de points : " , df.shape[0])
        st.write("Nombre de fonctions objectifs : " , df.shape[1] - 1)
        st.write("Point Nadir :" , df.drop(["Point"],axis = 1).max(axis = 0))
        st.write("Point Idéal : " , df.drop(["Point"],axis = 1).min(axis = 0))
         
        options = ["R dominance", "Lexico dominance","Extrême dominance",  "Cone dominance", "Max dominance"]

        # Barre de choix avec 5 éléments
        choix = st.selectbox("Sélectionnez votre type de dominance :", options)
        if choix == "R dominance" :
            domine = R_dominance(df)
            affichage(domine)
            
        if choix == "Lexico dominance" :
            domine = lexico_dominance(df)
            affichage(domine)
            
        if choix == "Max dominance" :
            domine = max_dominance(df)
            affichage(domine)   
            
        if choix == "Cone dominance" :
            pente = st.number_input("Veuillez saisir la pente du cone")
            if st.button("Valider"):
                domine = cone_dominance(df,pente)
                affichage(domine)

        if choix == "Extrême dominance" :
            valeurs = np.zeros(df.shape[1] - 1)
            for i in range(df.shape[1] - 1):
                valeur_saisie = st.number_input(f"Veuillez saisir la valeur de f{i + 1}",value=1/(df.shape[1] - 1), min_value=0.0, max_value= 1.0 - valeurs.sum())
                valeurs[i] = valeur_saisie
            if st.button("Valider"):
                
                domine = extreme_dominance(df, valeurs)
                affichage(domine)
                    


if __name__ == "__main__":
    main()

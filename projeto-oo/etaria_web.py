import streamlit as st


from minhas_funcoes import calc_media2_notas

st.title("Calcular Faixa Etária")
       
idade = st.number_input("Qual a sua idade? ")

if st.button("Calcular"):
    if idade < 0:
        faixa = "Idade inválida"
    elif idade <= 12:
        faixa = "Criança"
    elif idade <= 19:
        faixa = "Adolescente"
    elif idade <= 59:
        faixa = "Adulto"
    else:
        faixa = "Idoso"
    
    st.write(f"Sua faixa etária é: {faixa}")
    

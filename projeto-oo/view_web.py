import streamlit as st

from minhas_funcoes import calc_media2_notas

st.title("Hello World in Streamlit")
st.subheader("My first web app")
st.text("This is a simple web application using Streamlit.")
st.markdown("Streamlit makes it easy to create web apps for data science and machine learning.")
       
nota1 = st.number_input("Enter the first grade:", min_value=0.0, max_value=10.0, step=0.1)
nota2 = st.number_input("Enter the second grade:", min_value=0.0, max_value=10.0, step=0.1)

if st.button("Calculate Average"):
    media = calc_media2_notas(nota1, nota2)
    st.write(f"The average of the grades is: {media}")

st.write("This is my first web application using Streamlit.")


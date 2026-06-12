import streamlit as st

st.title("KakeiboAI")

income = st.number_input("Monthly Income")

if st.button("Calculate"):
    st.write(f"Your income is ₹{income}")

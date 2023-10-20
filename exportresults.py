from sqlalchemy import create_engine
import streamlit as st
import pandas as pd
from PIL import Image

st.set_page_config(
        page_title="Digital Dream Dashboard",
        page_icon="Ericsson Logo.png",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

image = Image.open('Banner.png')

st.image(image, width=1000, use_column_width="always")

st.header("Welcome to Digital Dream", divider='blue')

query = st.text_area("Insert your query")

driver = '{ODBC Driver 17 for SQL Server}'
odbc_str = 'mssql+pyodbc:///?odbc_connect=' \
           'Driver=' + driver + \
           ';Server=tcp:digital-dream-sql.database.windows.net;PORT=1433' + \
           ';DATABASE=digital-dream-db' + \
           ';Uid=digidrm' + \
           ';Pwd=8miIRF1@#50Kzb?mU$Ze' + \
           ';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=60;'

db_engine = create_engine(odbc_str)

if st.button("Submit Query", type="primary"):
    print("here:"+query)
    df = pd.read_sql(query, db_engine)
    csv = df.to_csv(index=False).encode('utf-8')
    print(csv)
    st.download_button("Press to Download", csv, "file.csv", "text/csv", key='download-csv')
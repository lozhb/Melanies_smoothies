import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

st.title(":cup_with_straw: Customise Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

# Pull BOTH columns you need
my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

pd_df = my_dataframe.to_pandas()

# Optional: show available fruits (don't stop the app)
st.dataframe(pd_df, use_container_width=True)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"].iloc[0]

        st.subheader(f"{fruit_chosen} Nutritional Information")
        resp = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        st.json(resp.json())  # or st.dataframe(resp.json()) if it’s tabular

    time_to_insert = st.button("Submit order")

    if time_to_insert:
        # Safer than string concatenation, but keeping your style:
        my_insert_stmt = f"""
            insert into smoothies.public.orders(ingredients, name_on_order)
            values ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

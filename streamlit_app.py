# Streamlit app for custom smoothie orders
# Co-authored with CoCo

import streamlit as st
import requests
from snowflake.snowpark.functions import col

# App Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name Input
name_on_order = st.text_input("Name on Smoothie:")

if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit names and API search values
my_dataframe = session.table(
    "SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# Convert to Pandas for .loc[]
pd_df = my_dataframe.to_pandas()

# Multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:

    # Store ingredients as comma-separated values
    ingredients_string = ", ".join(ingredients_list)

    # Display nutrition info
    for fruit_chosen in ingredients_list:

        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write(
            f"The search value for {fruit_chosen} is {search_on}."
        )

        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            )

            if smoothiefroot_response.status_code == 200:
                st.dataframe(
                    smoothiefroot_response.json(),
                    use_container_width=True
                )
            else:
                st.error(
                    f"Unable to retrieve nutrition data for {fruit_chosen}"
                )

        except Exception as e:
            st.error(f"API Error: {e}")

    # Submit Order Button
    time_to_insert = st.button("Submit Order")

    if time_to_insert:

        my_insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS
        (INGREDIENTS, NAME_ON_ORDER)
        VALUES
        ('{ingredients_string}', '{name_on_order}')
        """

        session.sql(my_insert_stmt).collect()

        st.success(
            "Your Smoothie is ordered!",
            icon="✅"
        )

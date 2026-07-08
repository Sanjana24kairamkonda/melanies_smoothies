# Streamlit app for custom smoothie orders
# Co-authored with CoCo

import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

name_on_order = st.text_input('Name on Smoothie:')

st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit names and API search values
my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(
    col('FRUIT_NAME'),
    col('SEARCH_ON')
)

# Convert Snowpark DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Fruit picker
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ' '

        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen,
            'SEARCH_ON'
        ].iloc[0]

        st.write(
            'The search value for ',
            fruit_chosen,
            ' is ',
            search_on,
            '.'
        )

        st.subheader(fruit_chosen + ' Nutrition Information')

        try:
            fruit_response = requests.get(
                "https://my.smoothiefroot.com/api/fruit/" + search_on
            )

            st.dataframe(
                data=fruit_response.json(),
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Error retrieving data: {e}")

    time_to_insert = st.button('Submit Order')

    if time_to_insert:

        my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders
        (ingredients, name_on_order)
        VALUES
        ('{ingredients_string.strip()}', '{name_on_order}')
        """

        session.sql(my_insert_stmt).collect()

        st.success('Your Smoothie is ordered!', icon='✅')

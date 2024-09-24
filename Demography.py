import streamlit as st
import pandas as pd
import plotly.express as px
from unidecode import unidecode

# Title and Subtitle
st.title('MSBA 325 - Demography Streamlit App')
st.markdown('_BY Ali Bzeih_', unsafe_allow_html=True)  # Using Markdown to style the subtitle

# Load your dataset
@st.cache_data
def load_data():
    url = 'https://linked.aub.edu.lb/pkgcube/data/f27ed504df388fb0be31097d4d1153ee_20240908_163458.csv'
    return pd.read_csv(url)

data = load_data()

# Update the mapping with exact matches likely from your dataset
district_to_governorate = {
    unidecode('Baabda District'): 'Mount Lebanon Governorate',
    unidecode('Byblos District'): 'North Governorate',
    unidecode('Tyre District'): 'South Governorate',
    unidecode('Bsharri District'): 'North Governorate',
    unidecode('Sidon District'): 'South Governorate',
    unidecode('Batroun District'): 'North Governorate',
    unidecode('Zgharta District'): 'North Governorate',
    unidecode('Keserwan District'): 'North Governorate',
    unidecode('Marjeyoun District'): 'Nabatieh Governorate',
    unidecode('Aley District'): 'Mount Lebanon Governorate',
    unidecode('Matn District'): 'Mount Lebanon Governorate',
    unidecode('Miniyeh-Danniyeh District'): 'Akkar Governorate',
    unidecode('MiniyehaDanniyeh District'): 'Akkar Governorate',
    unidecode('Bint Jbeil District'): 'Nabatieh Governorate',
    unidecode('Hasbaya District'): 'Nabatieh Governorate',
    unidecode('Zahle District'): 'Beqaa Governorate',
    unidecode('ZahlA(c) District'): 'Beqaa Governorate',
    unidecode('Western Beqaa District'): 'Beqaa Governorate',
    unidecode('Tripoli District, Lebanon'): 'North Governorate',
    unidecode('Hermel District'): 'Baalbek-Hermel Governorate'
}

# Function to extract and convert refArea to governorates
data['Governorate'] = data['refArea'].apply(
    lambda url: district_to_governorate.get(
        unidecode(url.split('/')[-1].replace('_', ' ')), 
        unidecode(url.split('/')[-1].replace('_', ' '))
    )
)

# Group by Governorate to count towns
governorate_counts = data.groupby('Governorate').size().reset_index(name='Number of Towns')

# Melt the data to long format
data_long = data.melt(id_vars=['Governorate'], value_vars=['Percentage of Eldelry - 65 or more years ', 'Percentage of Youth - 15-24 years'],
                      var_name='Category', value_name='Percentage')

# Sidebar - Selection
selected_governorate = st.sidebar.selectbox('Select a Governorate', governorate_counts['Governorate'])
elderly = st.sidebar.checkbox('Elderly - 65 or more years')
youth = st.sidebar.checkbox('Youth - 15-24 years')

# Highlight the selected governorate
governorate_counts['Color'] = governorate_counts['Governorate'].apply(lambda x: 'red' if x == selected_governorate else 'blue')

# Plotting the horizontal bar chart
fig_bar = px.bar(governorate_counts, y='Governorate', x='Number of Towns',
                 title='Number of Towns per Governorate', orientation='h',
                 color='Color', color_discrete_map="identity")
fig_bar.update_layout(yaxis_title="Governorate", xaxis_title="Number of Towns", yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_bar)

# Ensure the 'Color' column is included in data_long for plotting
data_long['Color'] = data_long['Governorate'].apply(lambda x: 'red' if x == selected_governorate else 'blue')

# Map the coordinates for plotting
governorate_coordinates = {
    'Mount Lebanon Governorate': (33.8333, 35.5333),
    'North Governorate': (34.4381, 35.8308),
    'South Governorate': (33.2733, 35.1939),
    'Nabatieh Governorate': (33.3772, 35.4839),
    'Beqaa Governorate': (33.8472, 35.9042),
    'Baalbek-Hermel Governorate': (34.0058, 36.2181),
    'Akkar Governorate': (34.5061, 36.0785)
}

data_long['lat'] = data_long['Governorate'].map(lambda x: governorate_coordinates.get(x, (None, None))[0])
data_long['lon'] = data_long['Governorate'].map(lambda x: governorate_coordinates.get(x, (None, None))[1])

# Plotting on the map of Lebanon
fig_geo = px.scatter_geo(
    data_long,
    lat='lat',
    lon='lon',
    text='Governorate',
    size='Percentage',
    projection="natural earth",
    title='Population Distribution in Lebanon',
    hover_name='Governorate',
    hover_data={'Percentage': True, 'lat': False, 'lon': False},
    color='Color',  # Use the same color logic for the map
    color_discrete_map="identity"
)

fig_geo.update_geos(fitbounds="locations", visible=True)
fig_geo.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig_geo)

# Filter the data based on sidebar choices
if elderly and youth:
    filtered_data = data_long[(data_long['Governorate'] == selected_governorate)]
elif elderly:
    filtered_data = data_long[(data_long['Governorate'] == selected_governorate) & 
                              (data_long['Category'] == 'Percentage of Eldelry - 65 or more years ')]
elif youth:
    filtered_data = data_long[(data_long['Governorate'] == selected_governorate) & 
                              (data_long['Category'] == 'Percentage of Youth - 15-24 years')]
else:
    filtered_data = pd.DataFrame(columns=['Governorate', 'Category', 'Percentage'])

# Plotting the box plot
if not filtered_data.empty:
    fig = px.box(filtered_data, x='Governorate', y='Percentage', color='Category', title='Demographic Percentages by Age Group')
    st.plotly_chart(fig)
else:
    st.write("Please select at least one category to display the data.")
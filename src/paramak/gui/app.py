import streamlit
import paramak
from streamlit_image_select import image_select


reactor_image_links = [
  'https://user-images.githubusercontent.com/8583900/99136724-91af6f00-261e-11eb-9956-476b818a0ee3.png',
  'https://user-images.githubusercontent.com/8583900/99136727-94aa5f80-261e-11eb-965d-0ccceb2743fc.png',
  'https://user-images.githubusercontent.com/8583900/99136728-983de680-261e-11eb-8398-51ae433f5546.png',
  # '',
  # '',
  # '',
  # '',
  # '',
  # '',
  # '',
  # '',
  # '',
  # '',
]

reactor_names=[
  '1',
  '2',
  'FlfSystemCodeReactor',
]


selected_reactor_link = image_select(
    label="Select a cat",
    images=reactor_image_links,
    captions=reactor_names
)

# gets the caption name of the selected image
selected_reactor = reactor_names[reactor_image_links.index(selected_reactor)]

if selected_reactor:
  if selected_reactor=='FlfSystemCodeReactor':
    # st.number_input
    
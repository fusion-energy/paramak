import streamlit as st
import paramak
from streamlit_image_select import image_select
import os
from pathlib import Path

reactor_image_links = [
    "https://user-images.githubusercontent.com/8583900/99136724-91af6f00-261e-11eb-9956-476b818a0ee3.png",
    "https://user-images.githubusercontent.com/8583900/99136727-94aa5f80-261e-11eb-965d-0ccceb2743fc.png",
    "https://user-images.githubusercontent.com/8583900/99136728-983de680-261e-11eb-8398-51ae433f5546.png",
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

reactor_names = [
    "1",
    "2",
    "FlfSystemCodeReactor",
]


selected_reactor_link = image_select(
    label="Select a cat",
    images=reactor_image_links,
    captions=reactor_names,
    # index=2
)

# gets the caption name of the selected image
selected_reactor = reactor_names[reactor_image_links.index(selected_reactor_link)]
st.write(selected_reactor)
if selected_reactor:

  if selected_reactor=='FlfSystemCodeReactor':
    # st.number_input
    pass
  
  generate_model = st.button('Generate model')
  
  if generate_model:
    with st.spinner('Building the 3d model'):
      paramak_reactor = paramak.FlfSystemCodeReactor()
      save_path = Path(os.path.realpath(__file__)).parent
      save_html_file = save_path/'reactor.html'
      save_stp_file = save_path/'reactor.stp'
      

      paramak_reactor.export_html_3d(save_html_file)
      with open(save_html_file, 'r') as file:
        html_data = file.read()

      st.components.v1.html(html_data, width=1100, height=800)
      
      paramak_reactor.export_stp(str(save_stp_file))
      with open(save_stp_file, 'r') as file2:
        stp_data = file2.read()
      st.download_button('Download CAD (STP format)', stp_data, file_name='paramak.stp')
      #TODO see if on_click arg can be used to make stp file on demand https://docs.streamlit.io/library/api-reference/widgets/st.download_button

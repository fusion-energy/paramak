import streamlit as st
import paramak
from streamlit_image_select import image_select
import os
from pathlib import Path

st.set_page_config(
    page_title="Paramak",
    page_icon="⚛",
    layout="wide",
)

hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {
                    visibility: hidden;
                    }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

reactor_image_links = [
    "",
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
    "0",
    "1",
    "2",
    "FlfSystemCodeReactor",
]


selected_reactor_index = image_select(
    label="Select a reactor",
    images=reactor_image_links,
    captions=reactor_names,
    return_value="index",  # function returns index instead of image
    index=0,  # initial selected image is 0 which is blank
)

# def export_stp(paramak_reactor, save_stp_file):


# gets the caption name of the selected image
selected_reactor = reactor_names[selected_reactor_index]

st.write(selected_reactor)
if selected_reactor_index not in [0, None]:

    if selected_reactor == "FlfSystemCodeReactor":
        angle = st.number_input("Angle", 180)

    # generate_model = st.button("Generate model")
    # stp_data=None
    # if generate_model:
    with st.spinner("Building the 3d model"):
        paramak_reactor = paramak.FlfSystemCodeReactor(rotation_angle=angle)
        save_path = Path(os.path.realpath(__file__)).parent
        save_html_file = save_path / "reactor.html"

        paramak_reactor.export_html_3d(save_html_file)
        with open(save_html_file, "r") as file:
            html_data = file.read()
        st.components.v1.html(html_data, width=1100, height=800)

        save_stp_file = save_path / "reactor.stp"
        paramak_reactor.export_stp(str(save_stp_file))
        with open(save_stp_file, "r") as file2:
            stp_data = file2.read()

        save_stl_file = save_path / "reactor.stl"
        paramak_reactor.export_stl(str(save_stl_file))
        with open(save_stl_file, "r") as file3:
            stl_data = file3.read()

        save_h5m_file = save_path / "reactor.h5m"
        paramak_reactor.export_dagmc_h5m(str(save_h5m_file))
        with open(save_h5m_file, "r") as file3:
            h5m_data = file3.read()

    st.download_button(
        "Download CAD (STP format)",
        stp_data,
        file_name="paramak.stp",
        # on_click=export_stp(paramak_reactor, save_stp_file)
    )
    st.download_button(
        "Download CAD (STL format)",
        stl_data,
        file_name="paramak.stl",
        # on_click=export_stp(paramak_reactor, save_stp_file)
    )
    st.download_button(
        "Download DAGMC (h5m format)",
        stl_data,
        file_name="paramak.h5m",
        # on_click=export_stp(paramak_reactor, save_stp_file)
    )
    # TODO see if on_click arg can be used to make stp file on demand https://docs.streamlit.io/library/api-reference/widgets/st.download_button

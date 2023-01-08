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

# TODO get images names from https://paramak.readthedocs.io/en/main/API-Reference.html#parametric-reactors
reactor_image_links = [
    "",
    "https://user-images.githubusercontent.com/8583900/211223396-41ed8628-5352-4e7a-8c4a-97914174954e.png",
    "https://user-images.githubusercontent.com/8583900/99136724-91af6f00-261e-11eb-9956-476b818a0ee3.png",
    "https://user-images.githubusercontent.com/8583900/99136728-983de680-261e-11eb-8398-51ae433f5546.png",
    'https://user-images.githubusercontent.com/8583900/99136727-94aa5f80-261e-11eb-965d-0ccceb2743fc.png',
    'https://user-images.githubusercontent.com/8583900/99136719-8e1be800-261e-11eb-907d-a9bafaebdbb8.png',
    'https://user-images.githubusercontent.com/8583900/99136731-9aa04080-261e-11eb-87a5-502708dfebcc.png',
    'https://user-images.githubusercontent.com/8583900/99136734-9e33c780-261e-11eb-837b-16a0bc59f8a7.png',
    'https://user-images.githubusercontent.com/8583900/110224418-4f62b400-7ed3-11eb-85f1-e40dc74f5671.png',
    'https://user-images.githubusercontent.com/40028739/110248118-cf3e5c00-7f6f-11eb-9e68-864c1a1e8676.png',
    'https://user-images.githubusercontent.com/8583900/100032191-5ae01280-2def-11eb-9654-47c3869b3a2c.png',
    'https://user-images.githubusercontent.com/85617935/144303187-8cb71e2d-fc35-450f-a8f4-88b6650d56b7.png',
]

reactor_names = [
    "0",
    "FlfSystemCodeReactor",
    "BallReactor",
    "SingleNullBallReactor",
    "SegmentedBlanketBallReactor",
    "SubmersionTokamak",
    "SingleNullSubmersionTokamak",
    "CenterColumnStudyReactor",
    "EuDemoFrom2015PaperDiagram",
    "IterFrom2020PaperDiagram",
    "SparcFrom2020PaperDiagram",
    "NegativeTriangularityReactor",

]


selected_reactor_index = image_select(
    label="Select a reactor",
    images=reactor_image_links,
    captions=reactor_names,
    use_container_width=False,
    return_value="index",  # function returns index instead of image
    index=0,  # initial selected image is 0 which is blank
)

# gets the caption name of the selected image
selected_reactor = reactor_names[selected_reactor_index]

st.write(selected_reactor)
write_cad_buttons=True
col1, col2, col3 = st.columns([1, 1,1])

if selected_reactor_index not in [0, None]:

    if selected_reactor == "FlfSystemCodeReactor":
        inner_blanket_radius = col1.number_input("inner blanket radius", 100.)
            
        blanket_thickness = col1.number_input("blanket thickness", 70.)
        
        blanket_height = col1.number_input("blanket height", 500.)
        
        lower_blanket_thickness = col1.number_input("lower blanket thickness", 50.)
        
        upper_blanket_thickness = col2.number_input("upper blanket thickness", 40.)
        
        blanket_vv_gap = col2.number_input("blanket vv gap", 20.)
        
        upper_vv_thickness = col2.number_input("upper vv thickness", 10.)
        
        vv_thickness = col3.number_input("vv thickness", 10.)
        
        lower_vv_thickness = col3.number_input("lower vv thickness", 10.)
        
        rotation_angle = col3.number_input("rotation angle", 180.)

    else:
        write_cad_buttons=False
        st.write(f'{selected_reactor} not implemented in GUI yet.')

    if write_cad_buttons: 
        with st.spinner("Building the 3d model"):
            if selected_reactor == "FlfSystemCodeReactor":
                paramak_reactor = paramak.FlfSystemCodeReactor(
                    inner_blanket_radius=inner_blanket_radius,
                    blanket_thickness=blanket_thickness,
                    blanket_height=blanket_height,
                    lower_blanket_thickness=lower_blanket_thickness,
                    upper_blanket_thickness=upper_blanket_thickness,
                    blanket_vv_gap=blanket_vv_gap,
                    upper_vv_thickness=upper_vv_thickness,
                    vv_thickness=vv_thickness,
                    lower_vv_thickness=lower_vv_thickness,
                    rotation_angle=rotation_angle,
                )

            save_path = Path(os.path.realpath(__file__)).parent
            save_html_file = save_path / "reactor.html"

            paramak_reactor.export_html_3d(save_html_file)
            with open(save_html_file, "r") as file:
                html_data = file.read()

            save_stp_file = save_path / "reactor.stp"
            paramak_reactor.export_stp(str(save_stp_file))
            with open(save_stp_file, "r") as file2:
                stp_data = file2.read()

            save_stl_file = save_path / "reactor.stl"
            paramak_reactor.export_stl(str(save_stl_file))
            with open(save_stl_file, "r") as file3:
                stl_data = file3.read()

            # TODO fix so that it works
            # save_h5m_file = save_path / "reactor.h5m"
            # paramak_reactor.export_dagmc_h5m(str(save_h5m_file))
            # with open(save_h5m_file, "r") as file4:
            #     h5m_data = file4.read()
        

            col1_buttons, col2_buttons = st.columns([1,1])
            # TODO see if on_click arg can be used to make stp file on demand https://docs.streamlit.io/library/api-reference/widgets/st.download_button
            col1_buttons.download_button(
                "Download CAD (STP format)",
                stp_data,
                file_name="paramak.stp",
            )
            col2_buttons.download_button(
                "Download CAD (STL format)",
                stl_data,
                file_name="paramak.stl",
            )

            # TODO fix so that it works
            # st.download_button(
            #     "Download DAGMC (h5m format)",
            #     stl_data,
            #     file_name="paramak.h5m",
            # )

            st.components.v1.html(html_data, height=800)
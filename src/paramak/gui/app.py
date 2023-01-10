import os
from pathlib import Path

import paramak
import streamlit as st
from streamlit_image_select import image_select

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
    "https://user-images.githubusercontent.com/8583900/99136727-94aa5f80-261e-11eb-965d-0ccceb2743fc.png",
    "https://user-images.githubusercontent.com/8583900/99136719-8e1be800-261e-11eb-907d-a9bafaebdbb8.png",
    "https://user-images.githubusercontent.com/8583900/99136731-9aa04080-261e-11eb-87a5-502708dfebcc.png",
    "https://user-images.githubusercontent.com/8583900/99136734-9e33c780-261e-11eb-837b-16a0bc59f8a7.png",
    "https://user-images.githubusercontent.com/8583900/110224418-4f62b400-7ed3-11eb-85f1-e40dc74f5671.png",
    "https://user-images.githubusercontent.com/40028739/110248118-cf3e5c00-7f6f-11eb-9e68-864c1a1e8676.png",
    "https://user-images.githubusercontent.com/8583900/100032191-5ae01280-2def-11eb-9654-47c3869b3a2c.png",
    "https://user-images.githubusercontent.com/85617935/144303187-8cb71e2d-fc35-450f-a8f4-88b6650d56b7.png",
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
write_cad_buttons = True
col1, col2, col3 = st.columns([1, 1, 1])

if selected_reactor_index not in [0, None]:

    if selected_reactor == "FlfSystemCodeReactor":
        inner_blanket_radius = col1.number_input("inner blanket radius", value=100.0)
        blanket_thickness = col1.number_input("blanket thickness", value=70.0)
        blanket_height = col1.number_input("blanket height", value=500.0)
        lower_blanket_thickness = col1.number_input("lower blanket thickness", value=50.0)
        upper_blanket_thickness = col2.number_input("upper blanket thickness", value=40.0)
        blanket_vv_gap = col2.number_input("blanket vv gap", value=20.0)
        upper_vv_thickness = col2.number_input("upper vv thickness", value=10.0)
        vv_thickness = col3.number_input("vv thickness", value=10.0)
        lower_vv_thickness = col3.number_input("lower vv thickness", value=10.0)
        rotation_angle = col3.number_input("rotation angle", value=180.0)

    elif selected_reactor == "BallReactor":
        inner_bore_radial_thickness = col1.number_input("inner_bore_radial_thickness", value=10.0)
        inboard_tf_leg_radial_thickness = col1.number_input("inboard_tf_leg_radial_thickness", value=30.0)
        center_column_shield_radial_thickness = col1.number_input("center_column_shield_radial_thickness", value=60.0)
        divertor_radial_thickness = col1.number_input("divertor_radial_thickness", value=150.0)
        inner_plasma_gap_radial_thickness = col1.number_input("inner_plasma_gap_radial_thickness", value=30.0)
        plasma_radial_thickness = col1.number_input("plasma_radial_thickness", value=300.0)
        outer_plasma_gap_radial_thickness = col1.number_input("outer_plasma_gap_radial_thickness", value=30.0)
        firstwall_radial_thickness = col1.number_input("firstwall_radial_thickness", value=30.0)
        blanket_radial_thickness = col2.number_input("firstwall_radial_thickness", value=50.0)
        blanket_rear_wall_radial_thickness = col2.number_input("blanket_rear_wall_radial_thickness", value=30.0)
        elongation = col2.number_input("elongation", value=2.0)
        triangularity = col2.number_input("triangularity", value=0.55)
        plasma_gap_vertical_thickness = col2.number_input("plasma_gap_vertical_thickness", value=50.0)
        divertor_to_tf_gap_vertical_thickness = col2.number_input("divertor_to_tf_gap_vertical_thickness", value=0.0)
        number_of_tf_coils = col2.number_input("number_of_tf_coils", value=12)
        rear_blanket_to_tf_gap = col2.number_input("rear_blanket_to_tf_gap", value=0.0)
        pf_coil_radial_thicknesses = col3.text_input(
            "pf_coil_radial_thicknesses", value="50,40,50", key="input_pf_coil_radial_thicknesses"
        )
        pf_coil_vertical_thicknesses = col3.text_input("pf_coil_vertical_thicknesses", value="60,40,60", key="")
        pf_coil_radial_position = col3.text_input(
            "pf_coil_radial_position", value="500,550,500", key="input_pf_coil_radial_position"
        )
        pf_coil_vertical_position = col3.text_input(
            "pf_coil_vertical_position", value="-250,0,250", key="input_pf_coil_vertical_position"
        )
        pf_coil_case_thicknesses = col3.text_input(
            "pf_coil_case_thicknesses", value="5,5,5", key="input_pf_coil_case_thicknesses"
        )
        outboard_tf_coil_radial_thickness = col3.number_input(
            "outboard_tf_coil_radial_thickness", value=50, key="input_outboard_tf_coil_radial_thickness"
        )
        outboard_tf_coil_poloidal_thickness = col3.number_input(
            "outboard_tf_coil_radial_thickness", value=50, key="input_outboard_tf_coil_poloidal_thickness"
        )
        divertor_position = col3.selectbox("divertor_position", options=["both", "lower", "upper"])
        rotation_angle = col3.number_input("rotation angle", value=180.0)
    else:
        write_cad_buttons = False
        st.write(f"{selected_reactor} not implemented in GUI yet.")

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
            elif selected_reactor == "BallReactor":
                paramak_reactor = paramak.BallReactor(
                    inner_bore_radial_thickness=inner_bore_radial_thickness,
                    inboard_tf_leg_radial_thickness=inboard_tf_leg_radial_thickness,
                    center_column_shield_radial_thickness=center_column_shield_radial_thickness,
                    divertor_radial_thickness=divertor_radial_thickness,
                    inner_plasma_gap_radial_thickness=inner_plasma_gap_radial_thickness,
                    plasma_radial_thickness=plasma_radial_thickness,
                    outer_plasma_gap_radial_thickness=outer_plasma_gap_radial_thickness,
                    firstwall_radial_thickness=firstwall_radial_thickness,
                    blanket_radial_thickness=blanket_radial_thickness,
                    blanket_rear_wall_radial_thickness=blanket_rear_wall_radial_thickness,
                    elongation=elongation,
                    triangularity=triangularity,
                    plasma_gap_vertical_thickness=plasma_gap_vertical_thickness,
                    divertor_to_tf_gap_vertical_thickness=divertor_to_tf_gap_vertical_thickness,
                    number_of_tf_coils=number_of_tf_coils,
                    rear_blanket_to_tf_gap=rear_blanket_to_tf_gap,
                    pf_coil_radial_thicknesses=[float(v) for v in pf_coil_radial_thicknesses.split(",")],
                    pf_coil_vertical_thicknesses=[float(v) for v in pf_coil_vertical_thicknesses.split(",")],
                    pf_coil_radial_position=[float(v) for v in pf_coil_radial_position.split(",")],
                    pf_coil_vertical_position=[float(v) for v in pf_coil_vertical_position.split(",")],
                    pf_coil_case_thicknesses=[float(v) for v in pf_coil_case_thicknesses.split(",")],
                    outboard_tf_coil_radial_thickness=outboard_tf_coil_radial_thickness,
                    outboard_tf_coil_poloidal_thickness=outboard_tf_coil_poloidal_thickness,
                    divertor_position=divertor_position,
                    rotation_angle=rotation_angle,
                )

            save_path = Path(os.path.realpath(__file__)).parent

            save_html_file = save_path / "reactor.html"
            paramak_reactor.export_html_3d(save_html_file)
            with open(save_html_file, "r") as file1:
                html_data = file1.read()

            save_stp_file = save_path / "reactor.stp"
            paramak_reactor.export_stp(str(save_stp_file))
            with open(save_stp_file, "r") as file2:
                stp_data = file2.read()

            # save_stl_file = save_path / "reactor.stl"
            # paramak_reactor.export_stl(str(save_stl_file))
            # with open(save_stl_file, "r") as file3:
            #     stl_data = file3.read()

            # TODO fix so that it works
            # save_h5m_file = save_path / "reactor.h5m"
            # paramak_reactor.export_dagmc_h5m(str(save_h5m_file))
            # with open(save_h5m_file, "r") as file4:
            #     h5m_data = file4.read()

            col1_buttons, col2_buttons = st.columns([1, 1])

            # TODO see if on_click arg can be used to make stp file on demand
            # https://docs.streamlit.io/library/api-reference/widgets/st.download_button
            col1_buttons.download_button(
                "Download CAD (STP format)",
                stp_data,
                file_name="paramak.stp",
            )
            col2_buttons.download_button(
                "Download CAD (HTML format)",
                html_data,
                file_name="paramak.html",
            )

            # this is not currently working, perhaps due to binary files
            # col2_buttons.download_button(
            #     "Download CAD (STL format)",
            #     stl_data,
            #     file_name="paramak.stl",
            # )

            # TODO fix so that it works
            # st.download_button(
            #     "Download DAGMC (h5m format)",
            #     stl_data,
            #     file_name="paramak.h5m",
            # )

        st.components.v1.html(html_data, height=800)

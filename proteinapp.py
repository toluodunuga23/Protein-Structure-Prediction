import streamlit as st
import py3Dmol
from stmol import showmol
import requests
import biotite.structure.io as bsio
import numpy as np
#streamlit run "/Users/toluodunuga/Documents/GitHub/Protein Stucture Prediction/proteinapp.py"


st.sidebar.title("ESMFold")
st.sidebar.write("End-to-end single sequence protein structure predictor based on the ESM 2 language model.")

def render_mol(pdb):
    mol = py3Dmol.view(width=600, height=400)
    mol.addModel(pdb, "pdb")
    mol.setStyle({"cartoon": {"color": "spectrum"}})
    mol.setBackgroundColor("0xeeeeee")
    mol.zoomTo()
    mol.show()
    mol.spin(True)
    showmol(mol, width=600, height=400)

# Protein sequence input
DEFAULT_SEQ = "MVLSEGEWQLVLHVWAKVEADVAGHGQDILIRLFKSHPETLEKFDRVKHLKTEAEMKASEDLKKHGKVEGDFVKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEFTPAVHASLDKFLASVSTVLTSKYR"
txt = st.sidebar.text_area("Input sequence", DEFAULT_SEQ, height=275)

# ESMFold
def update(sequence=txt):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.post('https://api.esmatlas.com/foldSequence/v1/pdb/', headers=headers, data=sequence)
    name = sequence[:3] + sequence[-3:]
    pdb_string = response.content.decode('utf-8')

    with open('predicted.pdb', 'w') as f:
        f.write(pdb_string)

    structure = bsio.load_structure('predicted.pdb', extra_fields={"b_factor"})
    if len(structure) > 0 and not np.isnan(structure.b_factor).any():
        b_value = round(structure.b_factor.mean(), 4)
    else:
        b_value = np.nan

    #Display protein structure
    st.subheader("Predicted protein structure")
    render_mol(pdb_string)

    #plDDT value is sotred in the B-factor field
    st.subheader('plDDT value')
    st.write('plDDT value is a per-residue confidence score for the predicted structure. The higher the value, the more confident the model is in the predicted structure.')
    st.info('plDDT value: '+str(b_value))

    st.download_button(
        label="Download PDB file",
        data=pdb_string,
        file_name=name+'.pdb',
        mime='text/plain',
    )


predict = st.sidebar.button("Predict", on_click=update)

if not predict:
    st.sidebar.write("Enter a protein sequence data!")

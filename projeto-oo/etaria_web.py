# etaria_web.py
import streamlit as st
import joblib
import os
from pathlib import Path
import numpy as np

# --- Caminho absoluto do modelo baseado no arquivo atual ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = Path(BASE_DIR) / "knn_idade_model.joblib"

# --- Função para carregar o modelo com cache (evita reloads a cada interação) ---
# Use st.cache_resource se disponível; se estiver usando uma versão antiga do Streamlit,
# você pode usar st.cache(allow_output_mutation=True).
@st.cache_resource
def carregar_modelo(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Modelo não encontrado em: {path.resolve()}")
    conteudo = joblib.load(path)
    # Se for um dict (como no seu script de treino), extraia model e label_encoder
    if isinstance(conteudo, dict):
        model = conteudo.get("model") or conteudo.get("modelo")  # tenta duas chaves possíveis
        label_encoder = conteudo.get("label_encoder") or conteudo.get("le") or conteudo.get("encoder")
        return {"model": model, "label_encoder": label_encoder}
    # Se não for dict, assumimos que é o modelo puro
    return {"model": conteudo, "label_encoder": None}

# Carrega modelo
try:
    recursos = carregar_modelo(MODEL_PATH)
    modelo = recursos["model"]
    le = recursos["label_encoder"]
except Exception as e:
    st.error(f"Erro ao carregar o modelo: {e}")
    st.stop()

# Verificação simples (útil para debug)
st.write("Modelo carregado:", type(modelo))
if le is not None:
    st.write("Label encoder carregado. Classes:", getattr(le, "classes_", None))

# Interface Streamlit
st.title("Calcular Faixa Etária")
idade = st.number_input("Qual a sua idade?", min_value=0.0, max_value=130.0, step=1.0, value=30.0)

if st.button("Calcular"):
    # Formata entrada conforme o que o modelo espera: array 2D
    X_input = np.array([[idade]])
    try:
        pred = modelo.predict(X_input)
    except Exception as e:
        st.error(f"Erro ao predizer com o modelo: {e}")
    else:
        # pred pode já ser rótulo (str) ou label codificado (int). Se houver label_encoder, decodificamos.
        if le is not None:
            # pred pode ser array numpy ints, convert para int antes de inverse_transform
            try:
                pred_labels = le.inverse_transform(pred)
                faixa = pred_labels[0]
            except Exception as e:
                st.error(f"Erro ao decodificar rótulo com LabelEncoder: {e}")
                faixa = str(pred[0])
        else:
            faixa = str(pred[0])
            
        st.success(f"Sua faixa etária é: {faixa}")

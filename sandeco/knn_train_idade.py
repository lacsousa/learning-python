# knn_train_idade.py
import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# --- Configurações ---
CSV_PATH = Path("dados/dataset_idade_faixa_etaria.csv")  # ajuste se necessário
RANDOM_STATE = 42
TEST_SIZE = 0.2

# --- Carregar dados ---
if not CSV_PATH.exists():
    raise FileNotFoundError(f"CSV não encontrado: {CSV_PATH.resolve()}")

df = pd.read_csv(CSV_PATH)

# Verificar colunas esperadas
assert "idade" in df.columns and "faixa_etaria" in df.columns, \
    "O CSV precisa ter as colunas 'idade' e 'faixa_etaria'"

# --- Preparação ---
X = df[["idade"]].copy()   # DataFrame com 1 coluna
y = df["faixa_etaria"].copy()

# Codificar rótulos (labels)
le = LabelEncoder()
y_enc = le.fit_transform(y)   # salva le.classes_ se quiser converter de volta

# --- Separar treino / teste ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y_enc
)

# --- Pipeline e Grid Search ---
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier())
])

param_grid = {
    "knn__n_neighbors": [1, 3, 5, 7, 9, 11, 15],
    "knn__weights": ["uniform", "distance"],
    "knn__p": [1, 2]  # p=1 -> Manhattan, p=2 -> Euclidean
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

grid = GridSearchCV(
    pipeline,
    param_grid,
    cv=cv,
    scoring="accuracy",
    n_jobs=-1,
    verbose=1
)

grid.fit(X_train, y_train)

# --- Avaliação ---
best_model = grid.best_estimator_
print("Melhor(s) hiperparâmetro(s):", grid.best_params_)
print(f"Melhor score (CV) obtido: {grid.best_score_:.4f}")

y_pred = best_model.predict(X_test)

acc = accuracy_score(y_test, y_pred)
print(f"\nAcurácia no conjunto de teste: {acc:.4f}\n")

# classification report com nomes das classes decodificados
y_test_labels = le.inverse_transform(y_test)
y_pred_labels = le.inverse_transform(y_pred)
print("Classification report:\n")
print(classification_report(y_test_labels, y_pred_labels))

# Matriz de confusão (plot)
cm = confusion_matrix(y_test_labels, y_pred_labels, labels=le.classes_)
plt.figure(figsize=(7, 5))
sns.heatmap(cm, annot=True, fmt="d", xticklabels=le.classes_, yticklabels=le.classes_, cmap="Blues")
plt.xlabel("Predito")
plt.ylabel("Verdadeiro")
plt.title("Matriz de Confusão - KNN")
plt.tight_layout()
plt.show()

# --- Salvar modelo e encoder ---
model_path = Path("knn_idade_model.joblib")
joblib.dump({"model": best_model, "label_encoder": le}, model_path)
print(f"Modelo salvo em: {model_path.resolve()}")

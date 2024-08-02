from joblib import load
import logging
from ..utils.utils import adjust_values

def load_model(model_path):
    try:
        return load(model_path)
    except Exception as e:
        logging.error(f"Error cargando el modelo: {e}")
        return None

def decide_action(candles, decisionModel):
    try:
        sample = [float(c[0]) for c in candles]
        sample = adjust_values(sample)
        prediction = decisionModel.predict([sample])
        return prediction[0]
    except Exception as e:
        logging.error(f"Error tomando decisión: {e}")
        return None
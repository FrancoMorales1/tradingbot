from joblib import load
import logging

def load_model(model_path):
    try:
        return load(model_path)
    except Exception as e:
        logging.error(f"Error cargando el modelo: {e}")
        return None

def decide_action(candles, decisionModel):
    try:
        sample = [float(c[0]) for c in candles]
        prediction = decisionModel.predict([sample])
        return prediction[0]
    except Exception as e:
        logging.error(f"Error tomando decisión: {e}")
        return None
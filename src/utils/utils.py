import logging

def get_precision(symbol, client):
    try:
        info = client.get_symbol_info(symbol)
        filters = info['filters']
        for f in filters:
            if f['filterType'] == 'LOT_SIZE':
                step_size = f['stepSize']
                # Obtener el número de decimales
                precision = len(step_size.split('1')[0]) - 1
                return precision
    except Exception as e:
            logging.error(f"Error obteniendo precisión: {e}")
            return 2

def round_quantity(quantity, precision):
    return round(quantity, precision)

def adjust_values(array):
    result = []
    for subarray in array:
        min_value = min(subarray)
        adjusted_subarray = [value - min_value for value in subarray]
        result.append(adjusted_subarray)
    return result
# utils/mapbox_motoboy.py
"""
Integração Mapbox + Motoboy App
- Carregamento seguro do .env e MAPBOX_TOKEN
- Geocodificação com Mapbox + fallback para erro
- Cálculo de distância/rota (Mapbox Driving + fallback Haversine)
- Cache inteligente, cálculo de valor de entrega e funções completas para despacho
- Código limpo, tipado e com tratamento de erros
"""

import os
import sys
from pathlib import Path
from urllib.parse import quote
from typing import Optional, Tuple
import requests

# Adiciona raiz do projeto ao path (necessário para importar database e haversine)
sys.path.append(str(Path(__file__).resolve().parent.parent))

from database import get_db
from .haversine import haversine  # fallback distância em linha reta

# Carrega .env da raiz do projeto
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
if not MAPBOX_TOKEN:
    print("[WARNING] MAPBOX_TOKEN não configurado. API Mapbox não funcionará.")


# ==================== GEOCODING ====================
def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Geocodifica endereço usando Mapbox Geocoding API.
    Retorna (lat, lng) ou None se falhar.
    """
    if not address or not MAPBOX_TOKEN:
        print(f"[ERRO] Endereço vazio ou MAPBOX_TOKEN não configurado: {address}")
        return None

    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{quote(address)}.json"
    params = {
        "access_token": MAPBOX_TOKEN,
        "limit": 1,
        "country": "BR",
        "language": "pt",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        features = data.get("features", [])

        if features:
            lng, lat = features[0]["center"]
            return lat, lng
        else:
            print(f"[ERRO] Nenhuma coordenada encontrada para: {address}")
            return None
    except requests.RequestException as e:
        print(f"[ERRO] Falha na requisição Mapbox Geocoding: {e}")
        return None


# ==================== CÁLCULO DE DISTÂNCIA / ROTA ====================
def get_directions(origin: Tuple[float, float], destination: Tuple[float, float]) -> Optional[dict]:
    """
    Retorna rota via Mapbox Driving API: distância (m) e duração (s)
    Fallback para None se falhar.
    """
    if not origin or not destination or not MAPBOX_TOKEN:
        return None

    origin_str = f"{origin[1]},{origin[0]}"  # lng, lat
    dest_str = f"{destination[1]},{destination[0]}"
    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{origin_str};{dest_str}"
    params = {"access_token": MAPBOX_TOKEN, "geometries": "geojson", "overview": "full", "steps": "false"}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        routes = data.get("routes", [])
        if routes:
            route = routes[0]
            return {"distance": route.get("distance", 0), "duration": route.get("duration", 0)}
    except Exception as e:
        print(f"[WARNING] Falha ao obter rota Mapbox: {e}")
    return None


def get_distance(origin: Tuple[float, float], destination: Tuple[float, float]) -> float:
    """
    Calcula distância em km. Usa Mapbox Driving API se disponível, senão fallback Haversine.
    """
    rota = get_directions(origin, destination)
    if rota:
        return rota['distance'] / 1000.0
    return haversine(origin, destination)


# ==================== CACHE INTELIGENTE ====================
def calcular_distancia_tempo(
    restaurante_id: int,
    endereco_origem: str,
    endereco_destino: str,
    usar_cache: bool = True
) -> Tuple[Optional[float], Optional[int]]:
    """
    Calcula distância (km) e tempo (min) entre dois endereços com cache inteligente.
    """
    db = get_db()

    if usar_cache:
        cache = db.buscar_distancia_cache(restaurante_id, endereco_origem, endereco_destino)
        if cache:
            return cache['distancia_km'], cache['tempo_estimado_min']

    coords_origem = geocode_address(endereco_origem)
    coords_destino = geocode_address(endereco_destino)

    if not coords_origem or not coords_destino:
        return None, None

    rota = get_directions(coords_origem, coords_destino)
    if not rota:
        # fallback Haversine
        distancia_km = haversine(coords_origem, coords_destino)
        tempo_min = round(distancia_km / 0.4)  # assume média 25 km/h (~0.4 km/min)
    else:
        distancia_km = round(rota['distance'] / 1000, 2)
        tempo_min = round(rota['duration'] / 60)

    if usar_cache:
        db.salvar_distancia_cache(restaurante_id, endereco_origem, endereco_destino, distancia_km, tempo_min)

    return distancia_km, tempo_min


# ==================== VALOR DE ENTREGA ====================
def calcular_valor_entrega(restaurante_id: int, distancia_km: float) -> float:
    db = get_db()
    config = db.buscar_config_restaurante(restaurante_id)
    if not config:
        return 0.0
    taxa_base = config['taxa_entrega_base']
    distancia_base = config['distancia_base_km']
    taxa_extra = config['taxa_km_extra']
    if distancia_km <= distancia_base:
        return taxa_base
    return round(taxa_base + (distancia_km - distancia_base) * taxa_extra, 2)


# ==================== FUNÇÃO COMPLETA ====================
def processar_entrega_completa(restaurante_id: int, endereco_restaurante: str, endereco_cliente: str) -> Optional[dict]:
    distancia_km, tempo_min = calcular_distancia_tempo(restaurante_id, endereco_restaurante, endereco_cliente)
    if distancia_km is None or tempo_min is None:
        return None
    valor_entrega = calcular_valor_entrega(restaurante_id, distancia_km)
    return {"distancia_km": distancia_km, "tempo_estimado_min": tempo_min, "valor_entrega": valor_entrega}


def invalidar_cache_restaurante(restaurante_id: int) -> bool:
    db = get_db()
    return db.invalidar_cache_restaurante(restaurante_id)

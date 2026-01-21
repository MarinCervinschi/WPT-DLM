from fastapi import WebSocket
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Dizionario: vehicle_id -> lista di websocket connesse per quel veicolo
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, vehicle_id: str):
        """Connette un client WebSocket per ricevere telemetrie di un veicolo specifico."""
        await websocket.accept()
        if vehicle_id not in self.active_connections:
            self.active_connections[vehicle_id] = []
        self.active_connections[vehicle_id].append(websocket)
        logger.info(f"Client connesso per veicolo {vehicle_id}. Totale connessioni: {len(self.active_connections[vehicle_id])}")

    def disconnect(self, websocket: WebSocket, vehicle_id: str):
        """Disconnette un client WebSocket."""
        if vehicle_id in self.active_connections and websocket in self.active_connections[vehicle_id]:
            self.active_connections[vehicle_id].remove(websocket)
            if not self.active_connections[vehicle_id]:
                del self.active_connections[vehicle_id]
            logger.info(f"Client disconnesso da veicolo {vehicle_id}")

    async def send_to_vehicle_clients(self, vehicle_id: str, message: dict):
        """Invia telemetria a tutti i client connessi per un veicolo specifico."""
        if vehicle_id not in self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections[vehicle_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Errore durante l'invio WebSocket a veicolo {vehicle_id}: {e}")
                disconnected.append(connection)
        
        # Rimuovi connessioni fallite
        for connection in disconnected:
            self.disconnect(connection, vehicle_id)

# Istanza globale da importare dove serve
ws_manager = ConnectionManager()
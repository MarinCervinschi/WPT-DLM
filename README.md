# WPT-DLM
This project implements a smart energy orchestration system for wireless charging hubs. It utilizes IoT telemetry to monitor State of Charge (SoC) and a Dynamic Load Management logic to shift grid capacity to critical users, maximizing throughput and efficiency.

## MQTT Topics
### Publishers
1. INFO
    - [x] `iot/hubs/{hub_id}/info`  - `retain=True`  
    - [x] `iot/hubs/{hub_id}/nodes/{node_id}/info`  - `retain=True` 

2. STATUS
    - [x] `iot/hubs/{hub_id}/status`  
    - [x] `iot/hubs/{hub_id}/nodes/{node_id}/status` 

3. TELEMETRY
    - [x] `iot/vehicles/{vehicle_id}/telemetry`  
    - [x] `iot/hubs/{hub_id}/nodes/{node_id}/telemetry` 

4. DLM
    - [x] `iot/hubs/{hub_id}/dlm/events` 

5. Charging Request
    - [x] `iot/hubs/{hub_id}/requests` 

### Subscribers (Cloud)
1. API (brain)
    - [x] `iot/hubs/+/info`  
    - [x] `iot/hubs/+/nodes/+/info`  
    - [x] `iot/hubs/+/dlm/events`  
    - [x] `iot/hubs/+/nodes/+/status` 
    - [x] `iot/vehicles/+/telemetry` 

2. Telegraf
    - [x] `iot/hubs/+/status`  
    - [x] `iot/hubs/+/nodes/+/status`  
    - [x] `iot/hubs/+/nodes/+/telemetry` 
    - [x] `iot/vehicles/+/telemetry`  




<!-- eraser-additional-content -->
## Diagrams
<!-- eraser-additional-files -->
<a href="/docs/diagrams/README-WPT-DLM Architecture-1.eraserdiagram" data-element-id="YNlSBabyQ0ELAIbAE9SHY"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----c7b53ce45e51530a9d0f2df98907719f-WPT-DLM-Architecture.png" alt="" data-element-id="YNlSBabyQ0ELAIbAE9SHY" /></a>
<a href="/docs/diagrams/README-Level 2&3 - Cloud-2.eraserdiagram" data-element-id="z1fLtN1Pi2Ed9TSYLy_mm"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----fc3d3360f393d538327fa60917831005-Level-2-3---Cloud.png" alt="" data-element-id="z1fLtN1Pi2Ed9TSYLy_mm" /></a>
<a href="/docs/diagrams/README-WPT-DLM Communications-3.eraserdiagram" data-element-id="SzsOyQy3vm1-rzsHEhoXi"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----e17c675359ba1183ef18528c9b05777b-WPT-DLM-Communications.png" alt="" data-element-id="SzsOyQy3vm1-rzsHEhoXi" /></a>
<a href="/docs/diagrams/README-PostgresSQL database-4.eraserdiagram" data-element-id="YiIdFMM5JvimPrVneXaL0"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----e633655e840814ac865956cccfdd9c54-PostgresSQL-database.png" alt="" data-element-id="YiIdFMM5JvimPrVneXaL0" /></a>
<a href="/docs/diagrams/README-Sequence Diagram of /recommendations-5.eraserdiagram" data-element-id="yBDGnZ1tXTITsJNfmO0_R"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----fe55e0517ccdb9bc18d00ddf9ff2faff-Sequence-Diagram-of--recommendations.png" alt="" data-element-id="yBDGnZ1tXTITsJNfmO0_R" /></a>
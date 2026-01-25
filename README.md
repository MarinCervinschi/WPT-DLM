<p><a target="_blank" href="https://app.eraser.io/workspace/ckMgfMWXETpfMUeeZgOh" id="edit-in-eraser-github-link"><img alt="Edit in Eraser" src="https://firebasestorage.googleapis.com/v0/b/second-petal-295822.appspot.com/o/images%2Fgithub%2FOpen%20in%20Eraser.svg?alt=media&amp;token=968381c8-a7e7-472a-8ed6-4a6626da5501"></a></p>

# WPT-DLM
This project implements a smart energy orchestration system for wireless charging hubs. It utilizes IoT telemetry to monitor State of Charge (SoC) and a Dynamic Load Management logic to shift grid capacity to critical users, maximizing throughput and efficiency.

## MQTT Topics
### Publishers
1. INFO
    - [ ] `iot/hubs/{hub_id}/info`  - `retain=True`  
    - [ ] `iot/hubs/{hub_id}/nodes/{node_id}/info`  - `retain=True` 

2. STATUS
    - [ ] `iot/hubs/{hub_id}/status`  
    - [ ] `iot/hubs/{hub_id}/nodes/{node_id}/status` 

3. TELEMETRY
    - [ ] `iot/vehicles/{vehicle_id}/telemetry`  
    - [ ] `iot/hubs/{hub_id}/nodes/{node_id}/telemetry` 

4. DLM
    - [ ] `iot/hubs/{hub_id}/dlm/events` 

5. Charging Request
    - [ ] `iot/hubs/{hub_id}/requests` 

### Subscribers (Cloud)
1. API (brain)
    - [ ] `iot/hubs/+/info`  
    - [ ] `iot/hubs/+/nodes/+/info`  
    - [ ] `iot/hubs/+/dlm/events`  
    - [ ] `iot/hubs/+/nodes/+/status` 
    - [ ] `iot/vehicles/+/telemetry` 

2. Telegraf
    - [ ] `iot/hubs/+/status`  
    - [ ] `iot/hubs/+/nodes/+/status`  
    - [ ] `iot/hubs/+/nodes/+/telemetry` 
    - [ ] `iot/vehicles/+/telemetry`  




<!-- eraser-additional-content -->
## Diagrams
<!-- eraser-additional-files -->
<a href="/README-WPT-DLM Architecture-1.eraserdiagram" data-element-id="YNlSBabyQ0ELAIbAE9SHY"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----c7b53ce45e51530a9d0f2df98907719f-WPT-DLM-Architecture.png" alt="" data-element-id="YNlSBabyQ0ELAIbAE9SHY" /></a>
<a href="/README-Level 2&3 - Cloud-2.eraserdiagram" data-element-id="z1fLtN1Pi2Ed9TSYLy_mm"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----fc3d3360f393d538327fa60917831005-Level-2-3---Cloud.png" alt="" data-element-id="z1fLtN1Pi2Ed9TSYLy_mm" /></a>
<a href="/README-WPT-DLM Communications-3.eraserdiagram" data-element-id="SzsOyQy3vm1-rzsHEhoXi"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----e17c675359ba1183ef18528c9b05777b-WPT-DLM-Communications.png" alt="" data-element-id="SzsOyQy3vm1-rzsHEhoXi" /></a>
<a href="/README-PostgresSQL database-4.eraserdiagram" data-element-id="YiIdFMM5JvimPrVneXaL0"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----e633655e840814ac865956cccfdd9c54-PostgresSQL-database.png" alt="" data-element-id="YiIdFMM5JvimPrVneXaL0" /></a>
<a href="/README-Sequence Diagram of /recommendations-5.eraserdiagram" data-element-id="yBDGnZ1tXTITsJNfmO0_R"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----fe55e0517ccdb9bc18d00ddf9ff2faff-Sequence-Diagram-of--recommendations.png" alt="" data-element-id="yBDGnZ1tXTITsJNfmO0_R" /></a>
<!-- end-eraser-additional-files -->
<!-- end-eraser-additional-content -->
<!--- Eraser file: https://app.eraser.io/workspace/ckMgfMWXETpfMUeeZgOh --->
# Unifi SMS Gateway

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kiall&repository=unifi-sms-gateway&category=Integration)

[![Open your Home Assistant instance and show the add app repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fkiall%2Funifi-sms-gateway)

## Features

* Supports Unifi ULTE-Pro - Tested with EU version.
* Basic SIM status (Current IMEI, Phone Number, Network Operator, Stored SMS Count)
* Send SMS messages:
  * `notify` entities for pre-registered destination numbers
  * `unifi_sms_gateway.send_message` service for arbitrary destination numbers
* Limited SMS receive support:
  * A `latest_sms` sensor entity with message, sender, timestamp

## Installation

1. Add repository to [HACS](https://hacs.xyz/):<br/>[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kiall&repository=unifi-sms-gateway&category=Integration)
2. Install "Unifi SMS Gateway" Componment via [HACS](https://hacs.xyz/)
   * Do NOT setup the compoment manually at this point
   * Restart Home Assistant
2. Add repository to App/Addon store:<br/>[![Open your Home Assistant instance and show the add app repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fkiall%2Funifi-sms-gateway)
   * Provide the IP, SSH user, SSH password for your ULTE-Pro
   * API Key - Enter anything. This is a credential used by the Component to talk to the Addon
3. Start the App/Addon
4. Go to Home Assistant Devices/Services page & add the discovered Unifi SMS Gateway integration
5. Optional: Reconfigure the discovered integration to add pre-registered destination numbers

## Usage

### Send a SMS to a arbitrary destination number:

```yaml
alias: Send SMS to arbitrary Number
description: ""
triggers: []
conditions: []
mode: single
actions:
  - action: unifi_sms_gateway.send_message
    metadata: {}
    data:
      destination_number: "0861234567"
      message: Test Message
```

### Send a SMS to a pre-registered destination number:

```yaml
alias: Send SMS to Pre-Registered Number
description: ""
triggers: []
conditions: []
mode: single
actions:
  - action: notify.send_message
    metadata: {}
    target:
      entity_id: notify.unifi_sms_gateway_sms_0861234567
    data:
      message: Test Message
```

### Act upon incoming SMS messages

```yaml
alias: Add Incoming SMS messages to Shopping List
description: ""
triggers:
  - trigger: state
    entity_id:
      - sensor.unifi_sms_gateway_latest_sms
conditions: []
mode: single
actions:
  - action: todo.add_item
    metadata: {}
    target:
      entity_id: todo.shopping_list
    data:
      item: {{ trigger.to_state.state }} (SMS Sender: {{ trigger.to_state.attributes.sender }})
```


## Acknowledgements

Originally based upon https://github.com/CppBunny/unifi_sms_gateway/

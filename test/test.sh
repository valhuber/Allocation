curl -X POST "http://localhost:5656/api/Payment/" -H  "accept: application/vnd.api+json" -H  "Content-Type: application/json" -d "{  \"data\": {    \"attributes\": {      \"Amount\": 100,      \"AmountUnAllocated\": 0,      \"CustomerId\": \"ALFKI\"    },    \"type\": \"Payment\"  }}"
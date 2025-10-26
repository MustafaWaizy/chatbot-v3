from router_phase3 import initialize_model, route_message

initialize_model()

# Test Cases 
test_inputs = [
    "unity to serve members",
    "sdfsdgsdgsdgsgsdgsg",
    "Mariamm",
    "Mustaf Waizy",
    "ultanzada?"
]

for input_text in test_inputs:
    print(f"User: {input_text}")
    response = route_message(input_text)
    print(f"Bot: {response}\n{'-'*50}")

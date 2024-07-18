import replicate
import os, requests





api_token = os.getenv("server_key")


client = replicate.Client(api_token=api_token)




waste_mapping = {
    # Green Bin (Food Waste)
    'apple': 'green',
    'apple core': 'green',
    'banana': 'green',
    'banana peel': 'green',
    'orange peel': 'green',
    'orange rind': 'green',
    'lettuce': 'green',
    'salad': 'green',
    'carrot': 'green',
    'carrot peel': 'green',
    'cooked rice': 'green',
    'cooked pasta': 'green',
    'coffee grounds': 'green',  
    'tea bag': 'green',

    # Blue Bin (Recyclable Materials)
    'plastic bottle': 'blue',
    'water bottle': 'blue',
    'soda bottle': 'blue',
    'juice box': 'blue', 
    'milk carton': 'blue',  
    'plastic cup': 'blue',
    'aluminum can': 'blue',
    'soda can': 'blue',
    'beer can': 'blue',
    'cardboard box': 'blue',
    'cardboard': 'blue',

    # Black Bin (General Waste)
    'chip bag': 'black',
    'crisp packet': 'black',
    'candy wrapper': 'black',
    'sweet wrapper': 'black',
    'plastic-coated paper': 'black',
    'used napkin': 'black',
    'greasy pizza box': 'black',
}





def generate_description(image):


    input={
        "image": image,
        "top_p": 1,
        "prompt": f"Identify the waste type in the image. The waste type one out of {waste_mapping} give the type as key and the value associated with the key is the waste item. For example, if the waste type is 'apple', your response should be 'The item is an 'apple' and classified as 'green'.",
        "max_tokens": 1024,
        "temperature": 0.2
    }
    
    output = client.run(

        "yorickvp/llava-13b:b5f6212d032508382d61ff00469ddda3e32fd8a0e75dc39d8a4191bb742157fb",
        input=input

        )

    return "".join(output)


##Documentation Followed(👇🏻)
##https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-diffusion-1-0-text-image.html 
## https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/invoke_model.html#invoke-model
## https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/put_object.html
## boto3 aws documentation based on Services Called. 
## https://www.geeksforgeeks.org/python-datetime-datetime-class/

import json
import base64
import datetime

#1. import boto3
import boto3

#2. Create client connection with Bedrock and S3 Services 
client_bedrock = boto3.client('bedrock-runtime')
client_s3 = boto3.client('s3')

def lambda_handler(event, context):
#3 save  input (prompt) as variable
    input_prompt=event['prompt']
    print(input_prompt)
    
#4. Create a Request Syntax 
    modelId = 'stability.stable-diffusion-xl-v1'
    accept = 'application/json'
    contentType = 'application/json'
## Define Body - https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-diffusion-1-0-text-image.html
    body=json.dumps({
        "text_prompts": [
            {
                "text": input_prompt,
                "weight": 1
            }
        ],
        ## "height": int,
        ## "width": int,
        "cfg_scale": 10,
        ##"clip_guidance_preset": string,
        ##"sampler": string,
        ##"samples",
        "seed": 0,
        "steps": 30,
        ##"style_preset": string,
        ##"extras" :JSON object
        
                })

    request_bedrock = client_bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
                                    
    print(request_bedrock)


#5. 5a. Retrieve from Dictionary, 5b. Convert Streaming Body to Byte using json load 5c. Print

    response_bedrock_bytes=json.loads(request_bedrock['body'].read())
    print(response_bedrock_bytes)
#6. 6a. Retrieve data with artifact key, 6b. Import Base 64, 6c. Decode from Base64 -

    response_bedrock_base64 = response_bedrock_bytes['artifacts'][0]['base64']
    response_bedrock_finalimage = base64.b64decode(response_bedrock_base64)
    print(response_bedrock_finalimage)

#7. 7a. Upload the File to S3 using Put Object Method – Link 7b. Import datetime 7c.Generate the image name to be stored in S3
##https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/put_object.html 

    Bucket='posterdesignwithbedrock'
    poster_name = 'posterName'+ datetime.datetime.today().strftime('%Y-%M-%D-%M-%S') ##https://www.geeksforgeeks.org/python-datetime-datetime-class/
    
    response_s3 = client_s3.put_object(
        #Bucket='posterdesignwithbedrock',
        Bucket=Bucket,
        Body=response_bedrock_finalimage,
        Key=poster_name)

#8. Generate Pre-Signed URL -
##https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/generate_presigned_url.html 

    #generate_presigned_url= client_s3.generate_presigned_url(ClientMethod, Params=None, ExpiresIn=3600, HttpMethod=None)
    generate_presigned_url= client_s3.generate_presigned_url('get_object', Params={'Bucket':Bucket,'Key':poster_name}, ExpiresIn=300, HttpMethod=None)

    print(generate_presigned_url)


    return {
        'statusCode': 200,
        #'body': json.dumps('Hello from Lambda!')
        'body': generate_presigned_url
    }

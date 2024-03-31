
import os, zipfile, boto3, json

def zipdir(path, ziph, exclude, base_path):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            if file == exclude:
                continue
            file_path = os.path.join(root, file)
            # Generate relative archive name based on the modified base_path
            arcname = os.path.relpath(file_path, base_path)
            ziph.write(file_path, arcname)

def upload_to_lambda(zip_filename, function_name, region_name):
    lambda_client = boto3.client('lambda', region_name=region_name)
  
    with open(zip_filename, 'rb') as zip_file:
        zip_bytes = zip_file.read()
        
    response = lambda_client.update_function_code(
        FunctionName=function_name,
        ZipFile=zip_bytes,
        Publish=True  # Automatically publish a new version
    )
    return response

if __name__ == '__main__':
    conf_json = os.getenv('BD530_PROJECT_CONF')
    configuration = json.loads(conf_json)
    src_folder = 'src'
    zip_filename = 'main.zip'
    lambda_function_name = configuration['aws']['lambda']
    region_name = configuration['aws']['region_name']

    base_path = os.path.abspath(src_folder)
    script_name = os.path.basename(__file__)
    
    # zip up the folder for lambda
    with zipfile.ZipFile('main.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(src_folder, zipf, script_name, base_path)
    print(f"Created 'main.zip' with the contents of '{src_folder}' excluding '{script_name}'")

    # upload to aws
    response = upload_to_lambda(zip_filename, lambda_function_name, region_name)
    print(f"Uploaded '{zip_filename}' to Lambda function '{lambda_function_name}'. Response: {response}")

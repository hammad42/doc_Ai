def hello(request):
    import re
    request_json = request.get_json()#cloud function request json which contains request 
    if request_json:
        source_url = request_json['source_url']#request key value
        print("source_url="+source_url)
    import sep_blob_bucket as bb
    import storage_download
    import storage_upload
    bucket_and_blob=bb.regex_(source_url)
    bucket_and_blob=re.split('[+]',bucket_and_blob)
    bucket_name=bucket_and_blob[0]#bucket_name
    print(bucket_name)
    prefix=bucket_and_blob[1]#prefix_name
    print(prefix)#blob name

    ### seperating filename from blob name

    exact_file_name_list = re.split("[/]", prefix)#seperating file nmae from blob name
    exact_file_name=exact_file_name_list[-1]#file_name
    print(exact_file_name)
    exact_file_name_without_ext=re.split("[.]",exact_file_name)

    exact_file_name_without_ext=exact_file_name_without_ext[0]
    print(exact_file_name_without_ext)

    #defining variable for document aI

    import uuid
    uuid=str(uuid.uuid1())
    project_id= 'elaborate-howl-285701'
    location = 'us' # Format is 'us' or 'eu'
    processor_id = '7edfadad4740f14b' # Create processor in Cloud Console
    gcs_input_uri = source_url
    gcs_output_uri = "gs://context_primary/Forms/Processed"
    gcs_output_uri_prefix = exact_file_name_without_ext+uuid+'.json'

    from google.cloud import documentai_v1beta3 as documentai
    from google.cloud import storage
    from google.protobuf.json_format import MessageToJson
    import proto
    #import os
    #os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:\gcp_credentials\elaborate-howl-285701-105c2e8355a8.json"

    client = documentai.DocumentProcessorServiceClient()
    destination_uri = f"{gcs_output_uri}/{gcs_output_uri_prefix}"
    print('destination_uri='+destination_uri)

    #downloading pdf blob
    match = re.match(r'gs://([^/]+)/(.+)', source_url)
    file_path = match.group(2)
    bucket_name = match.group(1)
    image_content = storage_download.download_blob(bucket_name, file_path).download_as_bytes()
    #image_content = storage.download_blob(bucket_name, file_path).download_as_bytes()
    #image_content = blob_.download_as_bytes()#pdf as bytes

    #setting attributes for request to document ai

    document = {"content": image_content, "mime_type": "application/pdf"}
    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"
    request = {"name": name, "document": document}
    result = client.process_document(request=request)
    document = result.document
    json_string = proto.Message.to_json(document)
    #print(json_string)
    #x=" ".join(json_string.split())

    import json
    #uploading_string = json.loads(x)
    uploading_string = json.loads(json_string)
    print(uploading_string.keys())# all keys for detected pdf

    #### pagenumber,dimensions,layout,paragraph,formfields

    for t in uploading_string['pages']:#removing unneccesory keys
        t.pop('detectedLanguages')
        t.pop('blocks')
        t.pop('lines')
        t.pop('tokens')
        t.pop('tables')
        t.pop('image')
        t.pop('transforms')
        t.pop('visualElements')
        print(t.keys())
    
    ##converting dictionary into json 
    
    #json_object = json.dumps(uploading_string['pages'], indent = 4)

    json_object = json.dumps(uploading_string, indent = 4)
    
    #with open(uuid+'simplifies.json','w')as j: no need to creating file
    #    j.write(json_object)
    
    match_output = re.match(r'gs://([^/]+)/(.+)', destination_uri)
    destination_blob_name = match_output.group(2)
    bucket_name_output = match_output.group(1)
    uploader=storage_upload.upload_blob(bucket_name_output, destination_blob_name,json_object)
    print(uploader)
    


    
    

    

    return destination_uri
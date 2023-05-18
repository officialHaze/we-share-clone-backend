from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import File, ShortURL
from nacl.secret import SecretBox
from upload_sessions.models import ZipName, FileUploadDetail
import shortuuid
import base64
import datetime
import os
import dropbox
import dropbox.files


app_key = os.environ.get('DROPBOX_KEY')
app_secret = os.environ.get('DROPBOX_SECRET')
refresh_token = os.environ.get('DROPBOX_REFRESH_TOKEN')

expiration_time_oauth = datetime.datetime.now() + datetime.timedelta(days=100)
expiration_time_str_oauth = expiration_time_oauth.strftime('%Y-%m-%d %H:%M:%S')
dbx = dropbox.Dropbox(
    app_key=app_key,
    app_secret=app_secret,
    oauth2_refresh_token=refresh_token,
    oauth2_access_token_expiration=expiration_time_oauth
    ) #create a dropbox instance

encryption_key = os.environ.get('ENCRYPTION_KEY')
decryption_key = os.environ.get('DECRYPTION_KEY')


def update_database(*args, **kwargs):
    download_url = kwargs.get('file')
    qs = File.objects.filter(file=download_url)
    if qs:
        instance = qs[0]
    else:
        instance = File.objects.create(**kwargs)
    return instance.id


def check_expiry(id):
    current_time = datetime.datetime.now()
    current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
    query_set = File.objects.filter(id=id)
    expiry = query_set[0].expires_on
    if current_time_str >= expiry:
        query_set[0].delete()
        return True
    return False


def extract_file_extension(filename):
    divided_filename = filename.rsplit('.', 1)
    file_name = divided_filename[0]
    extension = divided_filename[-1]
    return [file_name, extension]


def downloadable_url(url):
    url_without_param = url.rsplit("?", 1)[0]
    dl_param = '?dl=1'
    downloadable_url = url_without_param+dl_param
    return downloadable_url


def handle_encryption(content):
    secret_key = encryption_key.encode('utf-8')
    secret_box = SecretBox(secret_key)
    encryption = secret_box.encrypt(content.encode('utf-8'))
    encrypted_content = encryption.ciphertext
    nonce = encryption.nonce
    return [encrypted_content, nonce]


#automate the process of decryption
def handle_decryption(*args, nonce):
    secret_key = decryption_key.encode('utf-8')
    secret_box = SecretBox(secret_key)
    decrypted_datas = []
    for encrypted_data in args:
        encrypted_data_decoded = base64.b64decode(encrypted_data)
        decrypted_data = secret_box.decrypt(encrypted_data_decoded, nonce)
        decrypted_datas.append(decrypted_data)
    return decrypted_datas


'''Get the upload session details'''
def get_upload_session_details(zip_name, file_name):
    try:
        zip_name_instance = ZipName.objects.filter(zip_name=zip_name)[0]
        upload_session_instance = FileUploadDetail.objects.filter(zip_name=zip_name_instance, file_name=file_name)[0]
        session_id = upload_session_instance.session_id
        offset = upload_session_instance.offset
        upload_session_details = {
            'session_id':session_id,
            'offset':offset
        }
        return upload_session_details
    except:
        return None


'''Start/Update the upload session'''
def update_upload_session(zip_name, file_name, session_id, offset):
    zip_name_instance = ZipName.objects.update_or_create(zip_name=zip_name)
    '''populate the upload session details'''
    try:
        upload_session_instance = FileUploadDetail.objects.filter(file_name=file_name)[0]

        upload_session_instance.session_id = session_id
        upload_session_instance.offset = offset
        upload_session_instance.save()
    except:
        FileUploadDetail.objects.create(zip_name=zip_name_instance[0], file_name=file_name,
                                        session_id=session_id, offset=offset)


'''delete the upload session'''
def delete_upload_session(zip_name):
    zip_name_instance = ZipName.objects.get(zip_name=zip_name)
    zip_name_instance.delete()


@api_view(["POST"])
def upload_file(req, *args, **kwargs):
    file_name_encoded = req.data.get('file_name')
    zip_name_encoded = req.data.get('zip_name')
    file_description_encoded = req.data.get('file_desc')
    file_encoded = req.data.get('file')
    nonce_encoded = req.data.get('nonce')
    upload_status = req.data.get('complete_status')

    decrypted_datas = handle_decryption(
        file_name_encoded,
        zip_name_encoded,
        file_description_encoded,
        file_encoded,
        nonce=base64.b64decode(nonce_encoded)
        )

    decrypted_file_name = decrypted_datas[0].decode('utf-8')
    decrypted_zip_name = decrypted_datas[1].decode('utf-8')
    decrypted_file_desc = decrypted_datas[2].decode('utf-8')
    decrypted_file_chunk = decrypted_datas[4]


    # Set the expiration time for the uploaded file to 20 days from now
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=20)
    expiration_time_str = expiration_time.strftime('%Y-%m-%d %H:%M:%S')

    #get the file extension and the filename seperately
    [file_name, extension] = extract_file_extension(decrypted_file_name)

    upload_path = f'/files/uploads/{decrypted_zip_name}.zip/{file_name}.{extension}'
    download_path = f'/files/uploads/{decrypted_zip_name}.zip'

    #set a default id to be sent as a response
    id = 0

    #upload file using dropbox api
    # check if upload session already exists for this file
    upload_session_details = get_upload_session_details(decrypted_zip_name, decrypted_file_name)
    if not upload_session_details:
        # create a new upload session
        session_start_result = dbx.files_upload_session_start(
            b"",
        )
        offset = 0
        session_id = session_start_result.session_id
        update_upload_session(decrypted_zip_name, decrypted_file_name, session_id, offset)
    else:
        session_id = upload_session_details.get('session_id')
        offset = upload_session_details.get('offset')

    try:
        if upload_status == "incomplete":
            result = dbx.files_upload_session_append_v2(
                    decrypted_file_chunk, dropbox.files.UploadSessionCursor(session_id, offset)
                )
            # update offset in db
            update_upload_session(
                decrypted_zip_name, 
                decrypted_file_name, 
                session_id, 
                offset=offset+len(decrypted_file_chunk))
        elif upload_status == "complete":
            result = dbx.files_upload_session_finish(
                    decrypted_file_chunk, dropbox.files.UploadSessionCursor(session_id, offset), dropbox.files.CommitInfo(upload_path)
                )
            # delete the upload session
            delete_upload_session(decrypted_zip_name)
            print('upload_session deleted')

            shared_link_obj = dbx.sharing_create_shared_link(path=download_path)

            url = shared_link_obj.url
            download_url = downloadable_url(url)

            id = update_database(
                file_name=decrypted_zip_name,
                file_description=decrypted_file_desc,
                file=download_url,
                expires_on=expiration_time_str)

        return Response({'detail':'uploaded', 'id':id}, status=200)
    except:
        # remove upload session from dictionary if any upload error occurs
        delete_upload_session(decrypted_zip_name)
        print('upload_session deleted due to error')
        return Response({'detail':'upload error!'}, status=500)


@api_view(["GET"])
def get_download_url(req, *args, **kwargs):
    id = kwargs.get('id')
    try:
        isExpired = check_expiry(int(id))
        if isExpired:
            return Response({'detail':'url expired!'}, status=403)
        query_set = File.objects.filter(id=int(id))
        download_url = query_set[0].file
        [encrypted_content, nonce] = handle_encryption(download_url)
        return Response(
            {
            'download_url':base64.b64encode(encrypted_content),
            'nonce':base64.b64encode(nonce),
            },
            status=200)
    except:
        raise Exception


@api_view(["POST"])
def shorten_url(req, *args, **kwargs):
    encrypted_url = req.data.get('encryptedURL')
    nonce = req.data.get('nonce')

    decrypted_datas = handle_decryption(
        encrypted_url,
        nonce=base64.b64decode(nonce)
    )

    decrypted_url = decrypted_datas[0].decode('utf-8')

    #save the url as long url in db
    qs = ShortURL.objects.filter(long_url=decrypted_url) #checking wether the url already exists
    if qs:
        instance = qs[0] #if there is a query set existing, get the first instance, as there will be only one instance because duplication has been prevented
    else:
        #if there is no qs, create an instance
        alphabet = os.environ.get('SHORT_UUID_ALPHABET')
        su = shortuuid.ShortUUID(alphabet=alphabet) # Create a ShortUUID object with the custom alphabet
        short_id = su.random(length=8) # Generate a short ID of exactly 8 characters in length
        short_url_base_address = os.environ.get('SHORT_URL_BASE_ADDRESS')
        model_arguments = {
            "id": short_id,
            "long_url":decrypted_url,
            "short_url": f'{short_url_base_address}/{short_id}/'
        }
        instance = ShortURL.objects.create(**model_arguments)
    short_url = instance.short_url

    #encrypt the url before sending as a response
    [encrypted_content, nonce] = handle_encryption(short_url)

    return Response(
        {
            'enc_short_url':base64.b64encode(encrypted_content),
            'nonce':base64.b64encode(nonce)
         },
         status=200
         )

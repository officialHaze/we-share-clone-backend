from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.files.storage import FileSystemStorage
from .models import File, ShortURL
from dotenv import load_dotenv
from filestack import Client
from filestack.exceptions import FilestackHTTPError
from nacl.secret import SecretBox
import shortuuid
import base64
import datetime
import os
import io

load_dotenv()

client = Client(os.environ.get('FILESTACK_API_KEY'))

encryption_key = os.environ.get('ENCRYPTION_KEY')
decryption_key = os.environ.get('DECRYPTION_KEY')



# def binary_data(file):
#     fs = FileSystemStorage()
#     filename = fs.save(file.name, file)
#     file_path = fs.path(filename)
#     with open(file_path, 'rb') as f:
#         file_binary_data = f.read()
#     return [file_binary_data, filename]


def delete_local_file(filename):
    fs = FileSystemStorage()
    file_path = fs.path(filename)
    try:
        os.remove(file_path)
        return 'File deleted'
    except:
        return 'Error while deleting the file'


def populate_database(*args, **kwargs):
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


@api_view(["POST"])
def upload_file(req, *args, **kwargs):
    file_name_encoded = req.data.get('file_name')
    file_description_encoded = req.data.get('file_desc')
    file_encoded = req.data.get('file')
    file_type_encoded = req.data.get('file_type')
    file_original_name_encoded = req.data.get('original_name')
    nonce_encoded = req.data.get('nonce')

    secret_key = decryption_key.encode('utf-8')
    secret_box = SecretBox(secret_key)


    #decode all the data
    file_name_encrypted = base64.b64decode(file_name_encoded)
    file_desc_encrypted = base64.b64decode(file_description_encoded)
    file_type_encrypted = base64.b64decode(file_type_encoded)
    file_original_name_encrypted = base64.b64decode(file_original_name_encoded)
    file_encrypted = base64.b64decode(file_encoded)
    nonce = base64.b64decode(nonce_encoded)

    #decrypt all the data
    decrypted_file_name = secret_box.decrypt(file_name_encrypted, nonce).decode('utf-8')
    decrypted_file_desc = secret_box.decrypt(file_desc_encrypted, nonce).decode('utf-8')
    decrypted_file_type = secret_box.decrypt(file_type_encrypted, nonce).decode('utf-8')
    decrypted_file_orginal_name = secret_box.decrypt(file_original_name_encrypted, nonce).decode('utf-8')
    decrypted_file = secret_box.decrypt(file_encrypted, nonce)


    # Set the expiration time for the uploaded file to 24 hours from now
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=7)
    expiration_time_str = expiration_time.strftime('%Y-%m-%d %H:%M:%S')

    store_params={
        'mimetype': decrypted_file_type,
        'filename': decrypted_file_orginal_name
    }
    try:
        file_link = client.upload(
            file_obj=io.BytesIO(decrypted_file),
            store_params=store_params,
            )
    except:
        raise FilestackHTTPError()

    download_url = file_link.url + '?dl=true'

    id = populate_database(
        file_name=decrypted_file_name,
        file_description=decrypted_file_desc,
        file=download_url,
        expires_on=expiration_time_str)

    return Response({'detail':'uploaded', 'id':id}, status=200)


@api_view(["GET"])
def get_download_url(req, *args, **kwargs):
    id = kwargs.get('id')
    try:
        isExpired = check_expiry(int(id))
        if isExpired:
            return Response({'detail':'url expired!'}, status=403)
        query_set = File.objects.filter(id=int(id))
        download_url = query_set[0].file
        secret_key = encryption_key.encode('utf-8')
        secret_box = SecretBox(secret_key)
        encrypted = secret_box.encrypt(download_url.encode('utf-8'))
        return Response(
            {
            'download_url':base64.b64encode(encrypted.ciphertext),
            'nonce':base64.b64encode(encrypted.nonce),
            },
            status=200)
    except:
        raise Exception


@api_view(["POST"])
def shorten_url(req, *args, **kwargs):
    encrypted_url = req.data.get('encryptedURL')
    nonce = req.data.get('nonce')

    secret_key = decryption_key.encode('utf-8')
    secret_box = SecretBox(secret_key)

    #decode the data
    decoded_encrypted_url = base64.b64decode(encrypted_url)
    decoded_nonce = base64.b64decode(nonce)

    #decrypt the data
    decrypted_url = secret_box.decrypt(decoded_encrypted_url, decoded_nonce).decode()

    #save the url as long url in db
    qs = ShortURL.objects.filter(long_url=decrypted_url) #checking wether the url already exists
    if qs:
        instance = qs[0] #if there is a query set existing, get the first instance, as there will be only one instance because duplication has been prevented
    else:
        #if there is no qs, create an instance
        alphabet = os.environ.get('SHORT_UUID_ALPHABET')
        su = shortuuid.ShortUUID(alphabet=alphabet) # Create a ShortUUID object with the custom alphabet
        short_id = su.random(length=8) # Generate a short ID of exactly 8 characters in length
        model_arguments = {
            "id": short_id,
            "long_url":decrypted_url,
        }
        instance = ShortURL.objects.create(**model_arguments)
    short_id = instance.id
    return Response({'hashed_id':short_id})

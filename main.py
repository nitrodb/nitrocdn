import random
import quart
import orjson
import urllib3
import io
import secrets
from werkzeug.utils import secure_filename
from cdn.database import client, secret
from cdn.errors import BadData, Unauthorized, Err, NotFound

try:
    import uvloop # type: ignore

    uvloop.install()
except:
    pass

class ORJSONDecoder:
    def __init__(self, **kwargs):
        self.options = kwargs

    def decode(self, obj):
        return orjson.loads(obj)


class ORJSONEncoder:
    def __init__(self, **kwargs):
        self.options = kwargs

    def encode(self, obj):
        return orjson.dumps(obj).decode('utf-8')

app = quart.Quart(__name__)
# only accept 10mb or less files.
app.config['MAX_CONTENT_LENGTH'] = 10 * 1000 * 1000
app.json_encoder = ORJSONEncoder
app.json_decoder = ORJSONDecoder

@app.route('/admin/upload/<bucket_id>', methods=['PUT', 'POST'])
async def upload(bucket_id: str):
    if quart.request.headers.get('Authorization') != secret:
        raise Unauthorized()

    imgs = await quart.request.files

    for _, fp in imgs.items():

        if fp.filename == '':
            raise BadData()
        fp.filename = secure_filename(fp.filename)
        try:
            name = secrets.token_urlsafe(random.randint(3, 19)) + '-' + fp.filename
            client.put_object(
                bucket_name=bucket_id,
                object_name=str(name),
                data=fp,
                length=-1,
                content_type=fp.mimetype,
                part_size=app.config['MAX_CONTENT_LENGTH']
        )   
        except Exception as exc:
            print(repr(exc))
            raise BadData()

    return quart.jsonify({'id': str(name)})

# TODO: This currently downloads the file, but i just want this to show the file
def get_obj_by_id(bucket_id: str, obj_id: str):
    try:
        resp: urllib3.HTTPResponse = client.get_object(bucket_id, obj_id)
    except:
        raise NotFound()

    bytesio = io.BytesIO(resp.read(decode_content=False, cache_content=False))
    return quart.send_file(bytesio, resp.getheader('content-type').split(';')[0])

@app.route('/users/avatars/<avatar_id>')
async def get_user_avatar(avatar_id):
    return await get_obj_by_id('user-avatars', avatar_id)

@app.route('/users/banners/<banner_id>')
async def get_user_banner(banner_id):
    return await get_obj_by_id('user-banners', banner_id)

@app.route('/guilds/avatars/<avatar_id>')
async def get_guild_avatar(avatar_id):
    return await get_obj_by_id('guild-avatars', avatar_id)

@app.route('/guilds/banners/<banner_id>')
async def get_guild_banner(banner_id):
    return await get_obj_by_id('guild-banners', banner_id)

@app.route('/guilds/users/avatars/<avatar_id>')
async def get_guild_user_avatar(avatar_id):
    return await get_obj_by_id('guild-user-avatars', avatar_id)

@app.route('/guilds/users/banners/<banner_id>')
async def get_guild_user_banner(banner_id):
    return await get_obj_by_id('guild-user-banners', banner_id)

@app.errorhandler(Err)
async def handle_err(err: Err):
    resp = err._to_json()
    resp.mimetype = 'application/json'
    return resp

if __name__ == '__main__':
    app.run(debug=True)

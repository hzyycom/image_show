from flask import Flask, request, redirect, url_for, flash, render_template,send_from_directory, send_file
from werkzeug.utils import secure_filename
import os
from PIL import Image
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'youzi'
base_image_path = '%s/static/images/' %  app.root_path 


@app.route('/upload/<name>', methods=['POST'])
def upload_image(name):
    #print('upload name: ', name)
    if 'image' not in request.files:
        flash('No file part')
        return redirect(request.url)
 
    file = request.files['image']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
 
    if file:
        filename = secure_filename(file.filename)
        hash_filename = hash(filename)
        post = filename.split('.')

        filename = getTime()
        if len(post)>1:
            filename = filename + '.' + post[-1]
        file.save('%s/%s/%s'  % (  base_image_path, name, filename))
        return f'文件上传成功: {filename}'


@app.route('/images/<string:name>/<path:filename>')
def send_image(name, filename):
    #print('image path send_image:' + filename)
    filename = '%s/%s/%s' %  (base_image_path ,name, filename)
    byte_io = image_resize(filename, resize=8) 

    return send_file(byte_io, mimetype='image/jpeg')
    #return send_from_directory( '%s/%s' %  (base_image_path ,name) , filename)

@app.route('/video/<string:name>/<path:filename>')
def send_video(filename, name):
    return send_from_directory( '%s/%s' %  (base_image_path ,name), filename)



@app.route('/')
def imagelist():
    # 假设所有图片都在static/images文件夹下
    host = request.host
    print(host)
    prefix_host = host.split('.')[0]
    images = os.listdir(base_image_path + '/' + prefix_host)
    images.sort()
    images_list = [img for img in images if  img.split('.')[-1].lower()  not in ['mov', 'mp4'] and not img.startswith(".")]
    videos_list = [img for img in images if  img.split('.')[-1].lower()  in ['mov', 'mp4'] and not img.startswith(".")]
    return render_template('index.html', images=images_list[::-1], videos=videos_list[::-1], name=prefix_host)


def image_resize(origin_image_path, resize):
    image = Image.open(origin_image_path)
    width, height = image.size

    if hasattr(image, '_getexif'):
        exif_data = image._getexif()
        if exif_data is not None:
            # 检查EXIF中的方向信息
            orientation = exif_data.get(0x0112)
            if orientation:
                # 根据方向信息旋转图像
                if orientation == 3:
                    image = image.transpose(Image.ROTATE_180)
                elif orientation == 6:
                    image = image.transpose(Image.ROTATE_270)
                elif orientation == 8:
                    image = image.transpose(Image.ROTATE_90)
    
    # 缩放图片
    resized_image = image.resize((int(width/resize), int(height/resize)))

    # 将图片转换为字节流
    byte_io = BytesIO()
    resized_image.save(byte_io, format='JPEG')
    byte_io.seek(0)
    return byte_io

def getTime():
    now = datetime.now()
    return str(now.date()) + 'T' + str(now.time()).replace(':','-').replace('.', 'T')


if __name__ == '__main__':
    app.run(port=8866)

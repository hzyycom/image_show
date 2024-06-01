from flask import Flask, request, redirect, url_for, flash, render_template,send_from_directory, send_file
from werkzeug.utils import secure_filename
import os
from PIL import Image
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'youzi'
#base_image_path = '/var/www/html/youzi/'
base_image_path = '%s/static/images/' %  app.root_path 

#<div style="width: 50%; margin-left: auto; margin-right: auto;">
#@app.route('/')
#def index():
#    return render_template('index.html', images=[])
 
@app.route('/upload/<name>', methods=['POST'])
def upload_image(name):
    print('upload name: ', name)
    if 'image' not in request.files:
        flash('No file part')
        return redirect(request.url)
 
    file = request.files['image']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
 
    if file:
        filename = secure_filename(file.filename)
        file.save('%s/%s/%s'  % (  base_image_path, name, filename))
        return f'文件上传成功: {filename}'


#@app.route('/<path:filename>')
#def send_image(filename):
#    print('send_image:' + filename)
#    filename = filename.replace('images/', '')
#    filename = filename.replace('videos/', '')
#    print('result: ' + filename)
#    return send_from_directory(base_image_path, filename)

#@app.route('/uploads/images/<path:filename>')
#def send_image(filename):
#    print('image path send_image:' + filename)
#    return send_from_directory(base_image_path, filename)

@app.route('/images/<string:name>/<path:filename>')
def send_image(name, filename):
    print('image path send_image:' + filename)
    filename = '%s/%s/%s' %  (base_image_path ,name, filename)
    byte_io = image_resize(filename, resize=8) 

    return send_file(byte_io, mimetype='image/jpeg')
    #return send_from_directory( '%s/%s' %  (base_image_path ,name) , filename)

@app.route('/video/<string:name>/<path:filename>')
def send_video(filename, name):
    print('video path send_image:' + filename, name)
    return send_from_directory( '%s/%s' %  (base_image_path ,name), filename)



@app.route('/')
def imagelist():
    # 假设所有图片都在static/images文件夹下
    host = request.host
    print(host)
    prefix_host = host.split('.')[0]
    images = os.listdir(base_image_path + '/' + prefix_host)
    for img in images:
        print(img)
    images_list = [img for img in images if  img.split('.')[-1].lower()  not in ['mov', 'mp4']]
    videos_list = [img for img in images if  img.split('.')[-1].lower()  in ['mov', 'mp4']]
    #images_list = images
    #videos_list = []
    return render_template('index.html', images=images_list, videos=videos_list, name=prefix_host)


def image_resize(origin_image_path, resize):

    image = Image.open(origin_image_path)
    
    width, height = image.size
    #info = image._getexif()
    #print("image info:", info)

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
    
    print(int(width/resize), int(height/resize))
    # 缩放图片
    resized_image = image.resize((int(width/resize), int(height/resize)))

    # 将图片转换为字节流
    byte_io = BytesIO()
    resized_image.save(byte_io, format='JPEG')
    byte_io.seek(0)
    return byte_io

if __name__ == '__main__':
    app.run(port=8866)

from flask import Flask, request, redirect, url_for, flash, render_template,send_from_directory, send_file
from werkzeug.utils import secure_filename
import os
from PIL import Image
from io import BytesIO
from datetime import datetime
import hashlib
from datetime import datetime
from flask_paginate import Pagination


app = Flask(__name__)
app.secret_key = 'youzi'
base_image_path = '%s/static/images/' %  app.root_path 


@app.route('/upload/<name>', methods=['POST'])
def upload_image(name):
    print('upload name: ', name)
    if 'image' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    info = []
    files = request.files.getlist('image')
    for file in files:
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
 
        if file:
            filename = secure_filename(file.filename)

            hash_filename = md5_hash(filename)
            print('ori:', name, filename, hash_filename)
            flag_repeat, match_name = is_repeat(get_image_list(), hash_filename)
            print(flag_repeat, filename, hash_filename) 
            print('match_name:', match_name)
            if flag_repeat:
                info.append(f'文件已经存在: {match_name}')
                print(f'文件已经存在: {match_name}')
                continue
        
            post = filename.split('.')

            filename = getTime()
            if len(post)>1:
                #filename = filename + '@' + hash_filename + '.' + post[-1]
                filename = '%s@%s.%s' % (filename, hash_filename, post[-1])
                print('rest_filename:', filename)
            file.save('%s/%s/%s'  % (  base_image_path, name, filename))
            info.append(f'文件上传成功: {filename}')
    return  f''.join(['<p>%s</p>' % i  for i in info])

'''
send_image 参数:
name: youzi 等图片文件夹
filename: 图片文件名
size: 图片缩放比例: weight/size
'''
@app.route('/images/<string:name>/<path:filename>/<int:size>')
def send_image(name, filename, size):
    #print('image path send_image:' + filename)
    filename = '%s/%s/%s' %  (base_image_path ,name, filename)
    byte_io = image_resize(filename, resize=size) 

    return send_file(byte_io, mimetype='image/jpeg')
    #return send_from_directory( '%s/%s' %  (base_image_path ,name) , filename)

@app.route('/video/<string:name>/<path:filename>')
def send_video(filename, name):
    return send_from_directory( '%s/%s' %  (base_image_path ,name), filename)



def get_page_index(item_list, page, limit):
    start = (page - 1) * limit
    end = page * limit if len(item_list) > page * limit else len(item_list)
    return item_list[start:end]
    


@app.route('/')
def imagelist():
    # 假设所有图片都在static/images文件夹下
    host = request.host
    prefix_host = host.split('.')[0]
    limit = 10 # 翻页size
    
    images = get_image_list()
    images_list = [img for img in images if  img.split('.')[-1].lower()  not in ['mov', 'mp4'] and not img.startswith(".")]
    videos_list = [img for img in images if  img.split('.')[-1].lower()  in ['mov', 'mp4'] and not img.startswith(".")]
    
    page = int(request.args.get("page", 1))
    page_video = int(request.args.get("page_video", 1))
    
 
    page_video = page if page*limit<(len(videos_list)+limit) else (len(videos_list)//limit+1)
    paginate_video = Pagination(page=(page if page*limit<(len(videos_list)+limit) else (len(videos_list)//limit+1)), total=len(videos_list))
    #app.logger.info(page, page*limit, len(videos_list)+limit, len(videos_list)//limit+1, len(videos_list))
    print(page, page*limit, len(videos_list)+limit, len(videos_list)//limit+1, len(videos_list))
    paginate = Pagination(page=page, total=len(images_list))
    
    images_list = get_page_index(images_list, page, limit) 
    
    videos_list = get_page_index(videos_list, page_video, limit) 
     

    
    return render_template('index.html', images=images_list[::-1], videos=videos_list[::-1], name=prefix_host, paginate=paginate, paginate_video=paginate_video)


def get_image_list():
    host = request.host
    print(host)
    prefix_host = host.split('.')[0]
    images = os.listdir(base_image_path + '/' + prefix_host)
    images.sort()
    return images

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
    return str(now.date()) + '@' + str(now.time()).replace(':','-').replace('.', '@')


'''
判断文件重复
'''
def is_repeat(filenames, match_str):
    #print(filenames)
    for filename in filenames:
        if not filename.startswith('.'):
            name = filename.split('.')
            if len(name)<2:
                continue
            parts = name[0].split('@')
            if len(parts) == 4: 
                
                print("match status:", parts[3]==match_str,  parts[3], match_str)
                if parts[3] == match_str:
                    print("is match:", parts[3], match_str, )
                    return (True, filename)
    return (False, '')

def md5_hash(text):
    # 创建一个MD5散列对象
    md5 = hashlib.md5()
    # 添加要散列的字节数据
    md5.update(text.encode('utf-8'))
    # 返回散列的十六进制字符串
    return md5.hexdigest()



##########################################################
##  milk  喂奶记录

@app.route('/milk')
def get_milk_record():
    sub_host = get_sub_host()
    fname = './static/file/%s.milk.txt' % sub_host
    lines = open_milk_file(fname)
    
    return render_template('milk.html', lines=lines[::-1][:150])

def open_milk_file(fname):
    if not os.path.isfile(fname):
        return list()
    with open(fname) as f:
        lines = [line.strip().split(' ') for line in f]
        return lines 

def get_date():
    now = datetime.now()
    formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_now.split(' ')

def get_sub_host():
    host = request.host
    print(host)
    return host.split('.')[0]
    

def act_map(act):
    act_dic = {
        '1': '吃奶',
        '2': '吃奶',
        '3': '屎',
        '4': '尿'
    }
    return act_dic.get(act, '其它')

@app.route('/milk/add/<string:lr>')
def add_milk_record(lr):
    dt,tt = get_date()
    
    #按子域名生成文件名
    sub_host = get_sub_host()
    fname = './static/file/%s.milk.txt' % sub_host
    print('info: %s %s %s' % (dt, tt, lr))
     
    dr = act_map(lr)
    with open(fname, 'a') as fw:
        fw.write('%s %s %s\n' % (dt, tt, dr))
        #if lr == '1' or lr == '2':
        #    fw.write('%s %s %s %s\n' % (dt, tt, dr, '*'))
        #elif lr == '3' or lr == '4':
        #    fw.write('%s %s %s %s\n' % (dt, tt, '*', dr))
    
    lines = open_milk_file(fname)
    for line in lines:
        print(len(line), line)
    return render_template('milk.html', lines=lines[::-1])
    
    








if __name__ == '__main__':
    app.run(port=8866, debug=True)

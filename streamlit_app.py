from pathlib import Path
import streamlit as st
from COVIDNet_4.detect import start_detect
from COVIDNet_2.detect import start_detect
import os
import argparse
from PIL import Image


def get_subdirs(b='.'):
    '''
        Returns all sub-directories in a specific Path
    '''
    result = []
    for d in os.listdir(b):
        bd = os.path.join(b, d)
        if os.path.isdir(bd):
            result.append(bd)
    return result


def get_detection_folder():
    '''
        Returns the latest folder in a runs\detect
    '''
    return max(get_subdirs(os.path.join('runs', 'detect')), key=os.path.getmtime)


if __name__ == '__main__':

    st.set_page_config(page_title='COVID-19 Diagnostic CAD', page_icon=':sheep:', layout='wide', initial_sidebar_state="auto")
    st.title('COVID-19人工智能辅助诊断系统')
    st.header('Artificial intelligence computer aided diagnosis system for COVID-19')
    st.header('Introduction')
    st.text('This is a platform for diagnosis of COVID-19.\n'
           'You can enter the CT to be tested on the page\n'
           'and then choose model to diagnose COVID-19 here.\n')

    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default='weights/mass_best.pt', help='model path(s)')
    parser.add_argument('--source', type=str, default='data/images', help='file/dir/URL/glob, 0 for webcam')
    parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=[640], help='inference size h,w')
    parser.add_argument('--conf-thres', type=float, default=0.25, help='confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='NMS IoU threshold')
    parser.add_argument('--max-det', type=int, default=1000, help='maximum detections per image')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='show results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    parser.add_argument('--save-crop', action='store_true', help='save cropped prediction boxes')
    parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --classes 0, or --classes 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--visualize', action='store_true', help='visualize features')
    parser.add_argument('--update', action='store_true', help='update all models')
    parser.add_argument('--project', default='runs/detect', help='save results to project/name')
    parser.add_argument('--name', default='exp', help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    parser.add_argument('--line-thickness', default=3, type=int, help='bounding box thickness (pixels)')
    parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
    parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
    parser.add_argument('--half', action='store_true', help='use FP16 half-precision inference')
    parser.add_argument('--dnn', action='store_true', help='use OpenCV DNN for ONNX inference')
    opt = parser.parse_args()
    opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  # expand

    st.sidebar.header('患者3D CT图像输入')
    uploaded_file = st.sidebar.file_uploader(
        "请选择输入图像", type=['png', 'jpeg', 'jpg'])
    if uploaded_file is not None:
        is_valid = True
        with st.spinner(text='资源加载中...'):
            st.sidebar.image(uploaded_file)
            picture = Image.open(uploaded_file)
            picture = picture.save(f'images/{uploaded_file.name}')
            opt.source = f'images/{uploaded_file.name}'
    else:
        is_valid = False

    models = ("COVIDNet_2", "COVIDNet_4")
    st.sidebar.header('COVID-19辅助诊断模型选择')
    model_index = st.sidebar.selectbox("请选择COVID-19诊断模型", range(
        len(models)), format_func=lambda x: models[x])

    if model_index == 0:
        st.sidebar.text('You selected: COVIDNet_2')
        opt.weights = 'COVIDNet_2/weights/calc_best.pt'
    else:
        st.sidebar.text('You selected: COVIDNet_4')
        opt.weights = 'COVIDNet_4/weights/mass_best.pt'

    if is_valid:
        if st.sidebar.button('开始诊断'):
            start_detect(opt)

            with st.spinner(text='Preparing Images'):
                for img in os.listdir(get_detection_folder()):
                    st.image(str(Path(f'{get_detection_folder()}') / img))

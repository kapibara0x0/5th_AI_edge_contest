from PIL import Image
from PIL import ImageColor
import cv2 # resize_video 用
import json # resize_annotation 用

class CategoriesReader():
    categories = []
    categories_color = {}
    def __init__(self, categories_file_path):
        with open(categories_file_path, 'r') as f:
            categories = f.readlines()
            self.categories = [c.strip() for c in categories]
        self.assign_colors()
    def get_categories(self):
        return self.categories

    def assign_colors(self):
        '''
        カテゴリごとに色を割り当てる
        return categories_color : {"カテゴリ名":"3原色のタプル"}
        '''
        # HSVの色相をカテゴリ数で分割する
        cat_num = len(self.categories)
        for i, category in enumerate(self.categories):
            h = int(360 / (cat_num)) * i
            s = 100 # 100%
            v = 100 # 100%
            color = ImageColor.getrgb("hsv({},{}%,{}%)".format(str(h), str(s), str(v)))
            self.categories_color[category] = color

    def get_category_color(self, category):
        return self.categories_color[category]

    
def resize_video(video_path, save_video_path, save_fourcc, resized_width, resized_height):
    """
    動画をリサイズして保存する関数

    Parameters
    ----------
    video_path : str
    リサイズしたい動画を示すパス
    save_video_path : str
    リサイズ後の動画の保存先を示すパス
    save_fourcc : str
    保存する動画データのフォーマットを指定する four-character code
    　例：mp4形式 → "mp4v"
    resized_width : int
    リサイズ後の横の大きさ
    resized_height : int
    リサイズ後の縦の大きさ
    
    Returns
    -------
    None
    """
    # 動画データの読み込み
    video = cv2.VideoCapture(video_path)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    size = (width, height)
    frame_rate = int(video.get(cv2.CAP_PROP_FPS))
    # 書き込み用にVideoWriterオブジェクトを作成
    resized_size = (resized_width, resized_height)
    fmt = cv2.VideoWriter_fourcc(*save_fourcc)
    writer = cv2.VideoWriter(save_video_path, fmt, frame_rate, resized_size)
    # 動画をリサイズして保存する。
    while True:
        ret, frame = video.read()
        if ret is False:
            break
        frame = cv2.resize(frame, dsize=resized_size)
        writer.write(frame)
    writer.release()
    video.release()
    
    
def resize_annotation(annotations_path, annotations_resized_path, scale_2_resize_width, scale_2_resize_height):
    """
    アノテーションファイルのGround Truth（座標データ）を動画のリサイズ幅に合わせて変更して保存する関数
    Parameters
    ----------
    annotations_path : str
    リサイズしたいアノテーションファイルを示すパス
    annotations_resized_path : str
    リサイズ後のアノテーションファイルの保存先を示すパス
    scale_2_resize_width : float
    リサイズ後とリサイズ前の横幅の比率（リサイズ後/リサイズ前）
    scale_2_resize_height : float
    リサイズ後とリサイズ前の縦幅の比率（リサイズ後/リサイズ前）
    
    Returns
    -------
    None
    """
    # アノテーションデータ(json)のファイル読み込み
    with open(annotations_path, 'r') as f:
        annotations_json = json.load(f) # 辞書型に変換

    # 1フレームずつ処理します。
    for sequence in range(len(annotations_json['sequence'])):
        # 1フレームに含まれるデータをカテゴリずつ処理します。
        for category in annotations_json['sequence'][sequence].keys():
            # 1フレームの1カテゴリに対して、真値のデータは複数あるので一つずつ処理します。
            for index, rect_info in enumerate(annotations_json['sequence'][sequence][category]):
                box2d = rect_info['box2d']
                annotations_json['sequence'][sequence][category][index]['box2d'][0] = int(box2d[0] * scale_2_resize_width)
                annotations_json['sequence'][sequence][category][index]['box2d'][1] = int(box2d[1] * scale_2_resize_height)
                annotations_json['sequence'][sequence][category][index]['box2d'][2] = int(box2d[2] * scale_2_resize_width)
                annotations_json['sequence'][sequence][category][index]['box2d'][3] = int(box2d[3] * scale_2_resize_height)

    # アノテーションデータ(json)のファイル書き込み
    with open(annotations_resized_path, 'w') as f:
        json.dump(annotations_json, f)
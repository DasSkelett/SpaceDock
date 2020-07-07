import os.path

from PIL import Image

from KerbalStuff.config import _cfg, _cfgi, site_logger


def create(background_path: str, thumbnail_path: str) -> None:
    if not os.path.isfile(background_path):
        return

    size_str = _cfg('thumbnail_size')
    if not size_str:
        size_str = "320x320"
    size_str_tuple = size_str.split('x')
    size = (int(size_str_tuple[0]), int(size_str_tuple[1]))

    quality = _cfgi('thumbnail_quality')
    if not quality or 0 > quality > 100:
        quality = 80

    im = Image.open(background_path)
    if im.mode in ("RGBA", "P"):
        im = im.convert("RGB")
    im.thumbnail(size, Image.ANTIALIAS)
    im.save(thumbnail_path, 'jpeg', quality=quality, optimize=True)


def get_or_create(background_url: str) -> str:
    storage = _cfg('storage')
    if not storage:
        return background_url

    (background_directory, background_file_name) = os.path.split(background_url)

    thumb_file_name = os.path.splitext(background_file_name)[0] + '.jpg'
    thumb_url = os.path.join(background_directory, 'thumb_' + thumb_file_name)

    thumb_disk_path = os.path.join(storage, thumb_url.replace('/content/', ''))
    background_disk_path = os.path.join(storage, background_url.replace('/content/', ''))

    if not os.path.isfile(thumb_disk_path):
        try:
            create(background_disk_path, thumb_disk_path)
        except Exception:
            site_logger.exception('Unable to create thumbnail')
            return background_url
    return thumb_url

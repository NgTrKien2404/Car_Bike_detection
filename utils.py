import os

def get_next_filename(filename_base, extension):
    """Tìm tên file tiếp theo không bị trùng."""
    n = 1
    while True:
        filename = f"{filename_base}_{n}{extension}"
        if not os.path.exists(filename):
            return filename
        n += 1

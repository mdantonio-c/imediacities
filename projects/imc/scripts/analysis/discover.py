import glob
import mimetypes
import os
import os.path

stage_area = "/home/ubuntu/imediacities/imediastuff"

# discover movie extensions from the mimetypes

mimetypes.init()
movie_extensions = [
    k.upper() for k, v in mimetypes.types_map.items() if v.find("video") != -1
]

print("=== movie_extensions: ===")
for i, f in enumerate(movie_extensions):
    print(f"{i:3} {f}")
print()

# discover user folders
# example name: 'ac8e5f4d-5534-4e0d-befb-4b00c7a57fa3'


def is_user_folder(path):
    if os.path.isdir(path):
        dirname = os.path.basename(path)
        if len(dirname) == 36:
            if dirname[8] + dirname[13] + dirname[18] + dirname[23] == "----":
                return True
    return False


lst = glob.glob(stage_area + "/*")
user_folders = [d for d in lst if is_user_folder(d)]
user_folders.sort()

print("=== user folders: ===")
for i, f in enumerate(user_folders):
    print(f"{i:3} {os.path.basename(f)}")
print()

# discover user movies

user_movies = []
for uf in user_folders:
    for folder, subfolders, files in os.walk(uf):
        for f in files:
            ext = os.path.splitext(f)[1].upper()
            if ext in movie_extensions:
                user_movies.append(folder + "/" + f)
user_movies.sort()


def size_to_str(number_of_bytes):
    if number_of_bytes < 0:
        raise ValueError("!!! numberOfBytes can't be smaller than 0 !!!")

    step_to_greater_unit = 1024.0

    number_of_bytes = float(number_of_bytes)
    unit = "bytes"

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = "KB"

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = "MB"

    # if (number_of_bytes / step_to_greater_unit) >= 1:
    #    number_of_bytes /= step_to_greater_unit
    #    unit = 'GB'

    # if (number_of_bytes / step_to_greater_unit) >= 1:
    #    number_of_bytes /= step_to_greater_unit
    #    unit = 'TB'

    precision = 1
    number_of_bytes = round(number_of_bytes, precision)

    return str(number_of_bytes) + " " + unit


print("=== user movies: ===")
for i, m in enumerate(user_movies):
    name, ext = os.path.splitext(os.path.basename(m))
    size = size_to_str(os.path.getsize(m)).rjust(10)
    short_name = name[: 50 - len(ext)] + ext
    line = f"{i:3} {short_name:50} {size:10} {m}"
    print(line)
print()

# prepare output folders
"""
def mkdir(path):
    if not os.path.isdir(path):
        os.mkdir(path)
    if not os.path.isdir(path):
        print( "ERROR failed to create", path )
        sys.exit()

mkdir(analize_area)

for m in user_movies:
    uf = m.replace(stage_area+'/','').split('/')[0]
    analyze_uf = os.path.join( analize_area, uf )
    mkdir(analyze_uf)

    m_name, m_ext = os.path.splitext( os.path.basename( m ) )
    analyze_uf = os.path.join( analize_area, uf )
    movie_uf   = os.path.join( analyze_uf, m_name )
    mkdir(movie_uf)

    link_name = 'origin'+m_ext;
    link_path = os.path.join( movie_uf, link_name)
    if os.path.exists(link_path):
        os.remove(link_path)
    os.symlink( m, link_path )
"""

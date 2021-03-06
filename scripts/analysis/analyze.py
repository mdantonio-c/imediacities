import datetime
import glob
import json
import os
import os.path
import shutil
import sys
from subprocess import Popen
from xml.etree import ElementTree as ET

from PIL import Image

os.umask(int("007", 8))

TRANSCODED_FRAMERATE = 24  # now used as a default

host = "imc_vm"
root_dir = "/"

stage_area = root_dir + "uploads"
analize_area = root_dir + "uploads/Analize"
watermark_area = root_dir + "uploads/Analize/watermarks"
idmt_bin = root_dir + "imedia-pipeline/tools"
idmt_scripts = root_dir + "imedia-pipeline/scripts"
idmt_py = root_dir + "imedia-pipeline/scripts/idmt"

default_media = "00000000-0000-0000-00000000000000000/test_00.avi"
default_filename = os.path.join(stage_area, default_media)
default_mediatype = "Video"  # 'Image'
default_uuid = "000"

logfile = None


# -----------------------------------------------------
def log(msg):
    global logfile
    print(msg)
    sys.stdout.flush()
    time = datetime.datetime.now().strftime("[%d%b%y %H:%M:%S] ")
    if logfile is None:
        print("warning -- log file not initialized")
        sys.stdout.flush()
    try:
        logfile.write(time + msg + "\n")
        logfile.flush()
    except BaseException:
        print("warning -- write to log file failed -- logfile closed ?")
        sys.stdout.flush()


# -----------------------------------------------------
def mkdir(path, clean):
    # print(mkdir, path, clean)
    if clean:
        if os.path.isdir(path):
            shutil.rmtree(path)
    if not os.path.isdir(path):
        os.mkdir(path)
    if not os.path.isdir(path):
        print("ERROR failed to create", path)
        return False
    return True


# -----------------------------------------------------
def filename_to_frame(f):
    substr = os.path.basename(f).replace("tvs_s_", "").replace(".jpg", "")
    return int(substr)


# -----------------------------------------------------
def frame_to_timecode(f, fps):
    f = int(f)
    t_hour = int(f / (3600 * fps))
    t_min = int((f - t_hour * 3600 * fps) / (60 * fps))
    t_sec = int((f - t_hour * 3600 * fps - t_min * 60 * fps) / fps)
    t_frame = int(f - t_hour * 3600 * fps - t_min * 60 * fps - t_sec * fps)
    timecode = f"{t_hour:02d}:{t_min:02d}:{t_sec:02d}-f{t_frame:02d}"
    return timecode


# -----------------------------------------------------
# now called from outside
# -----------------------------------------------------
# make movie_analize_folder as :  analize_area / user_folder_name / movie_name
# and link the given filename as  movie_analize_folder/origin + movie_ext
def make_movie_analize_folder(filename, clean=False):  # , temporary=False):

    if not mkdir(analize_area, False):
        return ""

    user_folder = filename.replace(stage_area + "/", "").split("/")[0]
    user_analyze_folder = os.path.join(analize_area, user_folder)
    if not mkdir(user_analyze_folder, False):
        return ""

    m_name, m_ext = os.path.splitext(os.path.basename(filename))
    movie_analize_folder = os.path.join(user_analyze_folder, m_name)

    if not mkdir(movie_analize_folder, clean):
        return ""

    origin_link_name = os.path.join(movie_analize_folder, "origin")
    origin_link_target = filename.replace(stage_area, "../../..")

    if os.path.exists(origin_link_name):
        os.unlink(origin_link_name)
    try:
        os.symlink(origin_link_target, origin_link_name)
    except BaseException:
        print("failed to create origin link")

    global logfile
    logfile = open(os.path.join(movie_analize_folder, "log.txt"), "w")

    return movie_analize_folder


# -----------------------------------------------------
def init_child_proc():
    os.umask(0)


# -----------------------------------------------------
def run(cmd, out_folder, out_name, err_name, cmd_name=None):
    if cmd_name:
        cmd_filename = os.path.join(out_folder, cmd_name)
        cmd_file = open(cmd_filename, "w")
        cmd_file.write(cmd)
        cmd_file.close()

    out_filename = os.path.join(out_folder, out_name)
    err_filename = os.path.join(out_folder, err_name)

    out_file = open(out_filename, "w")
    err_file = open(err_filename, "w")

    p = Popen(
        cmd,
        shell=True,
        universal_newlines=True,
        stdout=out_file,
        stderr=err_file,
        preexec_fn=init_child_proc,
    )
    res = p.wait()

    out_file.close()
    err_file.close()
    if res == 0:
        return True
    else:
        return False


# -----------------------------------------------------
def get_framerate(filename):
    out_file = open(filename)
    if out_file is None:
        log("cant open " + filename)
        return 0

    data = json.load(out_file)
    for s in data["streams"]:
        if s["codec_type"] == "video":
            if "r_frame_rate" not in s:
                log("r_frame_rate not found in: " + filename)
                return 0
            value = int(s["r_frame_rate"].split("/")[0])
            if value < 1 or value > 100:
                log("bad framerate:" + str(value) + "in:" + filename)
                return 0
            return value
    log("framerate not found in: " + filename)
    return 0


# -----------------------------------------------------
def origin_tech_info(filename, out_folder):
    global TRANSCODED_FRAMERATE

    cmd_list = [
        "/usr/bin/ffprobe -v quiet -print_format json -show_format -show_streams",
        filename,
    ]
    cmd = " \\\n".join(cmd_list) + "\n"

    res = run(cmd, out_folder, "origin_info.json", "origin_info.err", "origin_info.sh")

    framerate = get_framerate(os.path.join(out_folder, "origin_info.json"))
    if framerate != 0:
        TRANSCODED_FRAMERATE = framerate
    else:
        TRANSCODED_FRAMERATE = 24  # fallback (errors already logged)
    return res


# -----------------------------------------------------
def image_origin_tech_info(filename, out_folder):
    cmd_list = [
        "/usr/bin/convert",
        filename,
        os.path.join(out_folder, "origin_info.json"),
    ]
    cmd = " \\\n".join(cmd_list) + "\n"

    res = run(cmd, out_folder, "origin_info.out", "origin_info.err", "origin_info.sh")
    return res


# -----------------------------------------------------
def transcoded_tech_info(filename, out_folder, v2=""):
    cmd_list = [
        "/usr/bin/ffprobe -v quiet -print_format json -show_format -show_streams",
        filename,
    ]
    cmd = " \\\n".join(cmd_list) + "\n"

    res = run(
        cmd,
        out_folder,
        v2 + "transcoded_info.json",
        v2 + "transcoded_info.err",
        v2 + "transcoded_info.sh",
    )
    return res


# -----------------------------------------------------
def image_transcoded_tech_info(filename, out_folder, v2=""):
    cmd_list = [
        "/usr/bin/convert",
        filename,
        os.path.join(out_folder, v2 + "transcoded_info.json"),
    ]
    cmd = " \\\n".join(cmd_list) + "\n"

    res = run(
        cmd,
        out_folder,
        v2 + "transcoded_info.out",
        v2 + "transcoded_info.err",
        v2 + "transcoded_info.sh",
    )
    return res


# -----------------------------------------------------
def transcoded_num_frames(out_folder, v2=""):
    out_filename = os.path.join(out_folder, v2 + "transcoded_info.json")
    out_file = open(out_filename)
    data = json.load(out_file)
    for s in data["streams"]:
        if s["codec_type"] == "video":
            return int(s["nb_frames"])


# -----------------------------------------------------
def lookup_v2(filename):
    dirname = os.path.dirname(filename)
    other_filename = os.path.join(dirname, "v2_" + os.path.basename(filename))
    if os.path.exists(other_filename):
        return other_filename
    other_filename = os.path.join(dirname, "V2_" + os.path.basename(filename))
    if os.path.exists(other_filename):
        return other_filename


# -----------------------------------------------------
def transcode(filename, out_folder, fps, prefix=""):

    out_filename = os.path.join(out_folder, prefix + "transcoded.mp4")

    cmd_list = []
    cmd_list.append("/usr/bin/ffmpeg -hide_banner -nostdin -y")
    # cmd_list.append('-threads 4')
    cmd_list.append("-i " + filename)
    cmd_list.append("-vf yadif=0:-1:0")  # deinterlacing
    cmd_list.append(
        "-vcodec libx264 -crf 15.0 -pix_fmt yuv420p -coder 1 -rc_lookahead 60 -r "
        + fps
        + " -strict -2"
    )  # video codec
    cmd_list.append(
        "-g " + fps + " -forced-idr 1 -sc_threshold 40 -bf 16 -refs 6 "
    )  # keyframes
    cmd_list.append("-acodec aac -b:a 128k")  # audio codec
    cmd_list.append(out_filename)

    cmd = " \\\n".join(cmd_list) + "\n"

    bk_filename = out_filename + ".bk"
    if os.path.exists(bk_filename):
        os.remove(bk_filename)
    if os.path.exists(out_filename):
        os.rename(out_filename, bk_filename)

    if not run(
        cmd,
        out_folder,
        prefix + "transcode.log",
        prefix + "transcode.err",
        prefix + "transcode.sh",
    ):
        return False
    return os.path.exists(out_filename)

    # to check if a movie is sane --- try to encode using a null output, so you only do the reading
    # ffmpeg -v error -i input -f null - 2> error.log


# -----------------------------------------------------
def v2_image_transcode(filename, out_folder):
    out_filename = os.path.join(out_folder, "v2_transcoded.jpg")
    if filename.lower().endswith((".tif",)):
        filename += "[0]"
    cmd_list = ["/usr/bin/convert", filename, "-quality", "95", out_filename]
    cmd = " \\\n".join(cmd_list) + "\n"

    if not run(
        cmd, out_folder, "v2_transcode.log", "v2_transcode.err", "v2_transcode.sh"
    ):
        return False


# -----------------------------------------------------
def image_transcode(filename, out_folder, watermark):
    """transcode an image to jpg, with a compression quality of 95
    rescale the image keeping the aspect ratio so that it is smaller then 800x600 and save it as transcoded.jpg
    also save a full resolution version as transcoded_fullres.jpg
    """

    out_filename = os.path.join(out_folder, "transcoded.jpg")
    out_filename_small = os.path.join(out_folder, "transcoded_small.jpg")
    out_filename_fullres = os.path.join(out_folder, "transcoded_fullres.jpg")
    out_filename_logo = os.path.join(out_folder, "transcoded_with_logo.jpg")
    out_filename_logo_fullres = os.path.join(
        out_folder, "transcoded_with_logo_fullres.jpg"
    )
    if filename.lower().endswith((".tif",)):
        filename += "[0]"

    # transcoded.jpg
    cmd_list = [
        "/usr/bin/convert",
        filename,
        "-resize",
        r"800x600\>",
        "-quality",
        "95",
        out_filename,
    ]
    cmd = " \\\n".join(cmd_list) + "\n"
    if not run(cmd, out_folder, "transcode.log", "transcode.err", "transcode.sh"):
        return False

    # transcoded_fullres.jpg
    cmd_list = ["/usr/bin/convert", filename, "-quality", "95", out_filename_fullres]
    cmd = " \\\n".join(cmd_list) + "\n"
    if not run(
        cmd,
        out_folder,
        "transcode_fullres.log",
        "transcode_fullres.err",
        "transcode_fullres.sh",
    ):
        return False

    # transcoded_small.jpg
    cmd_list = [
        "/usr/bin/convert",
        filename,
        "-resize",
        "80x80^",
        "-gravity",
        "center",
        "-quality",
        "95",
        out_filename_small,
    ]
    cmd = " \\\n".join(cmd_list) + "\n"
    if not run(
        cmd,
        out_folder,
        "transcode_small.log",
        "transcode_small.err",
        "transcode_small.sh",
    ):
        return False

    if watermark:
        log("transcoding with watermark...")
        cmd_list = [
            "/usr/bin/convert",
            out_filename,
            watermark,
            "-geometry",
            "+10+10",
            "-gravity",
            "SouthWest",
            "-composite",
            "-quality",
            "95",
            out_filename_logo,
        ]
        cmd = " \\\n".join(cmd_list) + "\n"
        if not run(
            cmd,
            out_folder,
            "transcode_logo.log",
            "transcode_logo.err",
            "transcode_logo.sh",
        ):
            return False

        cmd_list = [
            "/usr/bin/convert",
            out_filename_fullres,
            watermark,
            "-geometry",
            "+10+10",
            "-gravity",
            "SouthWest",
            "-composite",
            "-quality",
            "95",
            out_filename_logo_fullres,
        ]
        cmd = " \\\n".join(cmd_list) + "\n"
        if not run(
            cmd,
            out_folder,
            "transcode_logo_fullres.log",
            "transcode_logo_fullres.err",
            "transcode_logo_fullres.sh",
        ):
            return False
    return os.path.exists(out_filename)


# -----------------------------------------------------
def tvs(filename, out_folder):

    prg_filename = os.path.join(idmt_bin, "idmtvideoanalysis")
    out_filename = os.path.join(out_folder, "tvs.xml")
    cmd_filename = os.path.join(out_folder, "tvs.sh")
    sht_filename = os.path.join(out_folder, "tvs_s_%06d.jpg")
    key_filename = os.path.join(out_folder, "tvs_k_%06d.jpg")

    f = open(cmd_filename, "w")
    # f.write( 'export LC_ALL="en_US.UTF-8"\n')
    f.write("export LC_ALL=\n")
    f.write("export LD_LIBRARY_PATH=/opt/idmt/lib/:$LD_LIBRARY_PATH\n\n")
    f.write(prg_filename + " \\\n")
    f.write("-f " + filename + " \\\n")
    f.write("-o " + out_filename + " \\\n")
    f.write("-s " + sht_filename + " \\\n")
    f.write("-k " + key_filename + " \\\n")
    f.write("-t tvs \n")
    f.close()

    if not run("/bin/bash " + cmd_filename, out_folder, "tvs.log", "tvs.err"):
        return False
    return os.path.exists(out_filename)


# -----------------------------------------------------
def quality(filename, out_folder):

    prg_filename = os.path.join(idmt_bin, "idmtvideoanalysis")
    out_filename = os.path.join(out_folder, "quality.xml")
    cmd_filename = os.path.join(out_folder, "quality.sh")

    f = open(cmd_filename, "w")
    # f.write('export LC_ALL="en_US.UTF-8"\n')
    f.write("export LC_ALL=\n")
    f.write("export LD_LIBRARY_PATH=/opt/idmt/lib/:$LD_LIBRARY_PATH\n\n")
    f.write(prg_filename + " \\\n")
    f.write("-f " + filename + " \\\n")
    f.write("-o " + out_filename + " \\\n")
    f.write("-t quality \n")
    f.close()

    if not run("/bin/bash " + cmd_filename, out_folder, "quality.log", "quality.err"):
        return False
    return os.path.exists(out_filename)


# -----------------------------------------------------
def vimotion(filename, out_folder):

    prg_filename = os.path.join(idmt_bin, "idmtvideoanalysis")
    out_filename = os.path.join(out_folder, "vimotion.xml")
    cmd_filename = os.path.join(out_folder, "vimotion.sh")

    f = open(cmd_filename, "w")
    # f.write('export LC_ALL="en_US.UTF-8"\n')
    f.write("export LC_ALL=\n")
    f.write("export LD_LIBRARY_PATH=/opt/idmt/lib/:$LD_LIBRARY_PATH\n\n")
    f.write(prg_filename + " \\\n")
    f.write("-f " + filename + " \\\n")
    f.write("-o " + out_filename + " \\\n")
    f.write("-c 0.1 \\\n")
    f.write("-t vimotion \n")
    f.close()

    if not run("/bin/bash " + cmd_filename, out_folder, "vimotion.log", "vimotion.err"):
        return False
    return os.path.exists(out_filename)


# -----------------------------------------------------
def summary(filename, out_folder):

    scr_filename = os.path.join(
        idmt_scripts, "imc_create_video_summary_visualization.py"
    )
    out_filename = os.path.join(out_folder, "summary.jpg")
    cmd_filename = os.path.join(out_folder, "summary.sh")

    f = open(cmd_filename, "w")
    # f.write( 'export LC_ALL="en_US.UTF-8"\n')
    f.write("export LC_ALL=\n")
    f.write("export LD_LIBRARY_PATH=/opt/idmt/lib/:$LD_LIBRARY_PATH\n\n")
    f.write("export IDMT_PY=" + idmt_py + "\n")
    f.write("export PYTHONPATH=$IDMT_PY:$PYTHONPATH\n")
    f.write("/usr/bin/python3 " + scr_filename + " \\\n")
    f.write("-f " + filename + " \\\n")
    f.write("-o " + out_filename + " \\\n")
    f.write("-w 1024 -e 120 \n")
    f.close()

    if not run("/bin/bash " + cmd_filename, out_folder, "summary.log", "summary.err"):
        return False
    return os.path.exists(out_filename)


# -----------------------------------------------------
def submit_orf(media, mtype, uuid, out_folder):

    cmd_filename = os.path.join(out_folder, "submit_orf.sh")

    f = open(cmd_filename, "w")
    f.write("export KEY=/home/developer/.ssh/sil_rsa\n")
    f.write("export R_USER=simboden\n")
    f.write("export R_PATH=/gpfs/work/cin_staff/simboden/IMCgpu/imc-orf\n")
    f.write("MEDIA=" + media + "\n")
    f.write("MTYPE=" + mtype + "\n")
    f.write("UUID=" + str(uuid) + "\n")
    f.write(
        'ssh -i $KEY $R_USER@login.galileo.cineca.it "cd $R_PATH && sbatch submit.sh $MTYPE $MEDIA $UUID $PROJECT_DOMAIN"\n'
    )
    f.write("UUID=" + uuid + "\n")
    f.close()

    if not run(
        "/bin/bash " + cmd_filename, out_folder, "submit_orf.log", "submit_orf.err"
    ):
        return False
    return True


# -----------------------------------------------------
def thumbs_index_storyboard(filename, out_folder, num_frames):

    movie_name = os.path.basename(out_folder)

    # framenumber in shot filenames may be 5 or 6 digit long
    # force them to 6 digit, so that the following filenames.sort
    # will work as expected
    lst = glob.glob(out_folder + "/tvs_s_*.jpg")
    for name in lst:
        num = int(name.replace(out_folder + "/tvs_s_", "").replace(".jpg", ""))
        name2 = out_folder + f"/tvs_s_{num:06d}.jpg"
        if name != name2:
            os.rename(name, name2)

    # the same for tvs_k_*.jpg
    lst = glob.glob(out_folder + "/tvs_k_*.jpg")
    for name in lst:
        num = int(name.replace(out_folder + "/tvs_k_", "").replace(".jpg", ""))
        name2 = out_folder + f"/tvs_k_{num:06d}.jpg"
        if name != name2:
            os.rename(name, name2)

    # retrieve shot frames
    lst = glob.glob(out_folder + "/tvs_s_*.jpg")
    lst.sort()
    num_shot = len(lst)
    if num_shot == 0:
        print("thumbs_index_storyboard: no shots!")
        return False

    im = Image.open(lst[0])
    ar = float(im.height / im.width)
    th_sz = (100, int(100 * ar))

    # prepare thumbnails
    th_folder = os.path.join(out_folder, "thumbs")
    if not mkdir(th_folder, True):
        return False

    for fn in lst:
        im = Image.open(fn)
        im_small = im.resize(th_sz, Image.BILINEAR)
        im_small.save(fn.replace(out_folder, th_folder), quality=90)

    # prepare storyboard
    sb_folder = os.path.join(out_folder, "storyboard")
    if not mkdir(sb_folder, True):
        return False

    sb = {}
    sb["movie"] = movie_name
    sb["shots"] = []

    for i, fn in enumerate(lst):

        im = Image.open(fn)
        w1, h1 = 200, int(200.0 * im.height / im.width)
        im_small = im.resize((w1, h1), Image.BILINEAR)
        im_name = f"shot_{i:04d}.jpg"
        im_small.save(sb_folder + "/" + im_name, quality=90)

        frame = filename_to_frame(fn)
        shot_len = 0
        if i != len(lst) - 1:
            nextframe = filename_to_frame(lst[i + 1]) - 1
        else:
            nextframe = num_frames - 1

        shot_len = (nextframe - frame + 1) / TRANSCODED_FRAMERATE
        shot_len = round(shot_len, 2)

        d = {}
        d["shot_num"] = i
        d["first_frame"] = frame
        d["last_frame"] = nextframe
        d["timecode"] = frame_to_timecode(frame, TRANSCODED_FRAMERATE)
        d["len_seconds"] = shot_len
        d["img"] = im_name
        sb["shots"].append(d)

    # insert vim
    insert_vim_in_storyboard(out_folder, sb)

    # save
    text = json.dumps(sb, indent=4)
    f = open(sb_folder + "/storyboard.json", "w")
    f.write(text)
    f.close()

    return True


# -----------------------------------------------------
def insert_vim_in_storyboard(out_folder, sb):

    # retrieve last_frame_number
    num_frames = transcoded_num_frames(out_folder)
    if num_frames == 0:
        log("num_frames == 0, quitting")
        return False

    vim_filename = os.path.join(out_folder, "vimotion.xml")

    vim = {}
    vim_root = ET.parse(vim_filename).getroot()
    for m in vim_root.findall("module"):
        vim[m.attrib["name"]] = [0] * num_frames
    vim_names = list(vim.keys())
    vim_names.sort()
    # names_wid = max( [len(i) for i in vim_names ])

    for m in vim_root.findall("module"):
        scores = vim[m.attrib["name"]]
        for f in m.findall("frame"):
            frame = int(f.attrib["idx"])
            value = float(f.attrib["value"])
            scores[frame] = value

    for shot in sb["shots"]:
        f0 = shot["first_frame"]
        f1 = shot["last_frame"]

        # ---- output come dizionario
        shot_vim_dic = {}
        for n in vim_names:
            values = vim[n][f0:f1]
            if values:
                max_value = max(values)
                avg_value = sum(values) / float(len(values))
            else:
                max_value = 0
                avg_value = 0
            shot_vim_dic[n] = (round(avg_value, 3), round(max_value, 3))
        shot["motions_dict"] = shot_vim_dic

        # --- output come lista sortata sulla probabilita

        shot_vim = []
        for n in vim_names:
            values = vim[n][f0:f1]
            if values:
                avg_value = sum(values) / float(len(values))
            else:
                avg_value = 0
            if avg_value > 0.1:
                shot_vim.append((round(avg_value, 3), n))
        shot_vim.sort(reverse=True)

        shot["estimated_motions"] = shot_vim


# -----------------------------------------------------
def revert_to_origin_framerate(filename):

    out_folder = make_movie_analize_folder(filename, True, True)
    if out_folder == "":
        return False
    log("out_folder=" + out_folder)
    if not analize_movie(filename, out_folder, False):
        return False
    # if all ok swap the two out_folders


# -----------------------------------------------------
def analize_movie(filename, out_folder, muuid, fast=False):

    log("origin_tech_info -------- begin")
    if not origin_tech_info(filename, out_folder):
        return False
    log("origin_tech_info -------- ok")
    log("fast_mode --------------- " + str(fast))
    log("frame_rate -------------- " + str(TRANSCODED_FRAMERATE))

    tr_movie = os.path.join(out_folder, "transcoded.mp4")

    if fast and os.path.exists(tr_movie):
        log("transcode --------------- skipped")
    else:
        log("transcode --------------- begin ")
        if not transcode(filename, out_folder, fps=str(TRANSCODED_FRAMERATE)):
            return False
        log("transcode --------------- ok")

    log("transcoded_info --------- begin")
    if not transcoded_tech_info(tr_movie, out_folder):
        return False
    log("transcoded_info --------- ok")

    nf = transcoded_num_frames(out_folder)
    log("transcoded_nb_frames ---- " + str(nf))

    # other version
    v2_movie = os.path.join(out_folder, "v2_transcoded.mp4")
    if fast and os.path.exists(v2_movie):
        log("transcode v2 ------------ skipped")
    else:
        # look for the other version
        other_version = lookup_v2(filename)
        if other_version is not None:
            # create symbolic link
            v2_link_name = os.path.join(out_folder, "v2")
            v2_link_target = other_version.replace(stage_area, "../../..")

            if os.path.exists(v2_link_name):
                os.unlink(v2_link_name)
            try:
                os.symlink(v2_link_target, v2_link_name)
            except BaseException:
                print("failed to create v2 link")

            # transcode v2 movie
            log("transcode v2 ------------ begin")
            if not transcode(
                other_version, out_folder, fps=str(TRANSCODED_FRAMERATE), prefix="v2_"
            ):
                return False
            log("transcode v2 ------------ ok")

    if os.path.exists(v2_movie):
        log("v2_transcoded_info ------ begin")
        if not transcoded_tech_info(v2_movie, out_folder, "v2_"):
            return False
        log("v2_transcoded_info ------ end")

        v2_nf = transcoded_num_frames(out_folder, "v2_")
        log("v2_transcoded_nb_frames - " + str(v2_nf))
        if nf != v2_nf:
            # v2 transcoded version does NOT match the number of frames
            return False

    tvs_out = os.path.join(out_folder, "tvs.xml")

    if fast and os.path.exists(tvs_out):
        log("tvs --------------------- skipped")
    else:
        log("tvs --------------------- begin")
        if not tvs(tr_movie, out_folder):
            return False
        log("tvs --------------------- ok")

    quality_out = os.path.join(out_folder, "quality.xml")

    if fast and os.path.exists(quality_out):
        log("quality ----------------- skipped")
    else:
        log("quality ----------------- begin")
        if not quality(tr_movie, out_folder):
            return False
        log("quality ----------------- ok")

    vimotion_out = os.path.join(out_folder, "vimotion.xml")

    if fast and os.path.exists(vimotion_out):
        log("vimotion ---------------- skipped")
    else:
        log("vimotion ---------------- begin")
        if not vimotion(tr_movie, out_folder):
            return False
        log("vimotion ---------------- ok ")

    # summary_out = os.path.join(out_folder, 'summary.jpg')
    # if fast and os.path.exists(summary_out):
    #     log('summary ----------------- skipped')
    # else:
    #     log('summary ----------------- begin')
    #     if not summary(tr_movie, out_folder):
    #         return False
    #     log('summary ----------------- ok')

    log("index/storyboard -------- begin")
    if not thumbs_index_storyboard(tr_movie, out_folder, nf):
        return False
    log("index/storyboard -------- ok")

    orf_out = os.path.join(out_folder, "orf.xml")
    if fast and os.path.exists(orf_out):
        log("submit_orf ---------------- skipped")
    else:
        log("submit_orf -------------- begin")
        media = out_folder.replace(analize_area + "/", "")
        if not submit_orf(media, "Video", muuid, out_folder):
            return False
        log("submit_orf -------------- ok")

    return True


# -----------------------------------------------------


def analize_image(filename, out_folder, muuid, fast=False):

    log("image_origin_tech_info --- begin")
    if not image_origin_tech_info(filename, out_folder):
        return False
    log("image_origin_tech_info --- ok ")

    tr_image = os.path.join(out_folder, "transcoded.jpg")

    watermark = ""
    if "9621d236-230d-4a6f-bfbf-5959c15baf28" in filename:  # "crb"
        watermark = watermark_area + "/crb.png"
    if "995eee9b-3a7d-43b5-9c7e-264804583fbd" in filename:  # "ccb"
        watermark = watermark_area + "/ccb.png"
    if "15b54855-49c8-437c-9ad3-9226695d2fb4" in filename:  # "mct"
        watermark = watermark_area + "/mct.png"
    if "d42865cb-d61f-42f6-9c57-20f4d6b1ade3" in filename:  # "icec"
        pass
    if "8daa109f-76fd-4422-bfc4-0de6633ca582" in filename:  # "dif"
        pass
    if "1ede3472-6abd-453c-844f-e3a656cb21d6" in filename:  # "ofm"
        pass
    if "ac8e5f4d-5534-4e0d-befb-4b00c7a57fa3" in filename:  # "dfi"
        pass
    if "9324fc11-68b6-4a41-9294-0227ce8dcd15" in filename:  # "tte"
        pass
    if "9646014f-929c-4e73-88b7-afcff69f3463" in filename:  # "sfi"
        pass

    log("image_transcode ---------- begin ")
    if not image_transcode(filename, out_folder, watermark):
        return False
    log("image_transcode ---------- ok ")

    log("image_transcoded_info ---- begin ")
    if not image_transcoded_tech_info(tr_image, out_folder):
        return False
    log("image_transcoded_info ---- ok ")

    # other version
    v2_image = os.path.join(out_folder, "v2_transcoded.jpg")
    if fast and os.path.exists(v2_image):
        log("image_transcode v2 ------- skipped")
    else:
        # look for the other version
        other_version = lookup_v2(filename)
        if other_version is not None:
            # create symbolic link
            v2_link_name = os.path.join(out_folder, "v2")
            v2_link_target = other_version.replace(stage_area, "../../..")

            if os.path.exists(v2_link_name):
                os.unlink(v2_link_name)
            try:
                os.symlink(v2_link_target, v2_link_name)
            except BaseException:
                print("failed to create v2 link")

            # transcode v2 image
            log("image_transcode v2 ------ begin")
            v2_image_transcode(other_version, out_folder)
            log("image_transcode v2 ------ end")

    if os.path.exists(v2_image):
        log("v2_image_transcoded_info - begin")
        if not image_transcoded_tech_info(v2_image, out_folder, "v2_"):
            return False
        log("v2_image_transcoded_info - end")

    orf_out = os.path.join(out_folder, "orf.xml")
    if fast and os.path.exists(orf_out):
        log("submit_orf ---------------- skipped")
    else:
        log("submit_orf --------- begin")
        media = out_folder.replace(analize_area + "/", "")
        if not submit_orf(media, "Image", muuid, out_folder):
            return False
        log("submit_orf --------- ok")

    return True


# -----------------------------------------------------
def analize(filename, uuid, item_type, out_folder, fast=False):
    """Item type: "Video" or "Image"."""

    if item_type == "Video":
        return analize_movie(filename, out_folder, uuid, fast)

    if item_type in ["Image", "3D-Model"]:
        return analize_image(filename, out_folder, uuid, fast)

    print("analize error: bad item_type :", item_type)
    return False


# -----------------------------------------------------
def update_storyboard(revised_cuts, out_folder):

    # check out_folder ( must be an absolute path )
    if not os.path.exists(out_folder):
        print("bad_out_folder:", out_folder)
        return False

    # check storyboard folder
    sb_folder = os.path.join(out_folder, "storyboard")
    if not os.path.exists(sb_folder):
        print("no sb_folder:", sb_folder)
        return False

    # open storyboard logfile ( overwrite any previous )
    global logfile
    logfile = open(os.path.join(sb_folder, "log.txt"), "w")
    log("update_storyboard_begin")

    global TRANSCODED_FRAMERATE
    TRANSCODED_FRAMERATE = get_framerate(os.path.join(out_folder, "origin_info.json"))
    if TRANSCODED_FRAMERATE == 0:
        return False  # (errors already logged)

    # check movie
    movie = os.path.join(out_folder, "transcoded.mp4")
    if not os.path.exists(movie):
        log("no movie:", movie)
        return False

    # retrieve last_frame_number
    last_frame = transcoded_num_frames(out_folder)
    if last_frame == 0:
        log("total num frames == 0, quitting")
        return False

    # prepend 0 and append last_frame to revised_cuts -- ( side-effect: revised_cuts can't be empty )
    revised_cuts.insert(0, 0)  # -- to generate frame 0 thumbnail
    revised_cuts.append(last_frame)  # -- needed later ( next_frame is cuts[i+1]-1 )
    # check for duplicated cuts, (prevent 0-sized shots)
    revised_cuts = list(set(revised_cuts))
    revised_cuts.sort()
    # check cuts ranges
    first_cut = min(revised_cuts)
    last_cut = max(revised_cuts)
    if first_cut < 0 or last_cut > last_frame + 1:
        log(
            "bad cut range: [ "
            + str(first_cut)
            + " .. "
            + str(last_cut)
            + " ] should be in [0 .. "
            + str(last_frame + 1)
            + "] --- quitting"
        )
        return False

    # backup old storyboard.json
    storyboard = os.path.join(sb_folder, "storyboard.json")
    if os.path.exists(storyboard):
        counter = 0
        bk_name_root = storyboard.replace(".json", ".bk")
        counter = 0
        bk_name = bk_name_root + str(counter).rjust(3, "0")
        while counter < 100 and os.path.exists(bk_name):
            counter += 1
            bk_name = bk_name_root + str(counter).rjust(3, "0")
        if os.path.exists(bk_name):
            log("too many backups -- quitting")
            return False
        os.rename(storyboard, bk_name)

    # remove any shot_*.jpg file and any ../thumbs/tvs_s_*.jpg
    old_pics = glob.glob(sb_folder + "/shot_*.jpg")
    for name in old_pics:
        os.remove(name)
    old_pics = glob.glob(out_folder + "/thumbs/tvs_s_*.jpg")
    for name in old_pics:
        os.remove(name)

    def pic_name(num):
        return "f_" + str(num).rjust(6, "0") + ".jpg"

    # update frames pics
    cmd = "export MOVIE=" + movie + "\n"
    cmd += "export FOLDER=" + sb_folder + "\n"
    new_pics = []
    for num in revised_cuts[:-1]:  # skipping num_frames+1
        name = pic_name(num)
        path = os.path.join(sb_folder, name)
        if not os.path.exists(path):
            cmd += f'ffmpeg -i $MOVIE -vf "select=gte(n\\,{num})" -vframes 1 $FOLDER/{name} \n'
            new_pics.append(path)

    cmd_filename = os.path.join(sb_folder, "update_frames.sh")
    if os.path.exists(cmd_filename):
        os.remove(cmd_filename)
    if os.path.exists(cmd_filename):
        log('cant remove previous "update_frames.sh" file -- quitting')
        return False
    cmd_file = open(cmd_filename, "w")
    if not cmd_file:
        log('failed to create "update_frames.sh" file -- quitting')
        return False
    cmd_file.write(cmd)
    cmd_file.close()
    if not run(
        "/bin/bash " + cmd_filename, sb_folder, "update_frames.log", "update_frames.err"
    ):
        log("update frames failed")
        return False

    # update thumbs
    for n in new_pics:
        im = Image.open(n)
        w1, h1 = 200, int(200.0 * im.height / im.width)
        im_small = im.resize((w1, h1), Image.BILINEAR)
        im_name = n.replace("/storyboard/", "/thumbs/")
        im_small.save(im_name, quality=90)

    # make storyboard
    sb = {}
    sb["movie"] = os.path.basename(out_folder)
    sb["shots"] = []

    for i in range(len(revised_cuts) - 1):

        frame_start = revised_cuts[i]  # 0 was prepended to the cut_list
        frame_end = revised_cuts[i + 1] - 1  # last_frame+1 was appended to the cut_list

        shot_len = (frame_end - frame_start + 1) / TRANSCODED_FRAMERATE

        d = {}
        d["shot_num"] = i
        d["first_frame"] = frame_start
        d["last_frame"] = frame_end
        d["timecode"] = frame_to_timecode(frame_start, TRANSCODED_FRAMERATE)
        d["len_seconds"] = round(shot_len, 2)
        d["img"] = pic_name(frame_start)
        sb["shots"].append(d)

    # insert vim
    insert_vim_in_storyboard(out_folder, sb)

    # save
    text = json.dumps(sb, indent=4)
    f = open(sb_folder + "/storyboard.json", "w")
    f.write(text)
    f.close()

    log("update_storyboard done")
    logfile.close()

    return True


# -----------------------------------------------------
help = """ usage:  python3 analyze.py [options] [filename]
options:
[-fast  ]       skip transcoding, tvs, quality, vimotion and summary if their output files already exists.
[-clean ]       clean any previous data before analize
[-image ]       indicate that filename is an image ( not a movie)
[filename ]     if omitted use the default movie
"""


# -----------------------------------------------------
# not called form IMC
# IMC calls make_movie_analize_folder (if needed) and analize
# -----------------------------------------------------
def main(args):
    global logfile

    clean = False
    fast = False
    media = default_filename
    mtype = default_mediatype
    muuid = default_uuid

    args = sys.argv[1:]
    # num_args = len(args)
    for i, a in enumerate(args):
        if a == "--help" or a == "-help" or a == "-h":
            print(help)
            return
        elif a == "-clean":
            clean = True
        elif a == "-fast":
            fast = True
            clean = False  # fast is stronger than clean
        elif a == "-image":
            mtype = "Image"
        else:
            media = a

    if media.startswith(stage_area):
        # allow to specify media with full-path
        media = media.replace(stage_area + "/", "")

    filename = os.path.join(stage_area, media)
    if not os.path.exists(filename):
        print("aborting: bad input file", filename)
        return

    out_folder = make_movie_analize_folder(filename, clean)
    if out_folder == "":
        print("aborting: failed to create out_folder")
        return

    logfile = open(os.path.join(out_folder, "log.txt"), "w")
    log("Analize " + media)

    if analize(filename, muuid, mtype, out_folder, fast):
        log("Analize done")
    else:
        log("Analize terminated with errors")


# -----------------------------------------------------


if __name__ == "__main__":
    main(sys.argv[1:])
    print("done")

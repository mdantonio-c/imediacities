# -*- coding: utf-8 -*-

import os
import shutil
import json
from plumbum import local
from plumbum.commands.processes import ProcessExecutionError

from utilities.logs import get_logger
log = get_logger(__name__)


class FHG(object):

    TRANSCODED_FRAMERATE = 24
    ffprobe = '/usr/bin/ffprobe'
    ffmpeg = '/usr/bin/ffmpeg'
    idmt_bin = '/code/imc/imedia-pipeline/tools'

    def __init__(self, movie, stage_area):
        self.filename = os.path.join(stage_area, movie)
        self.stage_area = stage_area
        self.analize_area = self.stage_area + '/Analize'

    def analyze(self, fast):

        if not os.path.exists(self.filename):
            log.critical('Bad input file', self.filename)
            return False

        self.out_folder = self._make_movie_analize_folder(self.filename)
        if self.out_folder == "":
            log.critical('Failed to create out_folder')
            return False

        log.info("Analize " + self.filename)

        if not self.origin_tech_info():
            return False

        tr_movie = os.path.join(self.out_folder, 'transcoded.mp4')
        if not self.transcode(self.filename, tr_movie, fast):
            return False

        if not self.transcoded_tech_info(tr_movie):
            return False

        nf = self.transcoded_num_frames()

        tvs_out = os.path.join(self.out_folder, 'tvs.xml')

        if not self.tvs(tr_movie, tvs_out, fast):
            return False

        quality_out = os.path.join(self.out_folder, 'quality.xml')
        if not self.quality(tr_movie, quality_out, fast):
            return False

        vimotion_out = os.path.join(self.out_folder, 'vimotion.xml')
        if not self.vimotion(tr_movie, vimotion_out, fast):
            return False

        summary_out = os.path.join(self.out_folder, 'summary.jpg')
        if not self.summary(tr_movie, summary_out):
            return False

        if not self.thumbs_index_storyboard(tr_movie, self.out_folder, nf):
            return False

        return True

    def run(self, command, options, out_prefix):
        command = local[command]
        # command = myproxy.with_env(**env)

        out_file = os.path.join(self.out_folder, out_prefix)
        out_filename = out_file + ".json"
        err_filename = out_file + ".err"
        cmd_filename = out_file + ".sh"

        cmd_file = open(cmd_filename, 'w')
        cmd_file.write("%s %s" % (command, options))
        cmd_file.close()

        try:
            (command(options) > out_filename)()
            return True
        except ProcessExecutionError as e:
            stderr = e.stderr
            log.error(stderr)
            err_file = open(err_filename, 'w')
            err_file.write(stderr)
            err_file.close()
            return False

    def mkdir(self, path, clean=False):
        if clean:
            if os.path.isdir(path):
                shutil.rmtree(path)
        if not os.path.isdir(path):
            os.mkdir(path)
        if not os.path.isdir(path):
            log.reror("Failed to create", path)
            return False
        return True

    def _make_movie_analize_folder(self, filename, clean=False):
        """
        Make movie_analize_folder as:
            analize_area / user_folder_name / movie_name
        and link the given filename as
            movie_analize_folder/origin + movie_ext
        """

        if not self.mkdir(self.analize_area):
            return ""

        user_folder = filename.replace(self.stage_area + '/', '').split('/')[0]
        user_analyze_folder = os.path.join(self.analize_area, user_folder)
        if not self.mkdir(user_analyze_folder):
            return ""

        m_name, m_ext = os.path.splitext(os.path.basename(filename))
        movie_analize_folder = os.path.join(user_analyze_folder, m_name)
        if not self.mkdir(movie_analize_folder, clean):
            return ""

        origin_link = os.path.join(movie_analize_folder, 'origin')
        try:
            os.symlink(filename, origin_link)
        except BaseException:
            os.remove(origin_link)
            print('forcing origin link')
            os.symlink(filename, origin_link)

        return movie_analize_folder

    # -----------------------------------------------------
    def origin_tech_info(self):

        params = ""
        params += '-v quiet'
        params += ' -print_format json'
        params += ' -show_format'
        params += ' -show_streams'
        params += ' %s' % self.filename

        log.info('origin_tech_info --- begin')
        res = self.run(self.ffprobe, params, 'origin_info')

        if res:
            log.info('origin_tech_info --- ok ')
        else:
            log.error('origin_tech_info --- fail')

        return res

    # -----------------------------------------------------
    def transcode(self, out_filename, fast=False):

        if fast and os.path.exists(out_filename):
            log.info('transcode ---------- skipped')
            return True
        log.info('transcode ---------- begin ')

        params = ""
        params += '-hide_banner -nostdin -y'
        # params += '-threads 4'
        params += ' -i %s' % self.filename
        params += ' -vf yadif=1:-1:0'  # deinterlacin
        params += ' -vcodec libx264'
        params += ' -crf 15.0'
        params += ' -pix_fmt yuv420p'
        params += ' -coder 1'
        params += ' -rc_lookahead 60'
        params += ' -r %s' % self.TRANSCODED_FRAMERATE
        params += ' -strict -2'  # video code
        params += ' -g %s' % self.TRANSCODED_FRAMERATE
        params += ' -forced-idr 1'
        params += ' -sc_threshold 40'
        params += ' -bf 16'
        params += ' -refs 6'  # keyframe
        params += ' -acodec aac'
        params += ' -b:a 128k'  # audio code
        params += out_filename

        bk_filename = out_filename + ".bk"
        if os.path.exists(bk_filename):
            os.remove(bk_filename)
        if os.path.exists(out_filename):
            os.rename(out_filename, bk_filename)

        res = self.run(self.ffmpeg, params, 'transcode')

        if not res:
            log.info('transcode ---------- fail ')
            return False
        else:
            log.info('transcode ---------- ok ')
            return os.path.exists(out_filename)

        """
        to check if a movie is sane
        try to encode using a null output, so you only do the reading
        # ffmpeg -v error -i input -f null - 2> error.log
        """

    # -----------------------------------------------------
    def transcoded_tech_info(self, filename):

        log.info('transcoded_info ---- begin ')

        params = ""
        params += '-v quiet -print_format json -show_format -show_streams'
        params += filename

        res = self.run(self.ffprobe, params, 'transcoded_info')

        if res:
            log.info('transcoded_info ---- ok')
        else:
            log.info('transcoded_info ---- fail')
        return res

    # -----------------------------------------------------
    def transcoded_num_frames(self):
        out_filename = os.path.join(self.out_folder, 'transcoded_info.json')
        out_file = open(out_filename, 'r')
        data = json.load(out_file)
        return int(data['streams'][0]['nb_frames'])

    # -----------------------------------------------------
    def tvs(self, filename, tvs_out, fast):

        if fast and os.path.exists(tvs_out):
            log.info('tvs ---------------- skipped')
        else:
            log.info('tvs ---------------- begin ')

            log.info('tvs ---------------- ok ')

        prg_filename = os.path.join(self.idmt_bin, 'idmtvideoanalysis')
        out_filename = os.path.join(self.out_folder, 'tvs.xml')
        cmd_filename = os.path.join(self.out_folder, 'tvs.sh')
        sht_filename = os.path.join(self.out_folder, 'tvs_s_%05d.jpg')
        key_filename = os.path.join(self.out_folder, 'tvs_k_%05d.jpg')

        f = open(cmd_filename, 'w')
        # f.write( 'export LC_ALL="en_US.UTF-8"\n')
        f.write('export LC_ALL=\n')
        f.write('export LD_LIBRARY_PATH=/opt/idmt/lib/:$LD_LIBRARY_PATH\n\n')
        f.write(prg_filename + ' \\\n')
        f.write('-f ' + filename + ' \\\n')
        f.write('-o ' + out_filename + ' \\\n')
        f.write('-s ' + sht_filename + ' \\\n')
        f.write('-k ' + key_filename + ' \\\n')
        f.write('-t tvs \n')
        f.close()

        # TO FIX: output file should be .log and not .json
        res = self.run('/bin/bash ' + cmd_filename, params, 'tvs')

        if res:
            return os.path.exists(out_filename)
        else:
            return False

    # -----------------------------------------------------
    def quality(self, filename, quality_out, fast):

        if fast and os.path.exists(quality_out):
            log.info('quality ------------ skipped ')
            return True
        log.info('quality ------------ begin ')

        prg_filename = os.path.join(self.idmt_bin, 'idmtvideoanalysis')
        out_filename = os.path.join(self.ut_folder, 'quality.xml')
        cmd_filename = os.path.join(self.out_folder, 'quality.sh')

        f = open(cmd_filename, 'w')
        # f.write('export LC_ALL="en_US.UTF-8"\n')
        f.write('export LC_ALL=\n')
        f.write('export LD_LIBRARY_PATH=/opt/idmt/lib/:$LD_LIBRARY_PATH\n\n')
        f.write(prg_filename + ' \\\n')
        f.write('-f ' + filename + ' \\\n')
        f.write('-o ' + out_filename + ' \\\n')
        f.write('-t quality \n')
        f.close()

        # TO FIX: output file should be .log and not .json
        res = self.run('/bin/bash ' + cmd_filename, params, 'quality')

        if res:
            log.info('quality ------------ ok')
            return os.path.exists(out_filename)
        else:
            log.info('quality ------------ fail')
            return False

    # -----------------------------------------------------
    def vimotion(self, filename, vimotion_out, fast):

        if fast and os.path.exists(vimotion_out):
            log.info('vimotion ----------- skipped ')
            return True
        log.info('vimotion ----------- begin ')


        prg_filename = os.path.join(idmt_bin,   'idmtvideoanalysis')
        out_filename = os.path.join(out_folder, 'vimotion.xml')
        cmd_filename = os.path.join(out_folder, 'vimotion.sh')

        f = open(cmd_filename, 'w')
        # f.write('export LC_ALL="en_US.UTF-8"\n')
        f.write('export LC_ALL=\n')
        f.write('export LD_LIBRARY_PATH=/opt/idmt/lib/:$LD_LIBRARY_PATH\n\n')
        f.write(prg_filename + ' \\\n')
        f.write('-f ' + filename + ' \\\n')
        f.write('-o ' + out_filename + ' \\\n')
        f.write('-c 0.1 \\\n')
        f.write('-t vimotion \n')
        f.close()

        # TO FIX: output file should be .log and not .json
        res = self.run('/bin/bash ' + cmd_filename, params, 'vimotion')

        if res:
            log.info('vimotion ----------- ok ')
            return os.path.exists(out_filename)
        else:
            log.info('vimotion ----------- fail ')
            return False


    # -----------------------------------------------------
    def summary(self, filename, summary_out, fast):

        if fast and os.path.exists(summary_out):
            log.info('summary ------------ skipped ')
            return True
        log.info('summary ------------ begin ')


        scr_filename = os.path.join(idmt_scripts, 'imc_create_video_summary_visualization.py')
        out_filename = os.path.join(out_folder,   'summary.jpg')
        cmd_filename = os.path.join(out_folder,   'summary.sh')

        f = open(cmd_filename, 'w')
        # f.write( 'export LC_ALL="en_US.UTF-8"\n')
        f.write('export LC_ALL=\n')
        f.write('export LD_LIBRARY_PATH=/opt/idmt/lib/:$LD_LIBRARY_PATH\n\n')
        f.write('export IDMT_PY=' + idmt_py + '\n')
        f.write('export PYTHONPATH=$IDMT_PY:$PYTHONPATH\n')
        f.write('/usr/bin/python3 ' + scr_filename + ' \\\n')
        f.write('-f ' + filename + ' \\\n')
        f.write('-o ' + out_filename + ' \\\n')
        f.write('-w 1024 -e 120 \n')
        f.close()

        # TO FIX: output file should be .log and not .json
        res = self.run('/bin/bash ' + cmd_filename, params, 'summary')
        if res:
            log.info('summary ------------ ok ')
            return os.path.exists(out_filename)
        else:
            log.info('summary ------------ fail ')
            return False

    # -----------------------------------------------------
    def thumbs_index_storyboard(filename, out_folder, num_frames):

        log.info('index/storyboard---- begin ')

        movie_name = os.path.basename(out_folder)

        # retrieve shot frames
        lst = glob.glob(out_folder + '/tvs_s_*.jpg')
        lst.sort()
        num_shot = len(lst)
        if num_shot == 0:
            print("thumbs_index_storyboard: no shots!")
            return False

        im = Image.open(lst[0])
        ar = float(im.height / im.width)
        th_sz = (100, int(100 * ar))

        # prepare thumbnails
        th_folder = os.path.join(out_folder, 'thumbs')
        if not mkdir(th_folder, True):
            return False

        for fn in lst:
            im = Image.open(fn)
            im_small = im.resize(th_sz, Image.BILINEAR)
            im_small.save(fn.replace(out_folder, th_folder), quality=90)

        # prepare index
        idx_folder = os.path.join(out_folder, 'index')
        if not mkdir(idx_folder, True):
            return False

        num_col  = 5
        num_row  = num_shot // num_col
        if num_shot % num_col:
            num_row += 1
        idx_sz = (100 * num_col, int(100 * ar * num_row))
        idx_img = Image.new("RGB", idx_sz, '#ffffff')

        for i, fn in enumerate(lst):
            x = (i % num_col) * 100
            y = (i // num_col) * int(100 * ar)
            im = Image.open(fn)
            im_small = im.resize(th_sz, Image.BILINEAR)
            im_cp = im_small.copy()
            idx_img.paste(im_cp, (x, y))

        idx_img.save(idx_folder + '/index.jpg', quality=90)

        d = {}
        d['thumb_w'] = 100
        d['thumb_h'] = int(100 * ar)
        d['num_row'] = num_row
        d['num_col'] = num_col
        d['help'] = 'determine shot index from mouse pos as: index = x/thumb_w + (y/thumb_h)*num_col'
        str = json.dumps(d, indent=4)
        f = open(idx_folder + "/index.json", 'w')
        f.write(str)
        f.close()

        # prepare storyboard
        sb_folder = os.path.join(out_folder, 'storyboard')
        if not mkdir(sb_folder, True):
            return False

        sb = {}
        sb["movie"] = movie_name
        sb["shots"] = []

        for i, fn in enumerate(lst):

            im = Image.open(fn)
            w1, h1 = 200,  int(200.0 * im.height / im.width)
            im_small = im.resize((w1, h1), Image.BILINEAR)
            im_name = 'shot_{0:04d}.jpg'.format(i)
            im_small.save(sb_folder + '/' + im_name, quality=90)

            frame = filename_to_frame(fn)
            shot_len = 0
            if i != len(lst) - 1:
                nextframe = filename_to_frame(lst[i + 1])
            else:
                nextframe = num_frames

            shot_len = (nextframe - frame) / TRANSCODED_FRAMERATE
            shot_len = round(shot_len, 2)

            d = {}
            d['shot_num'] = i
            d['first_frame'] = frame
            d['last_frame'] = nextframe
            d['timecode'] = frame_to_timecode(frame)
            d['len_seconds'] = shot_len
            d['img'] = im_name
            sb['shots'].append(d)

        # insert video motion estimation
        vim_filename = os.path.join(out_folder, 'vimotion.xml')

        vim = {}
        vim_root = ET.parse(vim_filename).getroot()
        for m in vim_root.findall('module'):
            vim[m.attrib['name']] = [0] * num_frames
        vim_names = list(vim.keys())
        vim_names.sort()
        # names_wid = max( [len(i) for i in vim_names ])

        for m in vim_root.findall('module'):
            scores = vim[m.attrib['name']]
            for f in m.findall('frame'):
                frame = int(f.attrib['idx'])
                value = float(f.attrib['value'])
                scores[frame] = value

        for shot in sb['shots']:
            f0 = shot['first_frame']
            f1 = shot['last_frame']

            # ---- output come dizionario
            shot_vim_dic = {}
            for n in vim_names:
                values = vim[n][f0:f1]
                max_value = max(values)
                avg_value = sum(values) / float(len(values))
                shot_vim_dic[n] = (round(avg_value, 3), round(max_value, 3))
            shot['motions_dict'] = shot_vim_dic

            # --- output come lista sortata sulla probabilita

            shot_vim = []
            for n in vim_names:
                values = vim[n][f0:f1]
                avg_value = sum(values) / float(len(values))
                if avg_value > 0.1:
                    shot_vim.append((round(avg_value, 3), n))
            shot_vim.sort(reverse=True)

            shot['estimated_motions'] = shot_vim

        str = json.dumps(sb, indent=4)
        f = open(sb_folder + "/storyboard.json", 'w')
        f.write(str)
        f.close()

        log.info('index/storyboard---- ok ')
        return True

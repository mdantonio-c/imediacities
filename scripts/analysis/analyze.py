import sys
import os
import os.path
import getpass
import json
import datetime
import glob
import shutil

from PIL import Image
from subprocess import *


TRANSCODED_FRAMERATE = 24

if getpass.getuser() == 'simboden':
    host = 'sil_pc'
else:
    host = 'imc_vm'

if host == 'sil_pc': 
    root_dir = '/home/simboden/Desktop/IMC/worker_env/'
else:
    root_dir = '/'

stage_area   = root_dir + 'uploads'
analize_area = root_dir + 'uploads/Analize'
idmt_bin     = root_dir + 'code/imc/imedia-pipeline/tools'
idmt_scripts = root_dir + 'code/imc/imedia-pipeline/scripts'
idmt_py      = root_dir + 'code/imc/imedia-pipeline/scripts/idmt'

# default_movie   = '15b54855-49c8-437c-9ad3-9226695d2fb4/Grande_Manifestazione_Patriottica.mp4'
# default_movie   = '774688ec-dc09-4b38-90b6-9991e375d710/vivere_a_bologna.mov'
default_movie    = '00000000-0000-0000-00000000000000000/test_00.avi'
default_filename = os.path.join(stage_area, default_movie)

logfile = None


# -----------------------------------------------------
def log(msg):
    global logfile
    print(msg)
    sys.stdout.flush()
    time = datetime.datetime.now().strftime("[%d%b%y %H:%M:%S] ")
    logfile.write(time + msg + '\n')
    logfile.flush()


# -----------------------------------------------------
def mkdir(path, clean=False):
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
    substr = os.path.basename(f).replace('tvs_s_', '').replace('.jpg', '')
    return int(substr)


# -----------------------------------------------------
def frame_to_timecode(f, fps=25):
    f = int(f)
    t_hour  =  int(f / (3600 * fps))
    t_min   =  int( ( f - t_hour*3600*fps ) / ( 60*fps ) )
    t_sec   =  int( ( f - t_hour*3600*fps - t_min*60*fps ) / fps )
    t_frame =  int( ( f - t_hour*3600*fps - t_min*60*fps - t_sec*fps ) )
    timecode = '{0:02d}:{1:02d}:{2:02d}-f{3:02d}'.format( t_hour, t_min, t_sec, t_frame)
    return timecode


# -----------------------------------------------------
# make movie_analize_folder as :  analize_area / user_folder_name / movie_name
# and link the givel filename as  movie_analize_folder/origin + movie_ext
def make_movie_analize_folder(filename, clean=False):

    if not mkdir(analize_area): return ""

    user_folder = filename.replace(stage_area + '/', '').split('/')[0]
    user_analyze_folder = os.path.join(analize_area, user_folder)
    if not mkdir(user_analyze_folder) : return ""

    m_name, m_ext = os.path.splitext(os.path.basename(filename))
    movie_analize_folder = os.path.join(user_analyze_folder, m_name)
    if not mkdir(movie_analize_folder, clean): return ""

    origin_link = os.path.join(movie_analize_folder, 'origin')
    try:
        os.symlink(filename, origin_link)
    except :
        os.remove(origin_link)
        print('forcing origin link')
        os.symlink(filename, origin_link)

    return movie_analize_folder


#-----------------------------------------------------
def run(cmd, out_folder, out_name, err_name, cmd_name=None):

    if cmd_name:
        cmd_filename = os.path.join(out_folder, cmd_name)
        cmd_file = open(cmd_filename, 'w')
        cmd_file.write(cmd)
        cmd_file.close()

    out_filename = os.path.join( out_folder, out_name)
    err_filename = os.path.join( out_folder, err_name)

    out_file = open( out_filename, 'w')
    err_file = open( err_filename, 'w')

    p = Popen(cmd, shell=True, universal_newlines=True, stdout=out_file, stderr=err_file)
    res = p.wait()

    out_file.close()
    err_file.close()
    if res == 0:
        return True
    else:
        return False


# -----------------------------------------------------
def origin_tech_info(filename, out_folder):

    cmd_list = [] 
    cmd_list.append( '/usr/bin/ffprobe -v quiet -print_format json -show_format -show_streams' )
    cmd_list.append( filename )
    cmd = ' \\\n'.join(cmd_list) + '\n'

    res = run( cmd, out_folder, 'origin_info.json', 'origin_info.err', 'origin_info.sh' )

    ''' -- origin_info.json inspection example

    if res:

        out_filename = os.path.join( out_folder, 'origin_info.json')
        out_file = open( out_filename, 'r')
        data = json.load( out_file )
        print( '    movie tech info:')
        print( '    format', data['format']['format_long_name'])
        for s in data['streams'] :
            print( '   ', s['codec_type'], 'codec', s['codec_name'] )
    '''
    return res


# -----------------------------------------------------
def transcoded_tech_info(filename, out_folder):

    cmd_list = []
    cmd_list.append('/usr/bin/ffprobe -v quiet -print_format json -show_format -show_streams')
    cmd_list.append(filename)
    cmd = ' \\\n'.join(cmd_list) + '\n'

    res = run(cmd, out_folder, 'transcoded_info.json', 'transcoded_info.err', 'transcoded_info.sh')
    return res


# -----------------------------------------------------
def transcoded_num_frames(out_folder):
    out_filename = os.path.join(out_folder, 'transcoded_info.json')
    out_file = open(out_filename, 'r')
    data = json.load(out_file)	
    return int(data['streams'][0]['nb_frames'])


# -----------------------------------------------------
def transcode(filename, out_folder):

    out_filename = os.path.join( out_folder, 'transcoded.mp4')

    cmd_list = []
    cmd_list.append('/usr/bin/ffmpeg -hide_banner -nostdin -y')
    #cmd_list.append('-threads 4')
    cmd_list.append('-i ' + filename)
    cmd_list.append('-vf yadif=1:-1:0')                                                                       # deinterlacing
    cmd_list.append('-vcodec libx264 -crf 15.0 -pix_fmt yuv420p -coder 1 -rc_lookahead 60 -r ' +str(TRANSCODED_FRAMERATE)+ ' -strict -2' )  # video codec
    cmd_list.append('-g ' +str(TRANSCODED_FRAMERATE)+ ' -forced-idr 1 -sc_threshold 40 -bf 16 -refs 6 ' )                                   # keyframes
    cmd_list.append('-acodec aac -b:a 128k')                                                                  # audio codec
    cmd_list.append(out_filename)

    cmd = ' \\\n'.join(cmd_list) + '\n'

    bk_filename = out_filename + ".bk"
    if os.path.exists(bk_filename):
        os.remove(bk_filename)
    if os.path.exists(out_filename):
        os.rename(out_filename, bk_filename)
    
    if not run(cmd, out_folder, 'transcode.log', 'transcode.err', 'transcode.sh'):
        return False
    return os.path.exists(out_filename)

    # to check if a movie is sane --- try to encode using a null output, so you only do the reading
    # ffmpeg -v error -i input -f null - 2> error.log


# -----------------------------------------------------
def tvs(filename, out_folder):
    
    prg_filename = os.path.join( idmt_bin,   'idmtvideoanalysis')
    out_filename = os.path.join( out_folder, 'tvs.xml')
    cmd_filename = os.path.join( out_folder, 'tvs.sh')
    sht_filename = os.path.join( out_folder, 'tvs_s_%05d.jpg')
    key_filename = os.path.join( out_folder, 'tvs_k_%05d.jpg')

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

    if not run('/bin/bash ' + cmd_filename, out_folder, 'tvs.log', 'tvs.err'):
        return False
    return os.path.exists(out_filename)


# -----------------------------------------------------
def quality(filename, out_folder):
    
    prg_filename = os.path.join( idmt_bin,   'idmtvideoanalysis')
    out_filename = os.path.join( out_folder, 'quality.xml')
    cmd_filename = os.path.join( out_folder, 'quality.sh')
       

    f = open(cmd_filename, 'w')
    # f.write('export LC_ALL="en_US.UTF-8"\n')
    f.write('export LC_ALL=\n')
    f.write('export LD_LIBRARY_PATH=/opt/idmt/lib/:$LD_LIBRARY_PATH\n\n')
    f.write(prg_filename+' \\\n')
    f.write('-f ' + filename + ' \\\n')
    f.write('-o ' + out_filename + ' \\\n')
    f.write('-t quality \n')
    f.close()

    if not run( '/bin/bash ' + cmd_filename, out_folder, 'quality.log', 'quality.err'):
        return False
    return os.path.exists(out_filename)


# -----------------------------------------------------
def vimotion(filename, out_folder):
    
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

    if not run('/bin/bash ' + cmd_filename, out_folder, 'vimotion.log', 'vimotion.err'):
        return False
    return os.path.exists(out_filename)
     

# -----------------------------------------------------
def summary(filename, out_folder):
    
    scr_filename = os.path.join( idmt_scripts, 'imc_create_video_summary_visualization.py' )
    out_filename = os.path.join( out_folder,   'summary.jpg')
    cmd_filename = os.path.join( out_folder,   'summary.sh' )

    f = open( cmd_filename, 'w' )
    #f.write( 'export LC_ALL="en_US.UTF-8"\n')
    f.write( 'export LC_ALL=\n')
    f.write( 'export LD_LIBRARY_PATH=/opt/idmt/lib/:$LD_LIBRARY_PATH\n\n')
    f.write( 'export IDMT_PY='+idmt_py+'\n' )
    f.write( 'export PYTHONPATH=$IDMT_PY:$PYTHONPATH\n' )
    f.write( '/usr/bin/python3 ' +scr_filename+ ' \\\n' )
    f.write( '-f '+filename+   ' \\\n' )
    f.write( '-o '+out_filename+   ' \\\n' )
    f.write( '-w 1024 -e 120 \n' )
    f.close()

    if not run( '/bin/bash '+cmd_filename, out_folder, 'summary.log', 'summary.err' ):
        return False
    return os.path.exists( out_filename ) 

# -----------------------------------------------------
def thumbs_index_storyboard(filename, out_folder, num_frames):

    movie_name = os.path.basename(out_folder)

    # retrieve shot frames
    lst = glob.glob( out_folder + '/tvs_s_*.jpg')
    lst.sort()
    num_shot = len(lst)
    if num_shot == 0:
        print("thumbs_index_storyboard: no shots!")
        return False
    
    im = Image.open(lst[0])
    ar = float(im.height / im.width)
    th_sz = ( 100, int( 100*ar ) )

    # prepare thumbnails
    th_folder = os.path.join( out_folder, 'thumbs')
    if not mkdir(th_folder, True):
        return False

    for fn in lst:
        im = Image.open(fn)
        im_small = im.resize( th_sz, Image.BILINEAR )
        im_small.save( fn.replace(out_folder,th_folder), quality=90 )

    # prepare index
    idx_folder = os.path.join( out_folder, 'index')
    if not mkdir(idx_folder, True):
        return False

    num_col  = 5
    num_row  = num_shot // num_col
    if num_shot % num_col:
        num_row += 1
    idx_sz = ( 100*num_col, int(100*ar*num_row) )    
    idx_img = Image.new( "RGB", idx_sz, '#ffffff' )

    for i, fn in enumerate(lst):
        x = (i % num_col) * 100
        y = (i // num_col) * int(100*ar)
        im = Image.open(fn)
        im_small = im.resize( th_sz, Image.BILINEAR )
        im_cp = im_small.copy()
        idx_img.paste( im_cp, (x,y) )

    idx_img.save( idx_folder + '/index.jpg' , quality=90 )    
        
    d = {}
    d['thumb_w'] = 100
    d['thumb_h'] = int(100*ar)
    d['num_row'] = num_row
    d['num_col'] = num_col
    d['help'] = 'determine shot index from mouse pos as: index = x/thumb_w + (y/thumb_h)*num_col'
    str = json.dumps( d, indent=4 )
    f = open(idx_folder + "/index.json", 'w')
    f.write(str)
    f.close()

    # prepare storyboard
    sb_folder = os.path.join( out_folder, 'storyboard')
    if not mkdir(sb_folder, True):
        return False

    sb = {}
    sb["movie"] = movie_name
    sb["shots"] = []
    
    for i, fn in enumerate(lst):

        im = Image.open(fn)
        w1,h1 = 200,  int(200.0* im.height / im.width)
        im_small = im.resize((w1,h1), Image.BILINEAR)
        im_name = 'shot_{0:04d}.jpg'.format(i)
        im_small.save(sb_folder+'/'+im_name, quality=90)
                
        frame = filename_to_frame(fn)
        shot_len = 0
        if i != len(lst)-1:
            nextframe = filename_to_frame(lst[i+1])
            shot_len = ( nextframe - frame ) / TRANSCODED_FRAMERATE
        else:
            shot_len = ( num_frames - frame ) / TRANSCODED_FRAMERATE

        d = {}
        d['shot_num'] = i
        d['img']      = im_name
        d['timecode'] = frame_to_timecode(frame)
        d['frame']    = frame
        d['len']      = shot_len 
        sb["shots"].append( d )        

    str = json.dumps(sb, indent=4)
    f = open(sb_folder + "/storyboard.json", 'w')
    f.write(str)
    f.close()

    return True


# -----------------------------------------------------
def analize(filename, out_folder, fast=False):

    log('origin_tech_info --- begin')
    if not origin_tech_info( filename, out_folder ):
        return False
    log('origin_tech_info --- ok ')

    tr_movie = os.path.join( out_folder, 'transcoded.mp4')
    got_tr_movie = os.path.exists(tr_movie)

    if  fast and  got_tr_movie:
        log('transcode ---------- skipped')
    else:
        log('transcode ---------- begin ')
        if not transcode( filename, out_folder ):
            return False
        log('transcode ---------- ok ')

    log( 'transcoded_info ---- begin ')
    if not transcoded_tech_info( tr_movie, out_folder ):
        return False
    log( 'transcoded_info ---- ok ')
    
    nf = transcoded_num_frames(out_folder)

    tvs_out = os.path.join( out_folder, 'tvs.xml')
    got_tvs = os.path.exists( tvs_out )

    if  fast and  got_tvs:
        log('tvs ---------------- skipped')
    else:
        log('tvs ---------------- begin ')
        if not tvs(tr_movie, out_folder):
            return False
        log('tvs ---------------- ok ')


    if  fast:
        log('quality ------------ skipped ')
    else:
        log('quality ------------ begin ')
        if not quality(tr_movie, out_folder):
            return False
        log('quality ------------ ok ')

    if  fast:
        log('vimotion ----------- skipped ')
    else:
        log('vimotion ----------- begin ')
        if not vimotion(tr_movie, out_folder):
            return False
        log( 'vimotion ----------- ok ')

    log('summary ------------ begin ')
    if not summary(tr_movie, out_folder):
        return False
    log('summary ------------ ok ')

    log('index/storyboard---- begin ')
    if not thumbs_index_storyboard(tr_movie, out_folder, nf):
        return False
    log('index/storyboard---- ok ')

    return True

# -----------------------------------------------------
help = ''' usage:  python3 analyze.py [options] [filename]
options:
[-fast  ]       skip transcoding ( if transcoded.mp4 is ready ), skip tvs ( if tvs.xml is ready ) skip quality, skip vimotion 
[-clean ]       clean any previous data before analize 
[filename ]     if omitted use the default movie 
'''
# -----------------------------------------------------
def main(args):
    global logfile

    clean = False
    fast  = False
    movie = default_filename

    args = sys.argv[1:]
    num_args = len(args)
    for i, a in enumerate(args):
        if a == '--help' or a == '-help' or a == '-h':
            print(help)
            return
        elif a == '-clean':
            clean = True
        elif a == '-fast':
            fast = True
            clean = False  # fast is stronger than clean
        else:
            movie = a

    filename = os.path.join(stage_area, movie)
    if not os.path.exists(filename):
        print('aborting: bad input file', filename)
        return

    out_folder = make_movie_analize_folder(filename)
    if out_folder == "":
        print('aborting: failed to create out_folder')
        return

    logfile = open(os.path.join(out_folder, "log.txt"), "w")
    log("Analize " + movie)

    if analize(filename, out_folder, fast):
        log('Analize done')
    else:
        log('Analize terminated with errors')

# -----------------------------------------------------


if __name__ == "__main__":
    main(sys.argv[1:])

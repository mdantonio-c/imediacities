import sys
import os
import os.path
import getpass
import json
from subprocess import *


if getpass.getuser() == 'simboden':
    host = 'sil_pc'
else:
    host = 'imc_vm'    

if host=='sil_pc':    
    root_dir = '/home/simboden/Desktop/IMC/DEVEL'
else:
    #root_dir = '/home/ubuntu/imediacities'
    root_dir = '/'

#stage_area   = root_dir + '/imediastuff'
#analize_area = root_dir + '/imediastuff/Analize' 
#idmt_bin     = root_dir + '/imedia-pipeline/tools'
#idmt_scripts = root_dir + '/imedia-pipeline/scripts'
#idmt_py      = root_dir + '/imedia-pipeline/scripts/idmt'

stage_area   = root_dir + 'uploads'
analize_area = root_dir + 'uploads/Analize' 
idmt_bin     = root_dir + 'code/imc/imedia-pipeline/tools'
idmt_scripts = root_dir + 'code/imc/imedia-pipeline/scripts'
idmt_py      = root_dir + 'code/imc/imedia-pipeline/scripts/idmt'

#default_movie   = '15b54855-49c8-437c-9ad3-9226695d2fb4/Grande_Manifestazione_Patriottica.mp4'
#default_movie   = '774688ec-dc09-4b38-90b6-9991e375d710/vivere_a_bologna.mov'
default_movie    = '00000000-0000-0000-00000000000000000/test_00.avi'
default_filename = os.path.join( stage_area, default_movie )

#-----------------------------------------------------
def mkdir(path):
    if not os.path.isdir(path):
        os.mkdir(path)
    if not os.path.isdir(path):
        print( "ERROR failed to create", path )
        return False
    return True

#-----------------------------------------------------
# make movie_analize_folder as :  analize_area / user_folder_name / movie_name
# and link the givel filename as  movie_analize_folder/origin + movie_ext

def make_movie_analize_folder(filename):

    if( not mkdir(analize_area) ) : return ""

    user_folder = filename.replace(stage_area+'/','').split('/')[0]
    user_analyze_folder = os.path.join( analize_area, user_folder )
    if( not mkdir(user_analyze_folder) ) : return ""

    m_name, m_ext = os.path.splitext( os.path.basename( filename ) )
    movie_analize_folder = os.path.join( user_analyze_folder, m_name )
    if( not mkdir(movie_analize_folder) ) : return ""

    origin_link = os.path.join( movie_analize_folder, 'origin' )
    if os.path.exists(origin_link):
        os.remove(origin_link)
    os.symlink( filename, origin_link )

    return movie_analize_folder

#-----------------------------------------------------
def run( cmd, out_folder, out_name, err_name, cmd_name=None ):

    if cmd_name:
        cmd_filename = os.path.join( out_folder, cmd_name )
        cmd_file = open( cmd_filename, 'w' )
        cmd_file.write( cmd )
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
    
#-----------------------------------------------------
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

#-----------------------------------------------------
def transcoded_tech_info(filename, out_folder):

    cmd_list = [] 
    cmd_list.append( '/usr/bin/ffprobe -v quiet -print_format json -show_format -show_streams' )
    cmd_list.append( filename )
    cmd = ' \\\n'.join(cmd_list) + '\n'

    res = run( cmd, out_folder, 'transcoded_info.json', 'transcoded_info.err', 'transcoded_info.sh' )
    return res


#-----------------------------------------------------
def transcode(filename, out_folder):

    out_filename = os.path.join( out_folder, 'transcoded.mp4' )

    cmd_list = []
    cmd_list.append( '/usr/bin/ffmpeg -hide_banner -nostdin -y' )
    #cmd_list.append('-threads 4' )
    cmd_list.append( '-i ' + filename )
    cmd_list.append( '-vf yadif=1:-1:0' )                                                                       # deinterlacing
    cmd_list.append( '-vcodec libx264 -crf 15.0 -pix_fmt yuv420p -coder 1 -rc_lookahead 60 -r 24 -strict -2' )  # video codec
    cmd_list.append( '-g 24 -forced-idr 1 -sc_threshold 40 -bf 16 -refs 6 ' )                                   # keyframes
    cmd_list.append( '-acodec aac -b:a 128k' )                                                                  # audio codec
    cmd_list.append( out_filename )

    cmd = ' \\\n'.join(cmd_list) + '\n'

    bk_filename = out_filename + ".bk"
    if os.path.exists( bk_filename ):
        os.remove( bk_filename )
    if os.path.exists( out_filename ):
        os.rename( out_filename, bk_filename )
    
    if not run( cmd, out_folder, 'transcode.log', 'transcode.err', 'transcode.sh' ):
        return False
    return os.path.exists( out_filename )

    # to check if a movie is sane --- try to encode using a null output, so you only do the reading
    # ffmpeg -v error -i input -f null - 2> error.log


#-----------------------------------------------------
def tvs(filename, out_folder):
    
    prg_filename = os.path.join( idmt_bin,   'idmtvideoanalysis' )
    out_filename = os.path.join( out_folder, 'tvs.xml')
    cmd_filename = os.path.join( out_folder, 'tvs.sh' )
    sht_filename = os.path.join( out_folder, 'tvs_s_%05d.jpg' )
    key_filename = os.path.join( out_folder, 'tvs_k_%05d.jpg' )

    f = open( cmd_filename, 'w' )
    #f.write( 'export LC_ALL="en_US.UTF-8"\n')
    f.write( 'export LC_ALL=\n')
    f.write( 'export LD_LIBRARY_PATH=/opt/idmt/lib/:$LD_LIBRARY_PATH\n\n')
    f.write( prg_filename+' \\\n' )
    f.write( '-f '+filename+   ' \\\n' )
    f.write( '-o ' +out_filename+ ' \\\n' )
    f.write( '-s ' +sht_filename+ ' \\\n' )
    f.write( '-k ' +key_filename+ ' \\\n' ) 
    f.write( '-t tvs \n' )
    f.close()

    if not run( '/bin/bash '+cmd_filename, out_folder, 'tvs.log', 'tvs.err' ):
        return False
    return os.path.exists( out_filename )

#-----------------------------------------------------
def quality(filename, out_folder):
    
    prg_filename = os.path.join( idmt_bin,   'idmtvideoanalysis' )
    out_filename = os.path.join( out_folder, 'quality.xml')
    cmd_filename = os.path.join( out_folder, 'quality.sh' )
       

    f = open( cmd_filename, 'w' )
    #f.write( 'export LC_ALL="en_US.UTF-8"\n')
    f.write( 'export LC_ALL=\n')
    f.write( 'export LD_LIBRARY_PATH=/opt/idmt/lib/:$LD_LIBRARY_PATH\n\n')
    f.write( prg_filename+' \\\n' )
    f.write( '-f '+filename+   ' \\\n' )
    f.write( '-o ' +out_filename+ ' \\\n' )
    f.write( '-t quality \n' )
    f.close()

    if not run( '/bin/bash '+cmd_filename, out_folder, 'quality.log', 'quality.err' ):
        return False
    return os.path.exists( out_filename )

#-----------------------------------------------------
def vimotion(filename, out_folder):
    
    prg_filename = os.path.join( idmt_bin,   'idmtvideoanalysis' )
    out_filename = os.path.join( out_folder, 'vimotion.xml')
    cmd_filename = os.path.join( out_folder, 'vimotion.sh' )

    f = open( cmd_filename, 'w' )
    #f.write( 'export LC_ALL="en_US.UTF-8"\n')
    f.write( 'export LC_ALL=\n')
    f.write( 'export LD_LIBRARY_PATH=/opt/idmt/lib/:$LD_LIBRARY_PATH\n\n')
    f.write( prg_filename+' \\\n' )
    f.write( '-f '+filename+   ' \\\n' )
    f.write( '-o ' +out_filename+ ' \\\n' )
    f.write( '-c 0.1 \\\n' )
    f.write( '-t vimotion \n' )
    f.close()

    if not run( '/bin/bash '+cmd_filename, out_folder, 'vimotion.log', 'vimotion.err' ):
        return False
    return os.path.exists( out_filename )
     

#-----------------------------------------------------
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

#-----------------------------------------------------
def analize( filename ):

    if not os.path.exists( filename ):
        print( 'aborting: bad input file',filename )
        return False

    print( 'make_out_folder ---- begin')
    out_folder = make_movie_analize_folder( filename )
    if  out_folder == ""  :
        return False
    print( 'make_out_folder ---- ok')

    print( 'origin_tech_info --- begin')
    if not origin_tech_info( filename, out_folder ) :
        return False
    print( 'origin_tech_info --- ok ')

    print( 'transcode ---------- begin ')
    if not transcode( filename, out_folder ) :
        return False
    print( 'transcode ---------- ok ')
    tr_movie = os.path.join( out_folder, 'transcoded.mp4' )        

    print( 'transcoded_info ---- begin ')
    if not transcoded_tech_info( tr_movie, out_folder ) :
        return False
    print( 'transcoded_info ---- ok ')
    
    print( 'tvs ---------------- begin ')
    if not tvs( tr_movie, out_folder ) :
        return False
    print( 'tvs ---------------- ok ')

    print( 'quality ------------ begin ')
    if not quality( tr_movie, out_folder ) :
        return False
    print( 'quality ------------ ok ')

    print( 'vimotion ----------- begin ')
    if not vimotion( tr_movie, out_folder ) :
        return False
    print( 'vimotion ----------- ok ')

    print( 'summary ------------ begin ')
    if not summary( tr_movie, out_folder ) :
        return False
    print( 'summary ------------ ok ')

    return True

#-----------------------------------------------------
if __name__ == "__main__":
    if len( sys.argv ) > 1 :
        filename = sys.argv[1]
    else:
        filename = default_filename

    print( 'Analize', filename )
    if analize(filename):
        print( 'Analize done')
    else:
        print( 'Analize terminated with errors')
                                                                  
# TODO: -- decidere quando serve il transcoding, e il deinterallacciamento
# TODO: -- registrare il timing
# TODO: -- trattare i sottotitoli
# TODO: -- prevedere diverse modalita' di esecuzione : clean, preserve, ...
# TODO: -- VALIDATE ANALISIS -- vedere che ci sono tutti i file, e sono validi




# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 12:23:05 2019

@author: hwchai_PIMS
"""

# -*- coding: utf-8 -*-
"""
Created on Sat May 23 12:26:06 2015

@author: xhxiao
"""

#from tomopy.io.reader import *
#from numpy.testing import assert_allclose
import tomopy 
from tomopy.recon.rotation import write_center
from tomopy.recon.algorithm import recon
from tomopy import minus_log
import os, h5py, glob, fnmatch
import numpy as np
from scipy import misc
import time 
import dxchange
#import h5py
import shutil


def dataInfo(filename,showInfor=False):
    f = h5py.File(filename,"r")
    try:    
        arr = f["exchange/data"] 
        print '!!!!! Infor !!!!!'
        dim = arr.shape
        if showInfor == True:
            print 'Data dimension is [Theta:Y:X] = [', dim[0],':', dim[1],':', dim[2],']'
        arr = f["exchange/data_white"]
        if arr.shape[0] == 1:
            print '!!!!! Infor !!!!! '
            print 'There is no white images in this file.'
        arr = f["exchange/data_dark"] 
        if arr.shape[0] == 1:
            print '!!!!! Infor !!!!! '
            print 'There is no dark images in this file.'
        return dim    
    except:
        print '!!!!! Error !!!!!' 
        print 'Dataset \'exchange/data\' does not exist in the give file.'
        return 0    



def dataStandardReader(filename,sliceStart=0,sliceEnd=20,flat_name=None,dark_name=None):
    if flat_name != None:
        flat_name = flat_name
    if dark_name != None:
        dark_name = dark_name 
    
    if flat_name == None:
        flat_name = filename
    if dark_name == None:    
        dark_name = filename

    f = h5py.File(flat_name,"r")
    arr = f["exchange/data_white"]
    if (arr.shape[0]<=1 and flat_name==None):
        print '!!!!!! Error !!!!!'
        print 'There is no flat images in the file! Please provide an alternative file with flat images (using argument \'flat_name=some_name\').' 
        return 0,0,0
    f = h5py.File(dark_name,"r")
    arr = f["exchange/data_dark"]
    if (arr.shape[0]<=1 and dark_name==None):
        print '!!!!! Error !!!!!'
        print 'There is no dark images in the file! Please provide an alternative file with dark images (using argument \'dark_name=some_name\').'      
        return 0,0,0   
        
    f = h5py.File(filename,"r")
    try:    
        arr = f["exchange/data"] 
    except:
        print '!!!!!Error!!!!!' 
        print 'Dataset \'exchange/data\' does not exist in the give file.'
        return 0,0,0
    data = arr[:,sliceStart:sliceEnd,:]
    f.close()
    
    f = h5py.File(flat_name,"r")
    try:
        arr = f["exchange/data_white"]
    except:
        print '!!!!!Error!!!!!' 
        print 'Dataset \'exchange/data_white\' does not exist in the give file.'
        return 0,0,0
    white = arr[1:9,sliceStart:sliceEnd,:]
    f.close()
    
    f = h5py.File(dark_name,"r")
    try:
        arr = f["exchange/data_dark"]
    except:
        print '!!!!!Error!!!!!'
        print 'Dataset \'exchange/data_dark\' does not exist in the give file.' 
        return 0,0,0
    dark = arr[1:9,sliceStart:sliceEnd,:]
    f.close()
    
    print 'Data is read successfully'
    return data,white,dark


        
        
def getFiles(user_top_dir,output_dir,Exp_idx):
    data_top_dir = user_top_dir + '/'
    output_dir = output_dir + '/'
#    print os.path.join(data_top_dir,'Exp'+'{:03}'.format(Exp_idx)+'*')
    #data_dir = glob.glob(os.path.join(data_top_dir,'Exp'+'{:03}'.format(Exp_idx)+'*'))[0]
    data_dir = glob.glob(os.path.join(data_top_dir,'Exp'+'{:03}'.format(Exp_idx)+'*'))[0]
    #output_dir = os.path.join(output_dir,data_dir[data_dir.find(data_top_dir)+len(data_top_dir):])
    output_dir = os.path.join(output_dir,data_dir[data_dir.find(data_top_dir)+len(data_top_dir):-3])
    
    print data_dir,output_dir

    #filenames = np.sort(fnmatch.filter(os.listdir(data_dir),'*.hdf'))
    #if len(filenames) == 0:
    #    filenames = np.sort(fnmatch.filter(os.listdir(data_dir),'*.h'))
    filenames = np.sort(fnmatch.filter(os.listdir(data_top_dir),'Exp'+'{:03}'.format(Exp_idx)+'*.h5'))

    print filenames

    if len(filenames)  == 0:
        print '!!!!!Error!!!!! There is no valid hdf5 data file in the given path and Exp folder.' 
        return 0,0

    data_files = []
    output_files = []
    for ii in range(len(filenames)):
        data_files.append(os.path.join(data_top_dir, filenames[ii]))
        #output_files.append(output_dir+'/recon_'+filenames[ii].split(".")[-2]+'/recon_'+filenames[ii].split(".")[-2])
        output_files.append(output_dir+'/recon_')  
    
    return data_files, output_files         




def generalFilterContainer(data,**kwargs): 
    """
       kwargs: kwargs using format of filternameParams. For instance, to use filter
               remove_stripe_sf, you need to provide a kwarg 
               remove_stripe_sfParams = {'use':'yes','size':31}
               By default, this routine assume five filters
               1. retrieve_phase
               2. remove_stripe_fw
               3. remove_stripe_ti
               4. remove_stripe_sf
               5. normalize_bg
               
               in the __main__ function below, this functions uses all five filters.
               You can set 'use':'no' in a filter kwargs to disable that filter. You 
               can also include more filters in this function in the same format per
               your purposes.
    """ 
    kws = kwargs.keys()
    if 'remove_stripe_fwParams' in kws: 
         params = kwargs['remove_stripe_fwParams'] 
         if params['use'] != 'no':  
             del params['use']
             data = tomopy.prep.stripe.remove_stripe_fw(data,**params)
             params['use'] = 'yes'
             print 'remove_stripe_fw is done'
    if 'retrieve_phaseParams' in kws: 
         params = kwargs['retrieve_phaseParams'] 
         print params
         if params['use'] != 'no':   
             del params['use']
             data = 1 - data 
             data = tomopy.prep.phase.retrieve_phase(data,**params) 
             params['use'] = 'yes'
             print 'retrieve_phase is done'
    if 'remove_stripe_tiParams' in kws: 
         params = kwargs['remove_stripe_tiParams'] 
         if params['use'] != 'no':  
             del params['use']
             data = tomopy.prep.stripe.remove_stripe_ti(data,**params)
             params['use'] = 'yes'
             print 'remove_stripe_ti is done'
    if 'remove_stripe_sfParams' in kws: 
         params = kwargs['remove_stripe_sfParams'] 
         if params['use'] != 'no':  
             del params['use']
             data = tomopy.prep.stripe.remove_stripe_sf(data,**params) 
             params['use'] = 'yes'
             print 'remove_stripe_sf is done'
    if 'normalize_bgParams' in kws: 
         params = kwargs['normalize_bgParams'] 
         if params['use'] != 'no':  
             del params['use']
             data = tomopy.prep.normalize.normalize_bg(data,**params) 
             params['use'] = 'yes'
             print 'normalize_bg is done'

    return data




def manualFindCenter(filename,output_file,center_shift,center_shift_w,
                     zinger=None,zinger_level=1000,sliceStart=100,sliceEnd=120,
                     data_center_path=None,flat_name=None,dark_name=None,
                     mask=False,mask_ratio=1,**kwargs):
    dim = dataInfo(filename)
    theta = np.linspace(0,np.pi,num=dim[0]+1)
    
    if kwargs.has_key('ExplicitParams'):
        sliceStart = kwargs['ExplicitParams']['sliceStart']
        sliceEnd = kwargs['ExplicitParams']['sliceEnd']
        zinger = kwargs['ExplicitParams']['zinger']
        zinger_level = kwargs['ExplicitParams']['zinger_level']
        data_center_path = kwargs['ExplicitParams']['data_center_path']
        flat_name = kwargs['ExplicitParams']['flat_name']
        dark_name = kwargs['ExplicitParams']['dark_name'] 
        mask = kwargs['ExplicitParams']['mask'] 
        mask_ratio = kwargs['ExplicitParams']['mask_ratio']
        

    data,white,dark = dataStandardReader(filename,sliceStart=sliceStart,sliceEnd=sliceEnd,
                                         flat_name=flat_name,dark_name=dark_name)
   
    if data.all() == 0:
        print 'Reconstruction is terminated due to data file error.'
        exit()
    
    data_size = data.shape
    theta = np.linspace(0,np.pi,num=data_size[0]+1) 
    print 'data is read'
    
#    # remove zingers (pixels with abnormal counts)
    if zinger == True:
        data = tomopy.misc.corr.remove_outlier(data,zinger_level,size=15,axis=0)
        white = tomopy.misc.corr.remove_outlier(white,zinger_level,size=15,axis=0)
        print  'remove outlier is done'
    
    # normalize projection images; for now you need to do below two operations in sequence
    data = tomopy.prep.normalize.normalize(data,white,dark)
    print 'normalization is done'
    
    data = generalFilterContainer(data,**kwargs) 
        
#    data = tomopy.prep.normalize.minus_log(data)
    if data_center_path==None:
        data_center_path = '~/tomopy_data_center'
    write_center(data[:,int(data_size[1]/2)-1:int(data_size[1]/2)+1,:], theta, dpath=data_center_path, 
                 cen_range=(data.shape[2]/2+center_shift,data.shape[2]/2+center_shift+center_shift_w,0.5),
                 mask = mask, ratio = mask_ratio)



             
def loopEngine(filename,output_file,center=False,zinger=None,zinger_level=1000,offset=0,num_chunk=1,
               chunk_size=50,numRecSlices=50,margin_slices=30,flat_name=None,dark_name=None,
               mask=False,mask_ratio=1,**kwargs):
    dim = dataInfo(filename)
    numSlices = dim[1]  
    
    if kwargs.has_key('ExplicitParams'):
        center = kwargs['ExplicitParams']['center']
        zinger = kwargs['ExplicitParams']['zinger']
        zinger_level = kwargs['ExplicitParams']['zinger_level']
        offset = kwargs['ExplicitParams']['offset']
        num_chunk = kwargs['ExplicitParams']['num_chunk']
        chunk_size = kwargs['ExplicitParams']['chunk_size']
        numRecSlices = kwargs['ExplicitParams']['numRecSlices']
        margin_slices = kwargs['ExplicitParams']['margin_slices']
        flat_name = kwargs['ExplicitParams']['flat_name']
        dark_name = kwargs['ExplicitParams']['dark_name'] 
        mask = kwargs['ExplicitParams']['mask'] 
        mask_ratio = kwargs['ExplicitParams']['mask_ratio']
        
    if offset == None:
        offset = 0
    if numRecSlices == None:
        numRecSlices = dim[0] 
             
    state = 1
    for ii in range(num_chunk):   
        print 'chunk ',ii, ' reconstruction starts'                                                 
        print time.asctime()  
        
        if ii == 0:
            sliceStart = offset + ii*chunk_size
            sliceEnd = offset + (ii+1)*chunk_size
        else:
            sliceStart = offset + ii*(chunk_size-margin_slices)
            sliceEnd = offset + sliceStart + chunk_size
            if sliceEnd > (offset+numRecSlices):
                sliceEnd = offset+numRecSlices
            if sliceEnd > numSlices:
                sliceEnd = numSlices                
        
        if (sliceEnd - sliceStart) <= margin_slices:
            print 'Reconstruction finishes!'
            break        
    
        data,white,dark = dataStandardReader(filename,sliceStart=sliceStart,sliceEnd=sliceEnd,
                                             flat_name=flat_name,dark_name=dark_name)
   
        if data.all() == 0:
            state = 0
            break
        
        data_size = data.shape
        theta = np.linspace(0,np.pi,num=data_size[0]+1) 
        print 'data is read'
        
    #    # remove zingers (pixels with abnormal counts)
        if zinger == True:
            data = tomopy.misc.corr.remove_outlier(data,zinger_level,size=15,axis=0)
            white = tomopy.misc.corr.remove_outlier(white,zinger_level,size=15,axis=0)
            print  'remove outlier is done'
        
        # normalize projection images; for now you need to do below two operations in sequence
        data = tomopy.prep.normalize.normalize(data,white,dark)
        print 'normalization is done'
        
        data = generalFilterContainer(data,**kwargs)   

        if ii == 0 and center == False:
            center = tomopy.find_center_vo(data)
            
        print center    
        # tomo reconstruction
#        data = tomopy.prep.normalize.minus_log(data)
        data_recon = recon(data,theta,center=center,algorithm='gridrec')
        print 'reconstruction is done'
        
        if mask == True:
            data_recon = tomopy.circ_mask(data_recon, 0, ratio=mask_ratio)
        
        # save reconstructions
        dxchange.writer.write_tiff_stack(data_recon[np.int(margin_slices/2):(sliceEnd-sliceStart-np.int(margin_slices/2)),:,:], 
                                                     axis = 0,
                                                     fname = output_file, 
                                                     start = sliceStart+np.int(margin_slices/2),
                                                     overwrite = True)
        print 'chunk ',ii, ' reconstruction is saved'                                                 
        print time.asctime()
    
    if state == 1:
        print 'Reconstruction finishes!'  
    else:
        print 'Reconstruction is terminated due to data file error.'





if __name__ == '__main__':
############################### user input section -- Start ############################### 
##### This is the only section which you need to edit
    # TBelow is the top data directory in which 'ExpXYZ...' are located    
#    user_top_dir = '/run/media/user2bmb/My Passport/APS_2BM_2018_01' 
    #user_top_dir = '/mnt/APS_DATA/APS_201904/APS_2BM/projection'        # HDF file directory   These directory must without '/' at end
    user_top_dir = '/mnt/hgfs/share_with_windows'
    data_center_path = '/mnt/hgfs/share_with_windows/tomopy_201904/data_center'   # output center slice directory
    output_dir = '/mnt/hgfs/share_with_windows/tomopy_201904/data_tomography'     # output reconstruction slice directory

    #file_center = open(os.path.join(user_top_dir,'data_center.txt'))
    #file_center = open(os.path.join('/home/hwchai','data_center.txt'))
    #center_str = file_center.read()
    #file_center.close()
    #center_strs = center_str.split('\n')
    
    # Below you define list of data sets that you like to do volume reconstructions together
    #Exp_idx = np.arange(168,184,1)
    Exp_idx = [6]

    bad_data = []                             # 159,282,308 data was deleted  by hwchai at APS because the data will not been used
    for bad_data_index in bad_data:
        while bad_data_index in Exp_idx:
            Exp_idx.remove(bad_data_index)

    remove_tree = True   # Set to True if you want to remove old version data, and False if not. It just for reconstruct volume. for find data center will always remove old version data.
    
    # If your data does not have flat and dark images saved in same data file as sample image data,
    # you can specify an alternative file for reading flat and dark images. Otherwise, you can define
    # flat_name and dark_name as None
#    flat_name = '/local/data/2018_04/Wenlu/Exp006_BD3_furnaceT_30C_refT_27C_00_YPos1.8mm_SatApr7_11_27_05_2018_edge_10x_300mm_100.0msecExpTime_1.0DegPerSec_Rolling_20umLuAG_1mmC_2.657mrad_USArm1.349_monoY_-0.1_AHutch/proj_0006.hdf'
#    dark_name = flat_name
    flat_name = None
    dark_name = None
    
    # With manualCenter = True, you can do trial reconExp028_Epoxy_03_0C_00_YPos21.34mm_TueJan30_20_50_45_2018_edge_5x_60mm_67structions to find rotation center of one slice. 
    # This is also useful to quickly test reconstruction parameters by inspecting the reconstructed slice
    # images. Set manualCenter = False to do volume reconstruction    
    manualCenter = True
    if manualCenter == True:
        center_shift = -15     # relative center shift from projection image center
        center_shift_w = 15  # trial reconstruction center window size starting from center_shift
        sliceStart = 1000     # This define which slice image you want to check. 
        sliceEnd = sliceStart + 20
        zinger = True
    else:
        center_list = np.zeros(len(Exp_idx))
        for i in range(len(Exp_idx)):
            for center_str in center_strs:
                if len(center_str) > 12 and Exp_idx[i] == int(center_str[3:6]):
                    center_list[i] = int(center_str[7:11])+0.1*int(center_str[12:13])
                    continue
            if center_list[i] == 0:
                print Exp_idx,'center has not been found'
                Exp_idx[i] = None
        while None in Exp_idx:
            Exp_idx.remove(None)

        #data_center_path = os.path.join(os.path.abspath(os.path.join(user_top_dir,'..')),'data_center')

    offset = None       # set to None if you want to reconstruct the whole volume
    numRecSlices = 100    # set to None if you want to reconstruct the whole volume
    chunk_size = 100      # this number is determined by available RAM in your computer; 300 is good for a computer with at least 128GB RAM
    margin_slices = 30      # leave this fixed
    zinger = True           # zinger = True: apply zinger removal filtering on the data before tomographic reconstruction
    zinger_level = 500      # You may need to change this is you see some artifacts in reconstructed slice images
    mask = True             # You set 'mask' to be True if you like mask out four corners in the reconsructed slice images
    mask_ratio = 1          # Ratio of the mask's diameter in pixels to slice image width
       
    #center_list = [1290]    # If center_list is set to False (center_list = [False]*len(Exp_idx)), the script 
                                            # will try to find center position automatically. Some time 
                                            # automatic finding center may give wrong results. If you find center 
                                            # values for the list of data sets defined in Exp_idx above, you put 
                                            # these center values here in []. The number of values here in [] must be
                                            # equal to number of items in Exp_idx = [], and orders in these two [] must match.
    use_stripe_removal_fw = 'yes'
    use_stripe_removal_ti = 'no'
    use_stripe_removal_s = 'no'
    use_normalize_bg = 'no'
    use_retrieve_phase = 'yes'


    z = 17                  # sample-detector distance in cm
    eng = 14              # x-ray energy in keV
    pxl = 3.25e-4             # detector pixel size in cm
    rat = 3e-04        # you need to adjust this parameter to balance sharpness and contrast in your reconstructed slice imaoutputges
                            # smaller 'rat make contrast better bu4t in price of sharpness; its typical range is in [1e-4, 1e-2]
############################### user input section -- End ###############################   

    if len(Exp_idx) == 1:  
        data_files,output_files = getFiles(user_top_dir,output_dir,Exp_idx[0])

        output = output_files[0]
        HDF_name = output.split('/')[6]

        if len(data_files) == 0:
            print '!!!!! Error !!!!!'
            print 'There is no given file in the path. Reconstructon is aborted.'
            exit()
        
        dim = dataInfo(data_files[0],showInfor=True)
        if dim == 0:
            print '!!!!! Error !!!!!'
            print 'Cannot read the given data file. Reconstruction is aborted.'
            exit()
    
        if offset == None:
            offset = 0
        if numRecSlices == None:
            numRecSlices = dim[1]
            
        if chunk_size > numRecSlices:
            chunk_size = numRecSlices    
        num_chunk = np.int(numRecSlices/(chunk_size-margin_slices)) + 1
        if numRecSlices == chunk_size:
            num_chunk = 1    
    
        if manualCenter == True:
            data_center_path_now = data_center_path + '/' + HDF_name
            if os.path.exists(os.path.dirname(data_center_path_now+'/')):
                shutil.rmtree(data_center_path_now+'/',True)
            os.makedirs(os.path.dirname(data_center_path_now+'/'))
            print 'Finding center manually'
            loopEngineParams = {'ExplicitParams':
                                                {'sliceStart':sliceStart,
                                                'sliceEnd':sliceEnd,
                                                'zinger':zinger,
                                                'zinger_level':zinger_level,
                                                'data_center_path':data_center_path_now,
                                                'flat_name':flat_name,
                                                'dark_name':dark_name,
                                                'mask':mask,
                                                'mask_ratio':mask_ratio},
                                                
                          'remove_stripe_fwParams':
                                                {'use':use_stripe_removal_fw,
                                                'level':6,
                                                'wname':'db5',
                                                'sigma':1.,
                                                'pad':True},
                                                
                          'retrieve_phaseParams':
                                                {'use':use_retrieve_phase,
                                                'pixel_size':pxl,
                                                'dist':z,
                                                'energy':eng,
                                                'alpha':rat,
                                                'pad':True},
                                                
                          'remove_stripe_tiParams':
                                                {'use':use_stripe_removal_ti,
                                                'nblock':0,
                                                'alpha':5},
                                                
                          'remove_stripe_sfParams':
                                                {'use':use_stripe_removal_s,
                                                'size':31},
                                                
                          'normalize_bgParams':
                                                {'use':use_normalize_bg,
                                                'air':10}                          
                                     }         
            manualFindCenter(data_files[0],data_center_path_now,center_shift,center_shift_w,**loopEngineParams)
        else:
            print 'Reconstructing volume'

            if remove_tree == True:
                if os.path.exists(os.path.dirname(output[:-7])):
                    shutil.rmtree(output[:-7],True)
                    print Exp_idx[0], 'history data has been removed'
            else:
                if os.path.exists(os.path.dirname(output[:-7])):
                    print 'data has been reconsturcted before'
                    quit()

            loopEngineParams = {'ExplicitParams':{'center':center_list[0],
                                                 'zinger':zinger,
                                                 'zinger_level':zinger_level,
                                                 'offset':offset,
                                                 'num_chunk':num_chunk,
                                                 'chunk_size':chunk_size,
                                                 'numRecSlices':numRecSlices,
                                                 'margin_slices':margin_slices,
                                                 'flat_name':flat_name,
                                                 'dark_name':dark_name,
                                                 'mask':mask,
                                                 'mask_ratio':mask_ratio},
                          'remove_stripe_fwParams':{'use':use_stripe_removal_fw,
                                                    'level':6,
                                                    'wname':'db5',
                                                    'sigma':1,
                                                    'pad':True},
                          'retrieve_phaseParams':{'use':use_retrieve_phase,
                                                  'pixel_size':pxl,
                                                  'dist':z,
                                                  'energy':eng,
                                                  'alpha':rat,
                                                  'pad':True},
                          'remove_stripe_tiParams':{'use':use_stripe_removal_ti,
                                                    'nblock':0,
                                                    'alpha':5},
                          'remove_stripe_sfParams':{'use':use_stripe_removal_s,
                                                    'size':31},
                          'normalize_bgParams':{'use':use_normalize_bg,
                                                'air':10}                          
                              }    
                                     
            for ii in range(len(data_files)):     
                loopEngine(data_files[ii],output_files[ii],
                           **loopEngineParams)             

    else:
        for jj in range(len(Exp_idx)):           
            if manualCenter == True:
                data_files,output_files = getFiles(user_top_dir,output_dir,Exp_idx[jj])
                output = output_files[0]
                HDF_name = output.split('/')[6]

                data_center_path_now = data_center_path + '/' + HDF_name
                if os.path.exists(os.path.dirname(data_center_path_now+'/')):
                    shutil.rmtree(data_center_path_now+'/',True)
                os.makedirs(os.path.dirname(data_center_path_now+'/'))

                print 'Finding center manually'
                loopEngineParams = {'ExplicitParams':
                                                    {'sliceStart':sliceStart,
                                                    'sliceEnd':sliceEnd,
                                                    'zinger':zinger,
                                                    'zinger_level':zinger_level,
                                                    'data_center_path':data_center_path_now,
                                                    'flat_name':flat_name,
                                                    'dark_name':dark_name,
                                                    'mask':mask,
                                                    'mask_ratio':mask_ratio},
                                                    
                              'remove_stripe_fwParams':
                                                    {'use':use_stripe_removal_fw,
                                                    'level':6,
                                                    'wname':'db5',
                                                    'sigma':1.,
                                                    'pad':True},
                                                    
                              'retrieve_phaseParams':
                                                    {'use':use_retrieve_phase,
                                                    'pixel_size':pxl,
                                                    'dist':z,
                                                    'energy':eng,
                                                    'alpha':rat,
                                                    'pad':True},
                                                    
                              'remove_stripe_tiParams':
                                                    {'use':use_stripe_removal_ti,
                                                    'nblock':0,
                                                    'alpha':5},
                                                    
                              'remove_stripe_sfParams':
                                                    {'use':use_stripe_removal_s,
                                                    'size':31},
                                                    
                              'normalize_bgParams':
                                                    {'use':use_normalize_bg,
                                                    'air':10}                          
                                         }         
                shutil.rmtree(data_center_path+'/'+HDF_name,True)
                manualFindCenter(data_files[0],data_center_path_now,center_shift,center_shift_w,**loopEngineParams)
                #print '!!!!! Error !!!!!'
                #print 'Finding center manually requires only one data set. Please either change manualCenter to False or provide only one data set.'
                
            else:
                data_files,output_files = getFiles(user_top_dir,output_dir,Exp_idx[jj])
                output = output_files[0]
                HDF_name = output.split('/')[6]
                if remove_tree == True:
                    if os.path.exists(os.path.dirname(output[:-7])):
                        shutil.rmtree(output[:-7],True)
                        print Exp_idx[jj], 'history data has been removed'
                else:
                    if os.path.exists(os.path.dirname(output[:-7])):
                        print Exp_idx[jj],'data has been reconstructed before'
                        continue

                if len(data_files) == 0:
                    print '!!!!! Error !!!!!'
                    print 'There is no given file in the path. Reconstructon is aborted.'
                    exit()
                
                dim = dataInfo(data_files[0],showInfor=True)
                if dim == 0:
                    print '!!!!! Error !!!!!'
                    print 'Cannot read the given data file. Reconstruction is aborted.'
                    exit()
            
                if offset == None:
                    offset = 0
                if numRecSlices == None:
                    numRecSlices = dim[1]
                    
                if chunk_size > numRecSlices:
                    chunk_size = numRecSlices    
                num_chunk = np.int(numRecSlices/(chunk_size-margin_slices)) + 1
                if numRecSlices == chunk_size:
                    num_chunk = 1 
                    
                print 'Reconstructing volume'
                loopEngineParams = {'ExplicitParams':{'center':center_list[jj],
                                                     'zinger':zinger,
                                                     'zinger_level':zinger_level,
                                                     'offset':offset,
                                                     'num_chunk':num_chunk,
                                                     'chunk_size':chunk_size,
                                                     'numRecSlices':numRecSlices,
                                                     'margin_slices':margin_slices,
                                                     'flat_name':flat_name,
                                                     'dark_name':dark_name,
                                                     'mask':mask,
                                                     'mask_ratio':mask_ratio},
                              'remove_stripe_fwParams':{'use':use_stripe_removal_fw,
                                                        'level':6,
                                                        'wname':'db5',
                                                        'sigma':1,
                                                        'pad':True},
                              'retrieve_phaseParams':{'use':use_retrieve_phase,
                                                      'pixel_size':pxl,
                                                      'dist':z,
                                                      'energy':eng,
                                                      'alpha':rat,
                                                      'pad':True},
                              'remove_stripe_tiParams':{'use':use_stripe_removal_ti,
                                                        'nblock':0,
                                                        'alpha':5},
                              'remove_stripe_sfParams':{'use':use_stripe_removal_s,
                                                        'size':31},
                              'normalize_bgParams':{'use':use_normalize_bg,
                                                    'air':10}                          
                                  }    
                                         
                for ii in range(len(data_files)):     
                    loopEngine(data_files[ii],output_files[ii],
                               **loopEngineParams) 














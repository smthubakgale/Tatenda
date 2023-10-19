# I/O 
import sys
#:--- Open CV
import cv2
#:--- Upload 
# DICOM
import pydicom as dicom
import matplotlib.pylab as plt
# NIfTI
import nibabel as nib
# NRRD
import nrrd
import napari
from skimage import data
#:--- Convert
# General > DICOM
import pydicom
import numpy
import pillow
# DICOM > NIfTI
import os
import shutil

import dicom2nifti
# DICOM > NRRDimport sys
import argparse
import slicer

import DICOMLib.DICOMUtils as utils
import DICOMScalarVolumePlugin
# 

if __name__ == '__main__' :
   #  
   a = sys.argv
   n = len(a)
   

   if(n >= 1):
   {
     # 1. Upload 
     if(a[0] == "upload"):
     {
        # 1.1 General  
        if(n == 4 and a[1] == "general"):
        {
          path = a[2]
          title = a[3]

          image = cv2.imread(path , cv2.IMREAD_ANYCOLOR) 

          cv2.imshow(title , image)
        }
        # 1.2 DICOM 
        elif (n ==  3 and a[1] == "dicom"):
        {
          path = a[2]
          
          image = dicom.dcmread(path)

          plt.imshow(image)
        }
        # 1.3 NIfTI
        elif(n == 3 and a[1] == "nifti"):
        {
          path = a[2]
          
          image = nib.load(path)

          plt.imshow(image[96])
          plt.axis('off')
          plt.show()
        }
        # 1.4 NRRD 
        elif(n == 4 and a[1] == "nrrd"):
        {
          path = a[2]
          title = a[3]
          
          readdata, header = nrrd.read(path)

          viewer = napari.Viewer( title = title , 
                                  ndisplay = 3, order = (0, 1, 2) )

          viewer.add_image(  data = readdata, 
                             name = 'blobs' , scale = [256/300, 1, 1] , 
                         colormap = 'gray_trans' , 
                        rendering = 'attenuated_mip' ,
                      attenuation = 2.0 ,
                  contrast_limits =(0.25, 1))
        }
     } 
     # 2. Convert
     elif(a[0] == "convert" && n >= 5):
     {
        # 2.1 General to DICOM
        if(a[1] == "general" and a[2] == "dicom"):
        {
           path = a[3]
           dest = a[4]
           
           image = dicom.dcmread(path)
           dicomwrite(image, dest)
        }
        # 2.2 DICOM to NIFTI 
        if(a[1] == "dicom" and a[2] == "nifti"):
        {
           path = a[3]
           dest = a[4] 
           
           n_path = os.path.basename(path)
           n_dest = os.path.basename(dest)
           
           t_path = os.path.join(os.getcwd(), 'dicom_temp')  # path : temp folder
           f_path = os.path.join(t_path , n_path)            # path : temp file
           
           t_dest = os.path.join(os.getcwd(), 'nifti_temp')  # dest : temp folder 
           f_dest = os.path.join(t_dest , n_dest)            # dest : temp file 
        
           #----------: Path 
           if(os.path.exists(t_path)):                       # directory exist
           {
             shutil.rmtree(t_path, ignore_errors=True) 
             os.makedirs(t_path) 
             
             shutil.copyfile(path, f_path)
           } 
           else:                                             # directory not exist
           { 
             os.makedirs(t_path) 
             
             shutil.copyfile(path, f_path)
           }
           
           #----------: Dest  
           if(os.path.exists(t_dest)):                       # directory exist
           {
             shutil.rmtree(t_dest, ignore_errors=True) 
             os.makedirs(t_dest)  
           } 
           else:                                             # directory not exist
           { 
             os.makedirs(t_dest)  
           }
           #----------: 
           #===: Convert
           dicom2nifti.convert_directory(t_path, t_dest)
           #===:
           shutil.copyfile(f_dest , dest)
           shutil.rmtree(t_path, ignore_errors=True) 
           shutil.rmtree(t_dest, ignore_errors=True) 
           # 
        }
        # 2.3 
        if( a[1] == "dicom" and a[2] == "nrrd"):
        {
           path = a[3]
           dest = a[4] 
           
           n_path = os.path.basename(path)
           n_dest = os.path.basename(dest)
           
           t_path = os.path.join(os.getcwd(), 'dicom_temp')  # path : temp folder
           f_path = os.path.join(t_path , n_path)            # path : temp file
           
           t_dest = os.path.join(os.getcwd(), 'nifti_temp')  # dest : temp folder 
           f_dest = os.path.join(t_dest , n_dest)            # dest : temp file 
        
           #----------: Path 
           if(os.path.exists(t_path)):                       # directory exist
           {
             shutil.rmtree(t_path, ignore_errors=True) 
             os.makedirs(t_path) 
             
             shutil.copyfile(path, f_path)
           } 
           else:                                             # directory not exist
           { 
             os.makedirs(t_path) 
             
             shutil.copyfile(path, f_path)
           }
           
           #----------: Dest  
           if(os.path.exists(t_dest)):                       # directory exist
           {
             shutil.rmtree(t_dest, ignore_errors=True) 
             os.makedirs(t_dest)  
           } 
           else:                                             # directory not exist
           { 
             os.makedirs(t_dest)  
           }
           #----------: 
           #===: Convert  
           with utils.TemporaryDICOMDatabase() as db:
           {
             utils.importDicom(t_path, db)
             
             patient = db.patients()[0]
             study = db.studiesForPatient(patient)[0]
             series = db.seriesForStudy(study)[0]
             files = db.filesForSeries(series)
             reader = DICOMScalarVolumePlugin.DICOMScalarVolumePluginClass()
             loadable = reader.examineForImport([files])[0]
             node = reader.load(loadable)
              slicer.util.saveNode(node, t_dest)
           }
           #===:
           shutil.copyfile(f_dest , dest)
           shutil.rmtree(t_path, ignore_errors=True) 
           shutil.rmtree(t_dest, ignore_errors=True) 
           # 
        }
     }
     # 3. Save
     elif(a[0] == "save" ):
     {
        # 1.1 General  
        if(n == 4 and a[1] == "general"):
        {
          path = a[2]
          dest = a[3]

          image = cv2.imread(path , cv2.IMREAD_ANYCOLOR) 
          cv2.imwrite(dest, image)
        }
        # 1.2 DICOM 
        elif (n == 4 and a[1] == "dicom"):
        {
          path = a[2]
          dest = a[3]
          
          image = dicom.dcmread(path)
          cv2.imwrite(dest, image)
        }
     }
   }
   
 
   # input = input() # input

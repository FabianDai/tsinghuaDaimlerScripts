#!/usr/bin/python
#   ----------------------
#   The Tsinghua-Daimler Cyclist Benchmark
#   ----------------------
#
#
#   License agreement
#-  ----------------
#
#   This dataset is made freely available for non-commercial purposes such as academic research, teaching, scientific publications, or personal experimentation. Permission is granted to use, copy, and distribute the data given that you agree:
#   1. That the dataset comes "AS IS", without express or implied warranty. Although every effort has been made to ensure accuracy, Daimler (or the website host) does not accept any responsibility for errors or omissions.
#   2. That you include a reference to the above publication in any published work that makes use of the dataset.
#   3. That if you have altered the content of the dataset or created derivative work, prominent notices are made so that any recipients know that they are not receiving the original data.
#   4. That you may not use or distribute the dataset or any derivative work for commercial purposes as, for example, licensing or selling the data, or using the data with a purpose to procure a commercial gain.
#   5. That this original license notice is retained with all copies or derivatives of the dataset.
#   6. That all rights not expressly granted to you are reserved by Daimler. 
#
#   Contact
#   -------
#
#   Fabian Flohr
#   mail: tdcb at fabian-flohr.de


tar -C "$PWD" -cvf tdcb_camera_train.tar.gz camera/train
tar -C "$PWD" -cvf tdcb_camera_test.tar.gz camera/test
tar -C "$PWD" -cvf tdcb_camera_valid.tar.gz camera/valid
tar -C "$PWD" -cvf tdcb_camera_NonVRU.tar.gz camera/NonVRU

tar -C "$PWD" -cvf tdcb_leftImg8bit_train.tar.gz leftImg8bit/train
tar -C "$PWD" -cvf tdcb_leftImg8bit_test.tar.gz leftImg8bit/test
tar -C "$PWD" -cvf tdcb_leftImg8bit_valid.tar.gz leftImg8bit/valid
tar -C "$PWD" -cvf tdcb_leftImg8bit_NonVRU.tar.gz leftImg8bit/NonVRU

tar -C "$PWD" -cvf tdcb_disparity_train.tar.gz disparity/train
tar -C "$PWD" -cvf tdcb_disparity_test.tar.gz disparity/test
tar -C "$PWD" -cvf tdcb_disparity_valid.tar.gz disparity/valid
tar -C "$PWD" -cvf tdcb_disparity_NonVRU.tar.gz disparity/NonVRU

tar -C "$PWD" -cvf tdcb_labelData_train.tar.gz labelData/train
tar -C "$PWD" -cvf tdcb_labelData_test.tar.gz labelData/test
tar -C "$PWD" -cvf tdcb_labelData_valid.tar.gz labelData/valid
tar -C "$PWD" -cvf tdcb_labelData_NonVRU.tar.gz labelData/NonVRU

tar -C "$PWD" -cvf tdcb_scripts.tar.gz scripts





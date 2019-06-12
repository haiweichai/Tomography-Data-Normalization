%  This code is used to organize SSRF data into HDF5 files
%  Then batch processing is possible, based on TomoPy [1].
%  
%  Created on Tue Jun 11 12:23:05 2019
%  Author : hwchai_PIMS
%  
%  [1] Gursoy, Doga, et al. "TomoPy: a framework for the analysis of 
%  synchrotron tomographic data." Journal of synchrotron radiation 21.5 
%  (2014): 1188-1193.

filedir = 'F:\SSRFdata_201806';
output = 'F:\code\';

proj_name = 'tomo_';
flat_name = 'flat_';
dark_name = 'dark_';

remove_tree = 1;  % set to 1 if you want to remove old version data.
% ------------------------------------------------------------------------
dirOutput=dir(fullfile(filedir,'Exp*'));  data_num = size(dirOutput,1);

for num_ = 1:data_num,

filedir2 = [filedir,'\',dirOutput(num_).name,'\'];
projlist = dir(fullfile(filedir2,[proj_name,'*.tif']));
flatlist = dir(fullfile(filedir2,[flat_name,'*.tif']));
darklist = dir(fullfile(filedir2,[dark_name,'*.tif']));

timemachine = tic; for i = 1:size(projlist,1), 
	[X,map] = imread([filedir2,projlist(i).name],'tif');
	proj(:,:,i) = X; end, proj = permute(proj,[2,1,3]); % Permute array dimensions   Z_X_THETA to X_Z_THETA
disp(['imread proj stacks time: ',num2str(toc(timemachine))]);

timemachine = tic; for i = 1:size(flatlist,1), 
	[X,map] = imread([filedir2,flatlist(i).name],'tif');
	flat(:,:,i) = X; end, flat = permute(flat,[2,1,3]);
disp(['imread flat stacks time: ',num2str(toc(timemachine))]);

timemachine = tic; for i = 1:size(darklist,1), 
	[X,map] = imread([filedir2,darklist(i).name],'tif');
	dark(:,:,i) = X; end, dark = permute(dark,[2,1,3]);
disp(['imread dark stacks time: ',num2str(toc(timemachine))]);

data_type = class(proj);  % datatype  uint8  uint12  uint16  single  double

timemachine = tic; 
if exist(dirOutput(num_).name,'file') & remove_tree == 1, 
	disp([dirOutput(num_).name(1:6),' has been removed.']); 
	delete(dirOutput(num_).name);
elseif exist(dirOutput(num_).name,'file') & remove_tree == 0,
	disp([dirOutput(num_).name(1:6),' have been in existence.']); continue; end

h5create([dirOutput(num_).name,'.h5'],'/exchange/data'      ,size(proj),'Datatype',data_type);
h5create([dirOutput(num_).name,'.h5'],'/exchange/data_white',size(flat),'Datatype',data_type);
h5create([dirOutput(num_).name,'.h5'],'/exchange/data_dark' ,size(dark),'Datatype',data_type);
% 'Deflate'  0-9  gzip compress level     'Chunksize',[2048 2048 1],'Deflate',9

disp(['creat HDF5 file time: ',num2str(toc(timemachine))]);

timemachine = tic; 
h5write([dirOutput(num_).name,'.h5'],'/exchange/data'      ,proj);
h5write([dirOutput(num_).name,'.h5'],'/exchange/data_white',flat);
h5write([dirOutput(num_).name,'.h5'],'/exchange/data_dark' ,dark);
disp(['write stacks time: ',num2str(toc(timemachine))]);

clear proj flat dark projlist flatlist darklist X map i filedir2 data_type timemachine;

disp([dirOutput(num_).name(1:6),' has been transformed to HDF5.']);

end

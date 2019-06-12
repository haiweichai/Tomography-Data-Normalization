# Tomography-Data-Normalization

### 规范数据存储

团队已在多个同步辐射装置 (APS, SSRF, BSRF) 上进行同轴相衬CT实验，累积海量图像数据。各次实验数据存储规则各不相同，reconstruction程序及环境五花八门，不利于高效处理及分析，在此将现有全部CT原始数据统一至2019年04月2BM存储规范：

1. > 采用`HDF5`规范封装单组CT扫描图像集，包括投影图、白背底、暗背底，文件后缀(`.h5`)

2. > 各次实验采集数据独立编号，命名规则形如 `Exp020_*.h5`

3. > 投影图保存至`*.h5/exchange/data`，维度顺序为`[Theta,Z,X]`

4. > 白背底保存至`*.h5/exchange/data_white`，维度顺序为`[Num,Z,X]`

5. > 暗背底保存至`*.h5/exchange/data_dark`，维度顺序为`[Num,Z,X]`

6. > datatype `uint16`,`uint12`,`uin8`; `chunksize`选择默认; `Deflate`选择0

`SSRFdata_normalization.m` 可将上海光源数据按如上规范整理归纳。 `APSdata_normalization.m` 将APS数据整理归纳。统一归纳后，可利用`reconstruction.py` 对现有全部CT数据进行三维重建分析。

### 其他

1. > 实验参数记录 ：在各次实验存储路径下创建参数记录文本`log.txt`，记录内容按如下顺序：Exp001 Energy(keV) Pixel_size(mm) SSD(cm) Axes_center rat(delta/beta)

2. > 原位实验 ：实时采集的应力应变信息存储在各次实验存储路径下 `MTS_data\` 目录内

3. > 分析量化 ：分析结果整理为ppt存储在各次实验存储路径下

4. > 读写权限 ：仅在需要将新采集数据写入存储位置时开放写入权限，其他时期关闭写入、删改权限，避免数据丢失

### 后续改进

适用于CT图像的无损压缩技术

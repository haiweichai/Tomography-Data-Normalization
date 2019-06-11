# Tomography-Data-Normalization

### 规范数据存储

团队已在多个同步辐射装置 (APS, SSRF, BSRF) 上进行同轴相衬CT实验，累积海量图像数据。考虑到各次实验数据存储规则各不相同，reconstruction程序及环境五花八门，不利于高效处理及分析。在此将现有全部CT原始数据统一至2019年04月2BM数据存储的规范：

1. > 采用`HDF5`规范封装单组CT扫描图像集，包括投影图、白背底、暗背底，文件后缀(`.h5`)

2. > 各次实验采集数据独立编号，命名规则形如 `Exp020_*.h5`

3. > 投影图保存至`*.h5/exchange/data`，维度顺序为`[Theta,Z,X]`

4. > 白背底保存至`*.h5/exchange/data_white`，维度顺序为`[Num,Z,X]`

5. > 暗背底保存至`*.h5/exchange/data_dark`，维度顺序为`[Num,Z,X]`

6. > datatype 保持原状，2BM实验2018年04月前、BL13W1实验均为`uint16`，BL09U实验均为`uint12`，2BM_201904为`uin8`

7. > `chunksize`选择默认，`Deflate`选择0

### 后续改进计划

专用于CT原始图像的高压缩比无损压缩技术。

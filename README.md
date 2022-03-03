# ReadMe

File usage - python3 copyFiles.py <src_File> <dest_Folder>

**Assumptions**:

The Network shared locations are mounted and a symlink exists. 

**Limitations:**

If a destination file is mentioned, please make sure that file exists. If not provide a destinaion folder, and the src fileis copied to the destination folder with the same name

Only supports copying one file, recursive copy is not supported yet

**Requirements:**

Current implementation is done in python3. I have used threading library to optimize for slow writes.

Although,threading overheads are taken into consideration and threading is used only when network shared folder is used. This can be further optimized based on actual chunk write times.

Due to lack of testing capabilities for Network shared folders, I couldnt optimize it further. 

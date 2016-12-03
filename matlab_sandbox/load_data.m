function [IMGS, GT] = load_data(folder_path)

D           = dir([folder_path '*.png']);
IMGS        = cell(1, length(D));

idx_image   = 1;
for file = D'
    IMGS{idx_image} = imread([folder_path file.name]);    
    idx_image       = idx_image + 1;
end

GT = [];
if exist([folder_path 'result.csv']) == 2
    fid = fopen([folder_path 'result.csv']);
    fgetl(fid);
    GT = fscanf(fid, '"(%d, %d)","(%d, %d)",%f');
    fclose(fid);
end
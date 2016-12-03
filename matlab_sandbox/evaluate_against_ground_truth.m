function [ Q ] = evaluate_against_ground_truth( folder_path_to_ground_truth )
Q = [];

folders_days = get_folder_names(folder_path_to_ground_truth); 

for i = 1 : length(folders_days)
    folders_waggles = get_folder_names([folder_path_to_ground_truth '/' folders_days{i}]); 
    for j = 1 : length(folders_waggles)
        [IMGS, GT] = load_data([folder_path_to_ground_truth '/' folders_days{i} '/' folders_waggles{j} '/']);
        a = extract_waggle_angle_fourier(IMGS);
        Q = [Q; GT(5) a];
%         d = angDiff(GT(5), a, 180);
        fprintf('.')
        str = sprintf('gt:%.1f, out: %.1f, error: %.1f', GT(5), a, angDiff(GT(5), a, 180) ); 
        title(str)
        [folders_days{i} '/' folders_waggles{j}]
        pause
    end
end

dA = angDiff(Q(:,1), Q(:,2), 180);

dA(dA>90) = dA(dA>90) - 180;
dA(dA<-90) = dA(dA<-90) + 180;
hist(dA, 30)
mean(dA)
std(dA)

function folders = get_folder_names(root_path)
D           = dir(root_path);
isdir       = [D(:).isdir];
folders     = {D(isdir).name}';
folders(ismember(folders,{'.','..'})) = [];
